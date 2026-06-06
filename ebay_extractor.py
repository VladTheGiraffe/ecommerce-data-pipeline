#Imports
import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests
import psycopg
from datetime import datetime, timedelta


#Target URLs
endpoint_url = "https://api.ebay.com/sell/fulfillment/v1/order"


#Assign Global Variables
app_id=os.getenv("EBAY_APP_ID")
cert_id=os.getenv("EBAY_CERT_ID")
DB_URI=os.getenv("DB_CONNECTION_STRING")


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
    target_url = "https://apiz.ebay.com/sell/finances/v1/transaction"
    headers = {"Authorization": f"Bearer {access_token}"}
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    end_date = now.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    start_time = thirty_days_ago.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    params = {
        "filter": f"transactionDate:[{start_time}..{end_date}]",
        "limit": "100"
    }
    response = requests.get(target_url, headers=headers, params=params)
    print(f"API REQUEST: {response.status_code}")
    print(response.text)
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
    
    clean_orders = []
    print(f"DEBUG: Raw Orders Received from API: {len(order_list)}")
    for order in order_list:
        order_id = order.get("orderId")
        date_sold = order.get("creationDate")[:10]
        ebay_fees = float(order.get("totalMarketplaceFee", {}).get("value", 0.00))
        shipping_cost = 0.00
        for item in order.get("lineItems", []):
            sku = item.get("sku")
            if sku is None:
                continue
            sku = "VTG" + sku[3:].zfill(4)
            sale_price = float(item.get("lineItemCost", {}).get("value", "0.00"))
            shipping_charged = float(item.get("deliveryCost", {}).get("shippingCost", {}).get("value", "0.00"))

            order_data = {
                "sku": sku,
                "sale_price": sale_price,
                "shipping_charged": shipping_charged,
                "ebay_fees": ebay_fees,
                "shipping_cost": None,
                "date_sold": date_sold,
                "order_id": order_id
            }
            clean_orders.append(order_data)
    print((f"Debug: Clean items successfully packaged: {len(clean_orders)}"))
    print(f"DEBUG first item: {clean_orders[0]}")
    return clean_orders
        
#Import to Database Function
def load_to_postgres(payload):
    conn = psycopg.connect(DB_URI)
    cur = conn.cursor()
    for order in payload:
        cur.execute("""
            INSERT INTO public.sales
            (sku, sale_price, shipping_charged, ebay_fees, shipping_cost, date_sold)
            VALUES
            (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sku) DO NOTHING           
        """, (
            order['sku'],
            order['sale_price'],
            order['shipping_charged'],
            order['ebay_fees'],
            order['shipping_cost'],
            order['date_sold']
        ))
    conn.commit()
    cur.close()
    conn.close()

#Execution Block
fresh_token = refresh_access_token()
finance_payload = fetch_finance_data(fresh_token)
fulfillment_payload = fetch_ebay_data(fresh_token)
for order in fulfillment_payload:
    order_id = order.get("order_id")
    actual_cost = finance_payload.get(order_id, 0.00)
    order["shipping_cost"] = float(actual_cost)
    print(f"Successfully processed {len(fulfillment_payload)} orders.")
load_to_postgres(fulfillment_payload)