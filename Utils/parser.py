import json
import re

def parse_function(text,bfcl_format):
    if text.find('<function>') != -1:
        start_index = text.find('<function>')
        start_index += len('<function>')
    else:
        start_index = text.find('<Function call>')
        start_index += len('<Function call>')

    if text.find('</function>') != -1:
        end_index = text.find('</function>')
    else:
        end_index = text.find('<End of function call>')
    
    function_text = text[start_index:end_index].strip()
    function_text = re.sub(r'\(([^()]+)\)', r'[\1]', function_text)

    parsed_tools = json.loads(function_text)

    if bfcl_format == True:
        func_dicts = []
        for tool in parsed_tools:
            tool_dict = {
                tool['name']: tool['parameters']
            }
            func_dicts.append(tool_dict)
        return func_dicts

    return parsed_tools

