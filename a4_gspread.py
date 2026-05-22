import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json  # ← NEW: to read the JSON key file
import gspread  # ← NEW: to connect to Google Sheets
from google.oauth2.service_account import Credentials

# script_direc = os.path.dirname(os.path.abspath(__file__))
# os.chdir(script_direc)

def connect_to_gsheet():
    creds_dict = json.load(open("exp-tracker-496805-7f9858049fd3.json"))
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Exp_Tracker_Data").sheet1
    return sheet

# Connect to Google Sheets
sheet = connect_to_gsheet()

# Get all data from the sheet
def load_data_from_gsheet():
    """Load all expenses from Google Sheets into a DataFrame"""
    try:
        records = sheet.get_all_records()
        if records:
            # Convert to DataFrame
            df = pd.DataFrame(records)
        else:
            # Empty DataFrame with correct columns
            df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

def add_expense_to_gsheet(date, description, amount, category):
    try:
        sheet.append_row([str(date), description, amount, category])
        return True
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return False

# Load existing data
df = load_data_from_gsheet()

st.title("Smart Expense Tracker")
with st.form("expense_form"):
    date = st.date_input("Date")
    description = st.text_input("Description")
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if not description or not category:
            st.warning("Please fill in both Description and Category!")
        elif amount <= 0:
            st.warning("Amount must be greater than 0!")
        else:
            success = add_expense_to_gsheet(date, description, amount, category)
            if success:
                df = load_data_from_gsheet()
                st.success(f"✅ Added: {description} - ${amount:.2f} ({category})")

st.subheader("All Expenses")
st.dataframe(df)

if not df.empty:
    st.subheader("Expense Breakdown by Category")
    category_totals = df.groupby("Category")["Amount"].sum()

    # Bar Chart
    fig, ax = plt.subplots()
    category_totals.plot(kind="bar", ax=ax)
    ax.set_ylabel("Amount")
    st.pyplot(fig)

    # Pie Chart
    st.subheader("Category Distribution")
    fig2, ax2 = plt.subplots()
    category_totals.plot(kind="pie", autopct="%1.1f%%", ax=ax2)
    st.pyplot(fig2)