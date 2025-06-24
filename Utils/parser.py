import json
import re

def parse_function(text,bfcl_format = False):
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

def extract_json_dict(text):
    """
    Extracts and parses the JSON dictionary from the input text.

    Args:
        text (str): The input text containing a JSON object inside {}.

    Returns:
        dict: The parsed JSON dictionary.

    Raises:
        ValueError: If no valid JSON object is found or if parsing fails.
    """
    # Use regex to find the JSON object enclosed in {}
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        print("No match found in the text.")
        return None

    # Extract the JSON string
    json_str = match.group(0)

    json_str = re.sub(r"\\'", "'", json_str)

    try:
        # Parse the JSON string into a Python dictionary
        json_dict = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None

    return json_dict

# Read data
def readJSONLines(filename):
    json_dict_list = []
    with open(filename, "r") as f:
        for line in f.readlines():
            
            json_dict = extract_json_dict(line)
            json_dict_list.append(json_dict)

    product_list = []

    for json_dict in json_dict_list:
        product = json.dumps(json_dict, ensure_ascii=False)
        product_list.append(product)

    return product_list