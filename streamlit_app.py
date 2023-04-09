import numpy as np
import pandas as pd
import streamlit as st
from loguru import logger

import figures
import munge
from geo import get_map_layer
from loaders import get_datetime_cols, get_worksheet, get_worksheet_location


def main():
    sheet_url = st.secrets["private_gsheets_url"]
    cheki_df = get_worksheet(sheet_url, 0)
    dated_cheki_df = get_datetime_cols(cheki_df)
    names_df = munge.group_cheki_by_name(dated_cheki_df)
    person_df = get_worksheet(sheet_url, 1)
    venue_df = get_worksheet_location(sheet_url, 3)

    col1, col2 = st.columns(2)

    with col1:
        first_date, last_date = munge.get_dates(names_df)
        st.write("Selected dates are", first_date, last_date)

    with col2:
        all_persons = munge.get_all_names(person_df)
        selected_persons = st.multiselect(
            "Search for a name", np.insert(all_persons, 0, "")
        )
        st.write(f"Selected {selected_persons}")

    names_df = names_df[names_df.date.between(first_date, last_date)]

    groupby_select = st.selectbox(
        "Choose Columns to group by",
        ("name", "cheki_id"),
    )

    if "name" in groupby_select:
        also_group_by_date = st.checkbox("Also group by date?", value=False)
        if also_group_by_date:
            groupby_select = ["date", "name"]
            sort_level = 2
        else:
            groupby_select = ["name"]
            sort_level = 1
        df = munge.get_records_df(
            names_df=names_df,
            person_df=person_df,
            groupby_select=groupby_select,
            sort_level=sort_level,
        )

        df.columns = [str(col) for col in df.columns]
        if selected_persons:
            df = df[df["name"].isin(selected_persons)]

        chart_tab, data_tab = st.tabs(["📈 Chart", "🗃 Data"])

        with data_tab:
            st.dataframe(df, 800, 800)

        with chart_tab:
            max_value = int(df["total"].max())

            col1, col2 = st.columns(2)

            with col1:
                cutoff_value = 0
                if len(selected_persons) >= 12:
                    cutoff_value = round(df["total"].median())
                cutoff = st.number_input(
                    "Cutoff for other",
                    min_value=0,
                    max_value=max_value,
                    value=cutoff_value,
                )
                if cutoff > 0:
                    df = munge.get_cutoff_data(df, cutoff)
            with col2:
                top_n = st.number_input(
                    "Keep top n", step=1, min_value=0, max_value=len(df) + 1, value=0
                )

            if top_n:
                df = df.head(top_n)

            treemap_tab, bar_tab, pie_tab = st.tabs(["🌳treemap", "📊bar", "🥧pie"])
            with treemap_tab:
                fig = figures.get_treemap_fig(df)
                st.plotly_chart(fig)
            with bar_tab:
                fig = figures.get_bar_fig(df)
                st.plotly_chart(fig)
            with pie_tab:
                fig = figures.get_pie_fig(df)
                st.plotly_chart(fig)

    elif groupby_select == "cheki_id":
        df = dated_cheki_df
        df = df[
            (df.date >= pd.to_datetime(first_date))
            & (df.date <= pd.to_datetime(last_date))
        ]
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df = pd.merge(df, venue_df, how="left", left_on="location", right_on="location")

        if selected_persons:
            temp_dfs = []
            name_cols = [col for col in df.columns if "name" in col]
            for col in name_cols:
                for person in selected_persons:
                    temp_dfs.append(df[df[col].str.contains(person)])
            df = pd.concat(temp_dfs)

            df = df.replace("", np.nan)
            df = df.dropna(how="all", axis=1)
            df = df.replace(np.nan, "")
            df.sort_values("date", inplace=True)

        tab1, tab2 = st.tabs(["🗺️ Map", "🗃 Data"])

        with tab2:
            st.dataframe(df, 800, 800)

        with tab1:
            logger.debug(f"DF preview: {df.head()}")
            logger.debug(f"DF columns: {df.columns}")
            logger.debug(f"DF shape: {df.shape}")

            df_groupby = (
                df.groupby("location")["date"]
                .count()
                .reset_index()
                .rename(columns={"date": "count"})
            )
            df = pd.merge(
                df_groupby,
                df[["location", "latitude", "longitude", "full_address"]],
                how="inner",
                on="location",
            )
            # df = df[["location", "latitude", "longitude", "full_address"]]
            df = df.replace("", np.nan)
            df = df.dropna(axis=0, how="any")
            df.drop_duplicates(inplace=True)
            # df = df.reset_index(drop=True)

            df["latitude"] = df["latitude"].astype(float)
            df["longitude"] = df["longitude"].astype(float)

            (
                heat_tab,
                column_tab,
                scatter_tab,
            ) = st.tabs(["🔥Heatmap", "🏢Column", "⭕Scatter"])

            with heat_tab:
                deck = get_map_layer(df=df, map_type="heat")
                st.pydeck_chart(deck)
            with column_tab:
                deck = get_map_layer(df=df, map_type="column")
                st.pydeck_chart(deck)
            with scatter_tab:
                deck = get_map_layer(df=df, map_type="scatter")
                st.pydeck_chart(deck)

            st.dataframe(df, use_container_width=True)
            st.write(f"Total values: {len(df)}, count: {df['count'].sum()}")

    st.write(f"Total values: {len(df)}")


if __name__ == "__main__":
    main()
