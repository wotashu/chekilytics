import gspread
import streamlit as st
from google.oauth2 import service_account


def get_google_conn():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    return gspread.authorize(credentials)
