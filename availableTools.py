import requests
import json
from langfuse import observe
import os
from dotenv import load_dotenv
load_dotenv(override=True)

class IndoJuniTool:
    def __init__(self, access_token: str = None):
        self.base_url = os.environ['base_url']
        self.access_token = access_token

    # Get product list
    @observe(name="Search product list")
    def searchProductList(self, query: dict):
        url = f"{self.base_url}/api/v1/product/all"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=request_headers, params=query)
        response = response.json()
        function_output = {
            "content":{
                "function_name":"searchProductList",
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

        try:
            items = response['data']['cart_items']
        except:
            items = []
            
        function_output = {
            "content":{
                "function_name":"getCurrentCart",
                "content": items,
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
            "content":{
                "function_name":"modifyProduct",
                "content": response['data'],
            }
        }
        return function_output
    
    def _getBillingAddress(self):
        url = f"{self.base_url}/api/v1/auth/user"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=request_headers)
        response = response.json()
        return response['data']['default_payment_detail']

    @observe(name="Checkout cart")
    def checkoutCart(
        self
    ):
        url = f"{self.base_url}/api/v1/checkout"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        
        # Check if cart is empty
        if self.getCurrentCart()['content']['content'] == []:
            return {
                "content":{
                    "function_name":"checkoutCart",
                    "content": "Your cart is empty. Please add products to your cart before checking out.",
                }
            }
        
        personal_info = self._getBillingAddress()
        if personal_info is not None:
            response = requests.post(url,headers=request_headers,json=personal_info)
            response = response.json()
            if response['status'] != 200:
                return {
                    "content":{
                        "function_name":"checkoutCart",
                        "content": response['message'],
                    }
                }
            else:
                function_output = {
                    "content":{
                        "function_name":"checkoutCart",
                        "content": f"Checkout Success!. You can see your invoice in this url https://indojuni.cafaku.dev/invoice/{response['data']['id']}!.",
                    }
                }
        else:
            function_output = {
                "content":{
                    "function_name":"checkoutCart",
                    "content": f"Tell user to fill their personal detail on this url https://indojuni.cafaku.dev/profile . Tell them to comeback after filling the detail.",
                }
            }
        return function_output
    
