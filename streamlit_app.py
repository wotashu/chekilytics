import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List


@st.cache
def get_checki_data():
    filepath = "/mnt/c/Users/jolin/Downloads/cheki.csv"
    df = pd.read_csv(filepath)
    return df


def get_group(name: str) -> List[str]:
    name_group = name.split("@")
    try:
        group = name_group[1]
        return group
    except IndexError:
        return name


df = get_checki_data()
df = pd.DataFrame(
    df.groupby(
        ['person'])['date'].count().sort_values(ascending=False)
    ).reset_index()
df.columns = ['name', "count"]

df = df.query('count>10')
df['group'] = df['name'].apply(get_group)
df['name'] = df['name'].str.replace("@.+", "", regex=True)

df

df = df.sort_values(by='count', ascending=True)

fig = px.bar(df, x='count', y='group', color='name', height=900)
st.plotly_chart(fig, use_container_width=True)
