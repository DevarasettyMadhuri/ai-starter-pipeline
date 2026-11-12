import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import requests
import os

# Connect to the Docker network services
DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/devdb")
API_URL = os.getenv("API_URL", "http://localhost:8000/clean-record")

engine = create_engine(DB_URL)

st.set_page_config(page_title="AI Pipeline", layout="wide")
st.title("🗄️ AI Data Pipeline Dashboard")

# --- SECTION 1: View the Silver Layer (Database) ---
st.header("1. Curated Customers (Silver Layer)")
try:
    df = pd.read_sql("SELECT * FROM curated_customers", engine)
    st.dataframe(df, use_container_width=True)
    st.success(f"Successfully loaded {len(df)} records from PostgreSQL.")
except Exception as e:
    st.warning("No data found. The database might be empty.")

st.divider()

# --- SECTION 2: Trigger the FastAPI & LLM Pipeline ---
st.header("2. Submit Raw Record for AI Cleaning")
with st.form("new_record_form"):
    col1, col2 = st.columns(2)
    
    cust_id = col1.number_input("Customer ID", value=999)
    name = col2.text_input("Raw Name (Messy)", value="jOhN dOe")
    state = col1.text_input("State", value="new york")
    address = col2.text_input("Raw Address", value="123 dirty street, ny")
    
    submitted = st.form_submit_button("Clean & Save via AI")
    
    if submitted:
        payload = {
            "cust_id": cust_id,
            "name": name,
            "state": state,
            "raw_address": address
        }
        
        with st.spinner("LLM is processing..."):
            res = requests.post(API_URL, json=payload)
            
        if res.status_code == 200:
            st.success("Record cleaned and saved! Refresh the page to see it in the table above.")
            st.json(res.json())
        else:
            st.error(f"API Error: {res.text}")