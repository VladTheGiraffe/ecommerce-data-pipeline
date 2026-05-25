import os
from dotenv import load_dotenv
load_dotenv()
import requests
import urllib.parse

target_url = "https://api.ebay.com/identity/v1/oauth2/token"
app_id=os.getenv("EBAY_APP_ID")
cert_id=os.getenv("EBAY_CERT_ID")
headers = {"Content-Type": "application/x-www-form-urlencoded"}
payload = {"grant_type": "authorization_code", "code": urllib.parse.unquote("v%5E1.1%23i%5E1%23I%5E3%23p%5E3%23r%5E1%23f%5E0%23t%5EUl41XzEwOjNDQkM5MDFENjlBNzg5QjBEM0FGNTI2OEU0QjcwQkEyXzJfMSNFXjI2MA%3D%3D&expires_in=299"), "redirect_uri": "https://example.com"}
response = requests.post(target_url, headers=headers, data=payload, auth=(app_id, cert_id))

print(response.json())