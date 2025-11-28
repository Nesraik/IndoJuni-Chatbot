from availableTools import IndoJuniTool
from langfuse import Langfuse, observe
from langfuse.openai import OpenAI
import json
from Utils.jinjaProcessor import *
import requests
from dotenv import load_dotenv
load_dotenv(override=True)
langfuse = Langfuse()

class Chatbot(IndoJuniTool):
    def __init__(self, access_token: str = None):
        super().__init__(access_token=access_token)
        self.tools = json.loads(process_template_no_var('Prompt/tools_template.jinja'))
        self.functions = {
            "getCurrentCart": self.getCurrentCart,
            "addProduct": self.addProduct,
            "modifyCart": self.modifyCart,
            "searchProductList": self.searchProductList,
            "showInvoice": self.showInvoice,
            "checkoutCart": self.checkoutCart
        }
        self.client = OpenAI(
            base_url=os.environ.get("CHATBOT_BASE_URL"),
            api_key= os.environ.get("CHATBOT_API_KEY")
        )

    @observe()
    def _generate_response(self,messages):
        response = self.client.chat.completions.create(
            model = os.environ.get("CHATBOT_MODEL"),
            messages = messages,
            tools= self.tools,
            temperature=0.1,
            top_p=0.1,
        )

        return response.choices[0].message

    def generate_single_chat_message(self,user_prompt,messages,flag):

        system_prompt = process_template_no_var('Prompt/system_prompt.jinja')

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
                "content": response.content,
                "tool_calls": response.tool_calls if response.tool_calls is not None else []
            })

            if response.tool_calls is None:
                break
            
            for tool in response.tool_calls:

                if tool is None:
                    continue

                # Check for function name
                try:
                    function_name = self.functions[tool.function.name]
                except:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": "N/A",
                        "content": "Function not found in tools_dict"
                    })

                    continue

                function_args = json.loads(tool.function.arguments)

                # Check for function arguments
                try:    
                    function_output = function_name(**function_args)
                    content = json.dumps(function_output, indent=4)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool.id,
                        "name": tool.function.name,
                        "content": content
                    })

                except Exception as e:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool.id,
                        "name": tool.function.name,
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