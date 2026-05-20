import streamlit as st
from roi_engine import get_full_receipt, get_database_connection

@st.cache_resource
def init_db():
    return get_database_connection()
conn = init_db()

st.title("Sports Card ROI Dashboard")
lookup_sku = st.text_input("Enter inventory SKU:")
if st.button("Calculate True Profit"):
    if lookup_sku:
        data = get_full_receipt(lookup_sku, conn)
        if data is None:
            st.warning("No completed sale found for SKU: {lookup_sku}")
        else:
            st.subheader(f"Receipt: {data['player_name']}")
            
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(label="Total Revenue", value=f"${data['total_revenue']:.2f}")
            with col2:
                st.metric(label="Total Expenses", value=f"${data['total_expenses']:.2f}")
            with col3:
                st.metric(label="True Profit", value=f"${data['true_profit']:.2f}", delta=f"{data['roi_percentage']:.1f}% ROI")

