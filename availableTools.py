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
        print(url)
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
        print(url)
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=request_headers)
        response = response.json()
        function_output = {
            "content":{
                "function_name":"getCurrentCart",
                "content": response['data']['cart_items'],
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
        return response['data']

    # Function to checkout cart
    @observe(name="Checkout cart")
    def checkoutCart(
        self,
        firstname: str,
        lastname: str,
        address: str,
        zip: str,
        payment_method: str,
        card_name: str,
        card_number: str,
        card_expiration: str,
        card_cvv: str,
        address2: str = None,
        email: str = None,
    ):
        url = f"{self.base_url}/api/v1/checkout"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        personal_info = {
            "firstname": firstname,
            "lastname": lastname,
            "address": address,
            "address2": address2,
            "zip": zip,
            "email": email,
            "payment_method": payment_method,
            "card_name": card_name,
            "card_number": card_number,
            "card_expiration": card_expiration,
            "card_cvv": card_cvv,
        }
        response = requests.post(url,headers=request_headers,json=personal_info)
        response = response.json()
        function_output = {
            "content":{
                "function_name":"checkoutCart",
                "content": response['data'],
            }
        }
        return function_output
    
    @observe(name="Checkout cart")
    def checkoutCart(
        self
    ):
        url = f"{self.base_url}/api/v1/checkout"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        personal_info = self._getBillingAddress()
        if personal_info is not None:
            response = requests.post(url,headers=request_headers,json=personal_info)
            response = response.json()
            function_output = {
                "content":{
                    "function_name":"checkoutCart",
                    "content": response['data'],
                }
            }
        else:
            function_output = {
                "content":{
                    "function_name":"checkoutCart",
                    "content": "Error: Billing address not found. Please set your billing address in the profile page before checkout.",
                }
            }
        return function_output
    
    @observe(name="Show invoice")
    def showInvoice(self):
        url = f"{self.base_url}/api/v1/invoice"
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        response = requests.post(url,headers=request_headers)
        response = response.json()
        function_output = {
            "content":{
                "function_name":"showInvoice",
                "content": response['data'],
            }
        }
        return function_output
