import datetime
from logging import exception
from typing import List

import gspread
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2 import service_account

COLOR_DESCRETE_MAP = {
    "Suzy": "#EF553B".lower(),
    "OTHERS": "rgb(153,153,153)",
    "七瀬千夏": "#EF553B".lower(),
    "天音ゆめ": "#AB63FA".lower(),
    "恵深あむ": "#FECB52".lower(),
    "楠木りほ": "#19D3F3".lower(),
    "大西春菜": "#636EFA".lower(),
    "椎名まどか": "#19D3F3".lower(),
    "中谷亜優": "rgb(242,242,242)",
    "石田綾音": "#FF97FF".lower(),
    "濱崎みき": "rgb(242,242,242)",
    "瀬乃悠月": "#EF553B".lower(),
    "望月紗奈": "#FF97FF".lower(),
    "音羽のあ": "#636EFA".lower(),
    "火野快飛": "#636EFA".lower(),
    "メグ・ピッチ・オリオン": "#00CC96".lower(),
}


def get_google_conn():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    return gspread.authorize(credentials)


gc = get_google_conn()


# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def get_worksheet(url, sheet_num=0):
    worksheet = gc.open_by_url(url).get_worksheet(sheet_num)
    df = pd.DataFrame(worksheet.get_all_values())
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    df["Cheki"] = 0
    return df


def group_cheki_by_name(df):
    chekis = []
    for _, row in df.iterrows():
        for col in df.columns:
            if (row[col] is not np.nan) and ("Name" in col) and (row[col]):
                chekis.append(
                    {
                        "date": row["Date"].date(),
                        "person": row[col],
                        "location": row["Location"],
                        "year": row["Date"].year,
                        "month": row["Date"].month,
                        "name": split_name_group(row[col])[0],
                        "group": split_name_group(row[col])[1],
                    }
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


def get_bar_fig(df, **kwargs):
    return px.bar(
        df.sort_values(by="count", ascending=False),
        x="count",
        y="name",
        color="name",
        text="count",
        title=f"結果: {df['count'].sum()}枚数",
        color_discrete_map=COLOR_DESCRETE_MAP,
    )


def get_pie_fig(df):
    fig = px.pie(
        df.sort_values(by="count", ascending=True),
        names="name",
        values="count",
        color_discrete_map=COLOR_DESCRETE_MAP,
    )
    fig.update_traces(textposition="inside", textinfo="value+label")
    return fig


def get_cutoff_data(df, cutoff: int):
    df_top = df[df["count"] >= cutoff]
    df_bottom = df[df["count"] < cutoff]
    others_count = df_bottom["count"].sum()
    df_top = df_top.append(
        {"count": others_count, "name": "OTHERS", "group": "OTHERS"},
        ignore_index=True
    )
    return df_top


def main():
    sheet_url = st.secrets["private_gsheets_url"]
    df = get_worksheet(sheet_url, 0)
    df = group_cheki_by_name(df)

    earliest_date = df.date.min()
    today = datetime.datetime.today().date()
    last_date = today
    first_date = datetime.date(today.year, 1, 1)

    date_selector = st.sidebar.date_input(
        "Select date range",
        value=[first_date, today],
        min_value=earliest_date,
        max_value=today,
    )

    if len(date_selector) == 2:
        first_date = date_selector[0]
        last_date = date_selector[1]

    st.write("Selected dates are", first_date, last_date)

    df = df[df.date.between(first_date, last_date)]

    groupby_select = st.sidebar.multiselect(
        "Choose Columns to group by",
        ("name", "group", "location", "date", "year", "month")
    )

    st.write(f"Total values: {len(df)}")

    plot_type = st.sidebar.selectbox("Pick a plot type", ("dataframe", "bar", "pie"))

    if groupby_select:
        df = df.groupby(groupby_select)['person'].count().reset_index()
        df = df.rename(columns={'person': 'count'})

    if plot_type == "dataframe":
        st.dataframe(df)

    elif plot_type in ["bar", "pie"]:
        if groupby_select:
            max_value = int(df["count"].max())
            cutoff = st.slider(
                "Cutoff for other", 0, max_value, round(df["count"].median())
            )
            if cutoff > 0:
                df = get_cutoff_data(df, cutoff)
            if 'name' in groupby_select:
                if plot_type == "bar":
                    fig = get_bar_fig(df)
                elif plot_type == "pie":
                    fig = get_pie_fig(df)
            else:
                if plot_type == "bar":
                    fig = px.bar(
                        df.sort_values(by="count", ascending=False),
                        y='count',
                        x=groupby_select[0],
                        color="count",
                        # text=groupby_select[1],
                    )
                elif plot_type == "pie":
                    fig = px.pie(
                        df.sort_values(by='count', ascending=False),
                        names=groupby_select[0],
                        values='count'
                    )
        else:
            fig = px.pie(df, values="person")
        
        st.plotly_chart(fig)



if __name__ == "__main__":
    main()
