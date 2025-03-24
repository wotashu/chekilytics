from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

import src.figures as figures
import src.munge as munge
from src.geo import get_map_layer


def get_cheki_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    chart_data = df.copy()
    chart_data["datetime"] = pd.to_datetime(chart_data["date"])
    chart_data.set_index("datetime", inplace=True)
    df_groupby = chart_data.groupby(pd.Grouper(freq="MS"))["name1"].count()
    df_groupby.rename("count", inplace=True)
    updated_df = df_groupby.to_frame()
    return updated_df


def limit_to_selected_persons(
    selected_persons: list[str], df: pd.DataFrame
) -> pd.DataFrame:
    temp_dfs = []
    name_cols = [col for col in df.columns if "name" in col]
    for col in name_cols:
        for person in selected_persons:
            temp_dfs.append(df[df[col].str.contains(person)])
    dated_cheki_df = pd.concat(temp_dfs)

    dated_cheki_df = dated_cheki_df.replace("", np.nan)
    dated_cheki_df = dated_cheki_df.dropna(how="all", axis=1)
    dated_cheki_df = dated_cheki_df.replace(np.nan, "")
    dated_cheki_df.sort_values("date", inplace=True)
    return dated_cheki_df


def get_cheki_map_data(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("location")["date"].count()
    map_df = grouped.reset_index()
    map_df.rename(columns={"date": "count"}, inplace=True)
    cheki_map_df = pd.merge(
        map_df,
        df[["location", "latitude", "longitude", "full_address"]],
        how="inner",
        on="location",
    )
    # df = df[["location", "latitude", "longitude", "full_address"]]
    cheki_map_df = cheki_map_df.replace("", np.nan)
    cheki_map_df = cheki_map_df.dropna(axis=0, how="any")
    cheki_map_df.drop_duplicates(inplace=True)
    # df = df.reset_index(drop=True)

    cheki_map_df["latitude"] = cheki_map_df["latitude"].astype(float)
    cheki_map_df["longitude"] = cheki_map_df["longitude"].astype(float)
    return cheki_map_df


def get_cheki_tab(
    first_date: date,
    last_date: date,
    venue_df: pd.DataFrame,
    selected_persons: list[str],
    dated_cheki_df: pd.DataFrame,
) -> None:
    ranged_cheki_df = dated_cheki_df[
        (dated_cheki_df.date >= pd.to_datetime(first_date))
        & (dated_cheki_df.date <= pd.to_datetime(last_date))
    ]
    ranged_cheki_df["date"] = ranged_cheki_df["date"].dt.strftime("%Y-%m-%d")
    merged_cheki_data = pd.merge(
        dated_cheki_df,
        venue_df,
        how="left",
        left_on="location",
        right_on="location",
    )

    if selected_persons:
        merged_cheki_data = limit_to_selected_persons(
            selected_persons, merged_cheki_data
        )

    map_tab, chart_tab, data_tab = st.tabs(["🗺️ Map", "📈 Chart", "🗃 Data"])

    with data_tab:
        st.dataframe(merged_cheki_data, 800, 800)

    with chart_tab:
        cheki_chart_data = get_cheki_chart_data(merged_cheki_data)
        fig = figures.get_cheki_bar_fig(cheki_chart_data)
        st.plotly_chart(fig)

    with map_tab:
        merged_cheki_data.copy()
        cheki_map_df = get_cheki_map_data(merged_cheki_data)

        (
            heat_tab,
            column_tab,
            scatter_tab,
        ) = st.tabs(["🔥Heatmap", "🏢Column", "⭕Scatter"])

        with heat_tab:
            deck = get_map_layer(df=cheki_map_df, map_type="heat")
            st.pydeck_chart(deck)
        with column_tab:
            deck = get_map_layer(df=cheki_map_df, map_type="column")
            st.pydeck_chart(deck)
        with scatter_tab:
            deck = get_map_layer(df=cheki_map_df, map_type="scatter")
            st.pydeck_chart(deck)

        st.dataframe(cheki_map_df, use_container_width=True)
        st.write(
            f"Total values: {len(cheki_map_df)}, count: {cheki_map_df['count'].sum()}"
        )


def get_name_tab(
    names_df: pd.DataFrame, person_df: pd.DataFrame, selected_persons: list[str]
) -> None:
    also_group_by_date = st.checkbox("Also group by date?", value=False)
    if also_group_by_date:
        groupby_select = ["date", "name"]
        sort_level = 2
    else:
        groupby_select = ["name"]
        sort_level = 1
    name_df = munge.get_records_df(
        names_df=names_df,
        person_df=person_df,
        groupby_select=groupby_select,
        sort_level=sort_level,
    )

    name_df.columns = pd.Index([str(col) for col in name_df.columns])
    if selected_persons:
        name_df = name_df[name_df["name"].isin(selected_persons)]

    chart_tab, data_tab = st.tabs(["📈 Chart", "🗃 Data"])

    with data_tab:
        st.dataframe(name_df, 800, 800)

    with chart_tab:
        max_value = name_df["total"].max()
        if max_value is not np.nan:
            max_value = int(name_df["total"].max())

            col1, col2 = st.columns(2)

            with col1:
                cutoff_value = 0
                if len(selected_persons) >= 12:
                    cutoff_value = round(name_df["total"].median())
                cutoff = st.number_input(
                    "Cutoff for other",
                    min_value=0,
                    max_value=max_value,
                    value=cutoff_value,
                )
                if cutoff > 0:
                    name_df = munge.get_cutoff_data(name_df, int(cutoff))
            with col2:
                value = len(name_df)
                if len(name_df) > 100:
                    value = 100
                top_n = st.number_input(
                    "Keep top n",
                    step=1,
                    min_value=0,
                    max_value=len(name_df) + 1,
                    value=value,
                )

            if isinstance(top_n, int):
                name_df = name_df.head(top_n)

            treemap_tab, bar_tab, pie_tab = st.tabs(["🌳treemap", "📊bar", "🥧pie"])
            with treemap_tab:
                use_groups = st.checkbox(label="Use Groups")
                fig = figures.get_treemap_fig(name_df, use_groups=use_groups)
                st.plotly_chart(fig, use_container_width=True)
            with bar_tab:
                fig = figures.get_bar_fig(name_df)
                st.plotly_chart(fig)
            with pie_tab:
                fig = figures.get_pie_fig(name_df)
                st.plotly_chart(fig)
