import requests
import json
from langfuse.decorators import observe
import os

base_url = os.environ['base_url']

# Login
def login():
    request_body = {
        "email": os.environ['email'],
        "password": os.environ['password']
    }
    url = f"{base_url}/api/v1/auth/login"
    response = requests.post(url, json=request_body)
    return response.json()

response = login()
access_token = response['data']['access_token']

# Get product list
@observe(name="Get product list")
def getProductList():
    url = f"{base_url}/api/v1/product/all"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    response = response.json()
    function_output = {
        "tool_call_id":"0",
        "content":{
            "function_name":"getProductList",
            "content": response['data'],
        }
    }
    return function_output

# Get current cart
@observe(name="Get product in cart")
def getCurrentCart():
    url = f"{base_url}/api/v1/cart/current"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    response = response.json()
    function_output = {
        "tool_call_id":"1",
        "content":{
            "function_name":"getCurrentCart",
            "content": response['data']['cartItems'],
        }
    }
    return function_output

# Add product
@observe(name="Add product to cart")
def addProduct(products: list):
    url = f"{base_url}/api/v1/cart/add"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    request_body = {
        "product": products
    }
    response = requests.post(url, headers=headers, json=request_body)
    response = response.json()
    function_output = {
        "tool_call_id":"2",
        "content":{
            "function_name":"addProduct",
            "content": response['message'],
        }
    }
    return function_output

# Remove product
@observe(name="Remove product from cart")
def removeProduct(product_ids: list):
    url = f"{base_url}/api/v1/cart/remove"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    request_body = {
        "product_id": product_ids
    }
    response = requests.post(url, headers=headers, json=request_body)
    response = response.json()
    function_output = {
        "tool_call_id":"3",
        "content":{
            "function_name":"removeProduct",
            "content": response['message'],
        }
    }
    return function_output

# Function to modify product in cart
@observe(name="Modify product in cart")
def modifyCart(products: list):
    url = f"{base_url}/api/v1/cart/modify"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    request_body = {
        "product":products,
    }
    response = requests.post(url,headers=headers,json=request_body)
    response = response.json()

    function_output = {
        "tool_call_id":"4",
        "content":{
            "function_name":"modifyProduct",
            "content": response['message'],
        }
    }
    return function_output

# Placeholder function for user greetings
def greetings():
    function_output = {
        "tool_call_id":"5",
        "content":{
            "function_name":"greetings",
            "content": "Welcome to IndoJuni! How can I assist you today?",
        }
    }
    return function_output

# Function executor
def function_extractor(response):
    start_index = response.content.find('[')
    end_index = response.content.rfind(']') + 1
    extracted_string = response.content[start_index:end_index]

    parsed_tools = json.loads(extracted_string)
    return parsed_tools
