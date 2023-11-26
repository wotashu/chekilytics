import pandas as pd
import streamlit as st

from src.connections import get_google_conn

gc = get_google_conn()


# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def get_worksheet(url: str, sheet_num: int = 0):
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    df.columns = pd.Index([str(col).lower() for col in df.columns])
    return df


@st.cache_data(ttl=600)
def get_worksheet_location(url: str, sheet_num: int = 3) -> pd.DataFrame:
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    cols = df.iloc[0]
    df.columns = pd.Index(["_".join(col.lower().split()) for col in cols])
    df.drop(df.index[0], inplace=True)
    return df


@st.cache_data(ttl=600)
def get_worksheet_names(url: str, sheet_num: int = 1) -> pd.DataFrame:
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = pd.Index(df.iloc[0])
    df.drop(df.index[0], inplace=True)
    return df


def get_datetime_cols(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    return df
