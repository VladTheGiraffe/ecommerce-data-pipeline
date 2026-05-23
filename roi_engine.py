import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

#Connect to the database
def get_database_connection():
    conn = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

#Create the definition
def get_full_receipt(sku, conn):
    #Create the cursor
    with conn.cursor() as cur:
        #Write the query
        query = """
            SELECT
                l.player_name, l.allocated_cost, s.sale_price,
                s.shipping_charged, s.ebay_fees, s.shipping_cost
            FROM 
                sports_cards.sales s
            JOIN
                sports_cards.listings l ON s.sku = l.sku
            WHERE 
                s.sku = %s;
        """

        #Execute and Fetch
        cur.execute(query, (sku,))
        data = cur.fetchone()

    if data is None:
        return None
    
    #Math Engine

    #Unpack the tuple
    player_name, allocated_cost, sale_price, shipping_charged, ebay_fees, shipping_cost = data

    allocated_cost = float(allocated_cost) if allocated_cost is not None else 0.0
    sale_price = float(sale_price) if sale_price is not None else 0.0
    shipping_charged = float(shipping_charged) if shipping_charged is not None else 0.0
    ebay_fees = float(ebay_fees) if ebay_fees is not None else 0.0
    shipping_cost = float(shipping_cost) if shipping_cost is not None else 0.0


    #Run the math logic
    total_revenue = sale_price + shipping_charged
    total_expenses = allocated_cost + shipping_cost + ebay_fees
    true_profit = total_revenue - total_expenses
    roi_percentage = (true_profit / allocated_cost) * 100 if allocated_cost > 0 else 0

    #Clean dictionary
    return {
        "player_name": player_name,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "true_profit": true_profit,
        "roi_percentage": roi_percentage
    }


def get_player_margins(conn):
    #Connect to database
    with conn.cursor() as cur:
        #Write the query
        query = """
            SELECT 
                l.player_name, SUM((s.sale_price + s.shipping_charged) - (l.allocated_cost + s.shipping_cost + s.ebay_fees)) AS total_profit
            FROM 
                sports_cards.sales s
            JOIN 
                sports_cards.listings l ON s.sku = l.sku
            GROUP BY
                l.player_name
            """
        
        cur.execute(query)
        return cur.fetchall()
    