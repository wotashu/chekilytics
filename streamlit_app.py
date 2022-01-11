from logging import exception
import streamlit as st
from google.oauth2 import service_account
import gspread
import pandas as pd
import numpy as np
import plotly.express as px
from typing import List


# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
gc = gspread.authorize(credentials)

# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def get_worksheet(url, sheet_num=0):
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    df["Date"] = pd.to_datetime(df['Date'])
    df["Month"]  = df["Date"].dt.month
    df["Year"] = df['Date'].dt.year
    df['Cheki'] = 0
    return df


def group_cheki_by_name(df):
    chekis = []
    for _, row in df.iterrows():
        for col in df.columns:
            if (row[col] is not np.nan) and ('Name' in col) and (row[col]):
                chekis.append(
                    {'date': row["Date"], 'person': row[col]}
                )
    return pd.DataFrame(chekis)


def split_name_group(person: str) -> List[str]:
    split_result = person.split("@")
    if len(split_result) == 1:
        name = " ".join(split_result[0].split())
        return [name, name]
    elif len(split_result) == 2:
        name = " ".join(split_result[0].split())
        group = " ".join(split_result[1].split())
        return [name, group]
    else:
        raise exception


sheet_url = st.secrets["private_gsheets_url"]
df = get_worksheet(sheet_url, 0)
df = group_cheki_by_name(df)
df = df.groupby(['person']).count().sort_values(by='date', ascending=False).reset_index()
df.columns = ["person", "count"]
name_splits = pd.DataFrame(df['person'].apply(lambda x: split_name_group(x)).values.tolist())
name_splits.columns = ["name", "group"]
df = pd.concat([df, name_splits], axis=1)

print(name_splits)

st.dataframe(df)

fig = px.bar(df.sort_values(by='count', ascending=True), x="count", y="name", color="group")
st.plotly_chart(fig)

df_top = df[df['count'] >= 40]
df_bottom = df[df['count'] < 40]
others_count = df_bottom['count'].sum()
df_top = df_top.append({"count": others_count, "name": "OTHERS", "group": "OTHERS"}, ignore_index=True)

fig2 = px.pie(df_top, names="name", values="count")
st.plotly_chart(fig2)