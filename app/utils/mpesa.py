# app/utils/mpesa.py
import requests
import base64
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class MpesaClient:
    def __init__(self):
        self.consumer_key = os.getenv('CONSUMER_KEY')
        self.consumer_secret = os.getenv('CONSUMER_SECRET')
        self.shortcode = os.getenv('SHORTCODE', '174379')
        self.passkey = os.getenv('PASSKEY')
        self.callback_url = os.getenv('CALLBACK_URL')
        self.base_url = os.getenv('BASE_URL', 'https://sandbox.safaricom.co.ke')
        self.environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
        
        # Test phone number for sandbox
        self.test_phone = '254708374149'
    
    def get_access_token(self):
        """Get OAuth access token from Safaricom"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def stk_push(self, phone_number, amount, account_reference="LOAN", transaction_desc="Payment"):
        """
        Initiate STK Push payment
        phone_number: Format 2547XXXXXXXX (no leading 0)
        amount: Amount to charge
        """
        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        # ⭐ SANDBOX MAPPING LOGIC - Maps any number to test number
        if self.environment == 'sandbox':
            phone_number = self.test_phone
            print(f"🔧 Sandbox mode: Using test number {phone_number}")
        
        # Get access token
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        
        # Prepare request
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error initiating STK Push: {e}")
            return {'error': str(e)}
    
    def check_payment_status(self, checkout_request_id):
        """Check status of a payment"""
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking payment status: {e}")
            return {'error': str(e)}