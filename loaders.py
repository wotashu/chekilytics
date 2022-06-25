from connections import get_google_conn
import streamlit as st
import pandas as pd

gc = get_google_conn()


# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600, allow_output_mutation=True)
def get_worksheet(url, sheet_num=0):
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    df.columns = [col.lower() for col in df.columns]
    return df


@st.cache(ttl=600, allow_output_mutation=True)
def get_worksheet_location(url, sheet_num=2):
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = df.iloc[0]
    df.columns = [col.lower() for col in df.columns]
    df.drop(df.index[0], inplace=True)
    return df


@st.cache(ttl=600, allow_output_mutation=True)
def get_worksheet_names(url, sheet_num=1):
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    return df


def get_datetime_cols(df):
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    return df