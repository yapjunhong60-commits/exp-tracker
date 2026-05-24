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
    try:
        creds_dict = st.secrets["google_credentials"]
        print("Using credentials from Streamlit secrets")
    except:
        creds_dict = json.load(open("exp-tracker-496805-7f9858049fd3.json"))
        print("Using credentials from local JSON file")

    scope = ["https://spreadsheets.google.com/feeds", 
            "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Exp_Tracker_Data").sheet1
    return sheet

def load_data_from_gsheet(sheet):
    try:
        records = sheet.get_all_records()
        if records:
            # Convert to DataFrame
            df = pd.DataFrame(records)
            return df
        else:
            st.error("Sheet is unexpectedly empty!")
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None
    
def add_expense_to_gsheet(sheet, in_out, date, description, amount, category):
    # try:
    #     sheet.append_row([in_out, str(date), description, amount, category])
    #     return True
    # except Exception as e:
    #     st.error(f"Error adding expense: {e}")
    #     return False
    #To Do Auto Column Search (2 Extra API Calls Apparently)
    
    try:
        headers = sheet.row_values(1)
        in_out_col   = headers.index("In/Out")       + 1
        date_col     = headers.index("Date")         + 1
        desc_col     = headers.index("Description")  + 1
        amount_col   = headers.index("Amount")       + 1
        category_col = headers.index("Category")     + 1
        next_row = len(sheet.col_values(1)) + 1
        # sheet.update_cell(next_row, date_col, str(date))   
        # sheet.update_cell(next_row, desc_col, description) 
        # sheet.update_cell(next_row, amount_col, amount)    
        # sheet.update_cell(next_row, category_col, category)
        sheet.batch_update([{
            'range': f'{chr(64 + in_out_col)}{next_row}',
            'values': [[str(in_out)]]
        }, {
            'range': f'{chr(64 + date_col)}{next_row}',
            'values': [[str(date)]]
        }, {
            'range': f'{chr(64 + desc_col)}{next_row}',
            'values': [[description]]
        }, {
            'range': f'{chr(64 + amount_col)}{next_row}',
            'values': [[amount]]
        }, {
            'range': f'{chr(64 + category_col)}{next_row}',
            'values': [[category]]
        }])
        return True
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return False
    
def ui_submission(sheet):
    st.title("Exp")
    with st.form("exp_form"):
        in_out = st.selectbox("In/Out", ["In", "Out"], index=1)
        date = st.date_input("Date")
        category = st.text_input("Category", value="c")
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        
        submitted = st.form_submit_button("Add Exp")
        if submitted:
            if not description or not category:
                st.warning("Please fill in both Description and Category!")
                return False
            elif amount <= 0:
                st.warning("Amount must be greater than 0!")
                return False
            else:
                success = add_expense_to_gsheet(sheet, in_out, date, description, amount, category)
                if success:
                    st.success(f"✅ Added: {description} - ${amount:.2f} ({category})")
                    return True
                return False
        return False

def display_charts(df):
    st.subheader("All Exp")
    st.dataframe(df)

    if not df.empty:
        st.subheader("Exp Breakdown by Category")
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

def main():
    sheet = connect_to_gsheet()
    df = load_data_from_gsheet(sheet)
    if df is None:
        st.stop()
    if ui_submission(sheet):
        df = load_data_from_gsheet(sheet)
    display_charts(df)

# def main():
#     sheet = connect_to_gsheet()
#     # Show form and check if expense was added
#     if ui_submission(sheet):
#         st.rerun()  # ← Complete refresh
#     # Always load fresh data after potential changes
#     df = load_data_from_gsheet(sheet)
#     display_charts(df)

if __name__ == "__main__":
    main()









