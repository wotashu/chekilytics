import datetime

import numpy as np
import pandas as pd
import streamlit as st
from loguru import logger

import figures
from geo import get_map_layer
from loaders import get_datetime_cols, get_worksheet, get_worksheet_location


def group_cheki_by_name(df: pd.DataFrame) -> pd.DataFrame:
    name_cols = [col for col in df.columns if "name" in col]
    chekis = []
    for idx, row in df.iterrows():
        name_count = len(list(filter(None, row[name_cols].values)))
        for col in df.columns:
            if (row[col] is not np.nan) and ("name" in col) and (row[col]):
                chekis.append(
                    {
                        "cheki_id": idx,
                        "date": row["date"].date(),
                        "person": row[col],
                        "location": row["location"],
                        "year": row["date"].year,
                        "month": row["date"].month,
                        "name": split_name_group(row[col])[0],
                        "group": split_name_group(row[col])[1],
                        "n_shown": name_count,
                    }
                )
    return pd.DataFrame(chekis)


def split_name_group(person: str) -> list[str]:
    split_result = person.split("@")
    if len(split_result) == 1:
        name = " ".join(split_result[0].split())
        return [name, name]
    if len(split_result) == 2:
        name = " ".join(split_result[0].split())
        group = " ".join(split_result[1].split())
        return [name, group]
    return []


def get_cutoff_data(df: pd.DataFrame, cutoff: int) -> pd.DataFrame:
    df_top = df[df["total"] >= cutoff].reset_index(drop=True)
    df_bottom = df[df["total"] < cutoff]
    others_count = df_bottom["total"].sum()
    others_df = pd.DataFrame(
        {"total": [others_count], "name": ["OTHERS"], "group": ["OTHERS"]}
    )
    df_top = pd.concat([df_top, others_df], axis=0)
    return df_top


def get_all_names(df: pd.DataFrame) -> list[str]:
    return sorted([name for name in df.name1.unique() if name != ""])


def get_dates(input_df) -> tuple[datetime.date, datetime.date]:
    earliest_date = input_df.date.min()
    today = datetime.datetime.today().date()
    last_date = today
    first_date = datetime.date(today.year, 1, 1)

    date_selector = st.date_input(
        "Select date range",
        value=[earliest_date, today],
        min_value=earliest_date,
        max_value=today,
    )

    if len(date_selector) == 2:
        first_date = date_selector[0]
        last_date = date_selector[1]

    return first_date, last_date


def main():
    sheet_url = st.secrets["private_gsheets_url"]
    cheki_df = get_worksheet(sheet_url, 0)
    dated_cheki_df = get_datetime_cols(cheki_df)
    names_df = group_cheki_by_name(dated_cheki_df)
    person_df = get_worksheet(sheet_url, 1)
    venue_df = get_worksheet_location(sheet_url, 3)

    col1, col2 = st.columns(2)

    with col1:
        first_date, last_date = get_dates(names_df)
        st.write("Selected dates are", first_date, last_date)

    with col2:
        all_persons = get_all_names(person_df)
        selected_persons = st.multiselect(
            "Search for a name", np.insert(all_persons, 0, "")
        )
        st.write(f"Selected {selected_persons}")

    names_df = names_df[names_df.date.between(first_date, last_date)]

    groupby_select = st.selectbox(
        "Choose Columns to group by",
        ("name", "cheki_id"),
    )

    plot_type = "dataframe"

    if "name" in groupby_select:
        also_group_by_date = st.checkbox("Also group by date?", value=False)
        if also_group_by_date:
            groupby_select = ["date", "name"]
            sort_level = 2
        else:
            groupby_select = ["name"]
            sort_level = 1
        n_shown_columns = sorted(names_df.n_shown.unique())
        df = (
            names_df.groupby(groupby_select + ["n_shown"])["person"]
            .count()
            .sort_index(level=sort_level)
            .reset_index()
        )
        df = (
            df.pivot(index=groupby_select, columns="n_shown", values="person")
            .fillna(0)
            .astype(int)
        )
        df["total"] = df.sum(axis=1)
        df = df[["total"] + n_shown_columns]
        # df = df.rename(columns={"person": "count"})
        df = df.sort_values(
            by=["total"] + n_shown_columns, ascending=False
        ).reset_index()
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
                    df = get_cutoff_data(df, cutoff)
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

        also_group_by_date = st.sidebar.checkbox("Also group by date?", value=False)
        if also_group_by_date:
            groupby_select = ["date"]
            df = df.groupby(groupby_select)["note"].count().reset_index()
            df = df.rename(columns={"note": "total"})

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
            logger.debug(f"CURRENT DF GROUPBY: {df_groupby}")
            df = pd.merge(
                df_groupby,
                df[["location", "latitude", "longitude", "full_address"]],
                how="inner",
                on="location",
            )
            logger.debug(f"NOW the DF: {df.head()}")
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
