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
