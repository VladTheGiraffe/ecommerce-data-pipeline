#Imports
import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests


#Target URLs
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


#Fetch Finances Function
def fetch_finance_data(access_token):
    target_url = "https://api.ebay.com/sell/finances/v1/transaction"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(target_url, headers=headers)
    raw_data = response.json()
    shipping_map = {}
    transactions_list = raw_data.get("transactions", [])
    for txn in transactions_list:
        if txn.get("transactionType") == "SHIPPING_LABEL":
            order_id = txn.get("orderId")
            label_cost = txn.get("amount", {}).get("value")
            shipping_map[order_id] = label_cost
            return shipping_map
    

#Fetch Order Function
def fetch_ebay_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint_url, headers=headers)
    raw_data = response.json()
    order_list = raw_data.get("orders", [])
    
    for order in order_list:
        sku = order.get("lineItems", [])[0].get("sku")
        clean_orders = []
        if sku is None:
            continue
        sku = "VTG" + sku[3:].zfill(4)
        sale_price = float(order.get("lineItems", [])[0].get("value", "0.00"))
        shipping_charged = float(order.get("lineItems", [])[0].get("deliveryCost", {}).get("shippingCost", {}).get("value", "0.00"))
        ebay_fees = float(order.get("totalMarketplaceFee", {}).get("value", "0.00"))
        shipping_cost = 0.00
        date_sold = order.get("creationDate")[:10]
        order_data = {
            "sku": sku,
            "sale_price": sale_price,
            "shipping_charged": shipping_charged,
            "ebay_fees": ebay_fees,
            "shipping_cost": None,
            "date_sold": date_sold
        }
        clean_orders.append(order_data)
        return clean_orders
        

        print(f"SKU: {sku} | Sold For: ${sale_price:.2f} | Shipping Collected: ${shipping_charged:.2f} | Ebay Fees: ${ebay_fees:.2f} | Shipping Paid: ${shipping_cost:.2f} | Date Sold: {date_sold}")

#Execution Block
fresh_token = refresh_access_token()
finance_payload = fetch_finance_data(fresh_token)
fulfillment_payload = fetch_ebay_data(fresh_token)