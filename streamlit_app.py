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

    name_tab, cheki_tab = st.tabs(["💃name", "🎴cheki"])

    with name_tab:
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

        name_df.columns = [str(col) for col in name_df.columns]
        if selected_persons:
            name_df = name_df[name_df["name"].isin(selected_persons)]

        chart_tab, data_tab = st.tabs(["📈 Chart", "🗃 Data"])

        with data_tab:
            st.dataframe(name_df, 800, 800)

        with chart_tab:
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
                    name_df = munge.get_cutoff_data(name_df, cutoff)
            with col2:
                top_n = st.number_input(
                    "Keep top n",
                    step=1,
                    min_value=0,
                    max_value=len(name_df) + 1,
                    value=0,
                )

            if top_n:
                name_df = name_df.head(top_n)

            treemap_tab, bar_tab, pie_tab = st.tabs(["🌳treemap", "📊bar", "🥧pie"])
            with treemap_tab:
                fig = figures.get_treemap_fig(name_df)
                st.plotly_chart(fig)
            with bar_tab:
                fig = figures.get_bar_fig(name_df)
                st.plotly_chart(fig)
            with pie_tab:
                fig = figures.get_pie_fig(name_df)
                st.plotly_chart(fig)

    with cheki_tab:
        dated_cheki_df = dated_cheki_df[
            (dated_cheki_df.date >= pd.to_datetime(first_date))
            & (dated_cheki_df.date <= pd.to_datetime(last_date))
        ]
        dated_cheki_df["date"] = dated_cheki_df["date"].dt.strftime("%Y-%m-%d")
        dated_cheki_df = pd.merge(
            dated_cheki_df,
            venue_df,
            how="left",
            left_on="location",
            right_on="location",
        )

        if selected_persons:
            temp_dfs = []
            name_cols = [col for col in dated_cheki_df.columns if "name" in col]
            for col in name_cols:
                for person in selected_persons:
                    temp_dfs.append(
                        dated_cheki_df[dated_cheki_df[col].str.contains(person)]
                    )
            dated_cheki_df = pd.concat(temp_dfs)

            dated_cheki_df = dated_cheki_df.replace("", np.nan)
            dated_cheki_df = dated_cheki_df.dropna(how="all", axis=1)
            dated_cheki_df = dated_cheki_df.replace(np.nan, "")
            dated_cheki_df.sort_values("date", inplace=True)

        tab1, tab2 = st.tabs(["🗺️ Map", "🗃 Data"])

        with tab2:
            st.dataframe(dated_cheki_df, 800, 800)

        with tab1:
            logger.debug(f"DF preview: {dated_cheki_df.head()}")
            logger.debug(f"DF columns: {dated_cheki_df.columns}")
            logger.debug(f"DF shape: {dated_cheki_df.shape}")

            df_groupby = (
                dated_cheki_df.groupby("location")["date"]
                .count()
                .reset_index()
                .rename(columns={"date": "count"})
            )
            cheki_map_df = pd.merge(
                df_groupby,
                dated_cheki_df[["location", "latitude", "longitude", "full_address"]],
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

    st.write(f"Total values: {len(dated_cheki_df)}")


if __name__ == "__main__":
    main()
