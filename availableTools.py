import requests
import json
from langfuse.decorators import observe
import os
from dotenv import load_dotenv
load_dotenv()

class IndoJuniTool:
    def __init__(self):
        self.base_url = os.environ['base_url']
        self.access_token = self._login()['data']['access_token']

    # Login
    def _login(self):
        request_headers = {
            "Accept": "application/json"
        }
        request_body = {
            "email": os.environ['email'],
            "password": os.environ['password']
        }
        url = f"{self.base_url}/api/v1/auth/login"
        response = requests.post(url, json=request_body, headers=request_headers)
        return response.json()

    # Get product list
    @observe(name="Get product list")
    def getProductList(self):
        url = f"{self.base_url}/api/v1/product/all"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=request_headers)
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
    def getCurrentCart(self):
        url = f"{self.base_url}/api/v1/cart/current"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=request_headers)
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
    def addProduct(self, products: list):
        url = f"{self.base_url}/api/v1/cart/add"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        request_body = {
            "product": products
        }
        response = requests.post(url, headers=request_headers, json=request_body)
        response = response.json()
        function_output = {
            "tool_call_id":"2",
            "content":{
                "function_name":"addProduct",
                "content": response['data'],
            }
        }
        return function_output

    # Function to modify product in cart
    @observe(name="Modify product in cart")
    def modifyCart(self, products: list):
        url = f"{self.base_url}/api/v1/cart/modify"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        request_body = {
            "product":products,
        }
        response = requests.post(url,headers=request_headers,json=request_body)
        response = response.json()

        function_output = {
            "tool_call_id":"4",
            "content":{
                "function_name":"modifyProduct",
                "content": response['data'],
            }
        }
        return function_output

    # Function to checkout cart
    @observe(name="Checkout cart")
    def checkoutCart(self, personal_info: dict):
        url = f"{self.base_url}/api/v1/checkout"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.post(url,headers=request_headers,json=personal_info)
        response = response.json()
        function_output = {
            "tool_call_id":"5",
            "content":{
                "function_name":"checkoutCart",
                "content": response['data'],
            }
        }
        return function_output

    # Ignore this function for now (only used for testing purpose and won't be used for production)
    @observe(name="User greetings")
    def greetings(self):
        function_output = {
            "tool_call_id":"5",
            "content":{
                "function_name":"greetings",
                "content": "Welcome to IndoJuni! How can I assist you today?",
            }
        }
        return function_output
    
    # @observe(name="Show invoice")
    # def showInvoice(self):
    #     url = f"{self.base_url}/api/v1/cart/modify"
    #     headers = {
    #         "Authorization": f"Bearer {self.access_token}"
    #     }
    #     request_body = {
    #         "product":products,
    #     }
    #     response = requests.post(url,headers=headers,json=request_body)
    #     response = response.json()
    #     function_output = {
    #         "tool_call_id":"6",
    #         "content":{
    #             "function_name":"showInvoice",
    #             "content": "You can view your invoice at: https://indojuni.com/invoice (This is a placeholder link)",
    #         }
    #     }
    #     return function_output

    # Function executor
    def function_extractor(response):
        start_index = response.content.find('[')
        end_index = response.content.rfind(']') + 1
        extracted_string = response.content[start_index:end_index]

        parsed_tools = json.loads(extracted_string)
        return parsed_tools