#Imports
import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests

#Target URL
endpoint_url = "https://api.ebay.com/sell/fulfillment/v1/order"

#Assign Global Variables
app_id=os.getenv("EBAY_APP_ID")
cert_id=os.getenv("EBAY_CERT_ID")

#Refresh The Token
def refresh_access_token():
    target_url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = (app_id, cert_id)
    payload = {"grant_type": "refresh_token", "refresh_token": os.getenv("EBAY_REFRESH_TOKEN")}
    response = requests.post(target_url, headers=headers, data=payload, auth=auth)
    new_token_data = response.json()
    return new_token_data.get("access_token")

#Link the New Refresh Token
fresh_token = refresh_access_token()

#Fetch Function
def fetch_ebay_data():
    headers = {"Authorization": f"Bearer {fresh_token}"}
    response = requests.get(endpoint_url, headers=headers)
    print(response.json())

#Run Function
fetch_ebay_data()