import io
import csv
import streamlit as st
import os 
from dotenv import load_dotenv
from roi_engine import get_full_receipt, get_database_connection, get_player_margins, clean_money

load_dotenv()

@st.cache_resource
def init_db():
    return get_database_connection()
conn = init_db()

# ----Player Margin Data----
margin_data = get_player_margins(conn)
with st.sidebar:
    st.header("Player Margins")
    for player, margin in margin_data:
        st.metric(label=player, value=f"${margin:.2f}")
        pass

#----Single Item Lookup----

st.title("Sports Card ROI Dashboard")
with st.form(key="sku_form"):
    lookup_sku = st.text_input("Enter inventory SKU:")
    submit_button = st.form_submit_button("Calculate True Profit")
    if submit_button:
        if lookup_sku:
            data = get_full_receipt(lookup_sku, conn)
            if data is None:
                st.warning(f"No completed sale found for SKU: {lookup_sku}")
            else:
                st.subheader(f"Receipt: {data['player_name']}")
                
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(label="Total Revenue", value=f"${data['total_revenue']:.2f}")
                with col2:
                    st.metric(label="Total Expenses", value=f"${data['total_expenses']:.2f}")
                with col3:
                    st.metric(label="True Profit", value=f"${data['true_profit']:.2f}", delta=f"{data['roi_percentage']:.1f}% ROI")


#----CSV Upload----
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
if uploaded_file is not None: 
    raw_text = uploaded_file.getvalue().decode("utf-8")
    virtual_file = io.StringIO(raw_text)
    for _ in range(11):
        next(virtual_file)  # Skip header row
    reader = csv.DictReader(virtual_file)
    # 1. Create the empty Staging Area
    transaction_staging = {}
        
    for row in reader:
        order_num = row.get('Order number', '')
            
            
        if not order_num or order_num == "":
            continue
                    
            
        if order_num not in transaction_staging:
            transaction_staging[order_num] = {
                "Title": "Unknown",
                "SKU": "Unknown",
                "Total Sold": 0.0,
                "Total Shipping Collected": 0.0,
                "Total Fees": 0.0,
                "Total Shipping Paid": 0.0
            }
                
                
        if row.get('Item title', '') != "":
            transaction_staging[order_num]["Title"] = row['Item title']
                
        if row.get('Custom label', '') != "": 
            transaction_staging[order_num]["SKU"] = row['Custom label']
                    
                
        transaction_staging[order_num]["Total Sold"] += clean_money(row.get('Item subtotal', ''))
                
        transaction_staging[order_num]["Total Shipping Collected"] += clean_money(row.get('Shipping and handling', ''))
                
                
        fixed_fee = clean_money(row.get('Final Value Fee - fixed', ''))
        variable_fee = clean_money(row.get('Final Value Fee - variable', ''))
        transaction_staging[order_num]["Total Fees"] += (fixed_fee + variable_fee)
                
                
        transaction_staging[order_num]["Total Shipping Paid"] += clean_money(row.get('Net amount', ''))

        
    st.write("--- FINAL AGGREGATED LEDGER ---")
    for order_id, data in transaction_staging.items():
        st.write(f"SKU: {data['SKU']} | Card: {data['Title']} | Sold: {data['Total Sold']} | Fees: {data['Total Fees']} | Label: {data['Total Shipping Paid']}")