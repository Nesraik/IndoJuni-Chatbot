from availableTools import IndoJuniTool
from langfuse import Langfuse
from langfuse.openai import OpenAI
from langfuse.decorators import observe
import json
from Utils.jinjaProcessor import *
from Utils.parser import *
from rag import *
import requests
from dotenv import load_dotenv
load_dotenv(override=True)
langfuse = Langfuse()

class Chatbot(IndoJuniTool):
    def __init__(self):
        super().__init__()
        self.api_keys = []
        self.current_index = 0
        self._insert_api_key()
        self.tools_prompt = process_template_no_var('Prompt/tools_template.jinja')
        self.functions = {
            "getCurrentCart": self.getCurrentCart,
            "addProduct": self.addProduct,
            "modifyCart": self.modifyCart,
            "getProductDetails": self.getProductDetails,
            "showInvoice": self.showInvoice,
        }
        self.Retriever = ContextRetriever()

    def _insert_api_key(self):
        with open("llm_api_keys.txt") as f:
            for line in f.readlines():
                self.api_keys.append(line.strip())

    def _get_client(self):
        return OpenAI(
            base_url=os.environ.get("CHATBOT_BASE_URL"),
            api_key= self.api_keys[self.current_index]
        )
    
    @observe()
    def _generate_response(self,messages):
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model = os.environ.get("CHATBOT_MODEL"),
                messages = messages,
                temperature=0.1,
                top_p=0.1,
                presence_penalty=0.0,
                frequency_penalty=0.0,
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                self.current_index = (self.current_index + 1) % len(self.api_keys)
                client = self._get_client()
                response = client.chat.completions.create(
                    model = "llama-3.3-70b-versatile",
                    messages = messages,
                    temperature=0.1,
                    top_p=0.1,
                    presence_penalty=0.0,
                    frequency_penalty=0.0,
                )
        return response.choices[0].message.content

    def generate_single_chat_message(self,user_prompt,messages,flag):

        context = self.Retriever.retrieveContext(user_message=user_prompt,chat_history=messages)

        temp = {
            "tools": self.tools_prompt,
            "context": context
        }

        system_prompt = process_template('Prompt/system_prompt.jinja', temp)

        if flag == False:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
            flag = True
        else:
            messages.append({
                "role": "user",
                "content": user_prompt
            })
            messages[0]['content'] = system_prompt

        while True:
            response = self._generate_response(messages)
            messages.append({
                "role": "assistant",
                "content": response
            })

            
            tools = parse_function(response,bfcl_format=False)

            if len(tools) == 1 and (tools[0]['function_name'] == 'FUNCTION_NOT_FOUND' or tools[0]['function_name'] == 'NONE'):
                break
            
            
            for tool in tools:

                if tool['function_name'] == 'FUNCTION_NOT_FOUND' or tool['function_name'] == 'NONE':
                    continue

                # Check for function name
                try:
                    function_name = self.functions[tool['function_name']]
                except:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": "N/A",
                        "content": "Function not found in tools_dict"
                    })

                    continue

                try:
                    function_args = tool['args']
                except:
                    function_args = tool['parameters']

                if "<MISSING>" in function_args.values():
                    return messages, flag

                # Check for function arguments
                try:    
                    function_output = function_name(**function_args)
                    content = json.dumps(function_output, indent=4)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": function_output['tool_call_id'],
                        "content": content
                    })

                except Exception as e:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": "N/A",
                        "content": f"Error: {str(e)} calling {function_name.__name__} with args {function_args}"
                    })

        return messages, flag
    
    def run_conversation(self):
        messages = []
        flag = False

        count = 0
        while True:
            
            # Delete this for production
            tester_message = input("Tester Message: ")
            if tester_message.strip().lower() == 'exit':
                print("Exiting the chatbot.")
                break
                
            messages, flag = self.generate_single_chat_message(tester_message, messages,flag)

            count += 1
