import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import gspread
import pandas as pd
import numpy as np

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)
gc = gspread.authorize(credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows


@st.cache(ttl=600)
def get_worksheet(url, sheet_num=0):
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    df["Date"] = pd.to_datetime(df['Date'])
    df["Month"]  = df["Date"].dt.month
    df["Year"] = df['Date'].dt.year
    df['Name1'] = df['Name1'].str.title()
    df['Cheki'] = 0
    return df


def group_cheki_by_name(df):
    chekis = []
    for _, row in df.iterrows():
        for col in df.columns:
            if (row[col] is not np.nan) and ('Name' in col) and (row[col]):
                chekis.append(
                    {'date': row["Date"], 'person': row[col].title()}
                )
    return pd.DataFrame(chekis)


sheet_url = st.secrets["private_gsheets_url"]
df = get_worksheet(sheet_url, 0)
df = group_cheki_by_name(df)

st.dataframe(df)
# rows = run_query(f'SELECT * FROM "{sheet_url}"')

# Print results.
# for row in rows:
#    st.write(f"{row.Name1} has a :{row.Date}:")