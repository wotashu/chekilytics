import datetime
from logging import exception

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from figures import get_bar_fig, get_pie_fig
from loaders import get_datetime_cols, get_worksheet, get_worksheet_location


def group_cheki_by_name(df):
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
    elif len(split_result) == 2:
        name = " ".join(split_result[0].split())
        group = " ".join(split_result[1].split())
        return [name, group]
    else:
        raise exception


def get_cutoff_data(df, cutoff: int):
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


def main():
    sheet_url = st.secrets["private_gsheets_url"]
    cheki_df = get_worksheet(sheet_url, 0)
    dated_cheki_df = get_datetime_cols(cheki_df)
    names_df = group_cheki_by_name(dated_cheki_df)
    person_df = get_worksheet(sheet_url, 1)
    venue_df = get_worksheet_location(sheet_url, 3)

    earliest_date = names_df.date.min()
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

    st.write("Selected dates are", first_date, last_date)

    names_df = names_df[names_df.date.between(first_date, last_date)]

    all_persons = get_all_names(person_df)
    print(all_persons[:10])

    select_person = st.sidebar.selectbox(
        "Search for a name", np.insert(all_persons, 0, "")
    )

    groupby_select = st.sidebar.selectbox(
        "Choose Columns to group by",
        ("name", "cheki_id", "location"),
    )

    plot_type = "dataframe"

    if "name" in groupby_select:
        also_group_by_date = st.sidebar.checkbox("Also group by date?", value=False)
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
        if select_person:
            df = df[df["name"] == select_person]

        if groupby_select:
            plot_type = st.sidebar.selectbox(
                "Pick a plot type", ("dataframe", "bar", "pie")
            )

    elif "location" in groupby_select:
        df = names_df.groupby("location")["person"].count().reset_index()
        df = df.rename(columns={"person": "total"})
        df = df.sort_values(by="total", ascending=False)
        df = pd.merge(df, venue_df, how="left", left_on="location", right_on="location")

        if groupby_select:
            plot_type = st.sidebar.selectbox(
                "Pick a plot type", ("dataframe", "bar", "pie")
            )
    else:
        df = dated_cheki_df
        df = df[
            (df.date >= pd.to_datetime(first_date))
            & (df.date <= pd.to_datetime(last_date))
        ]
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        if select_person:
            temp_dfs = []
            name_cols = [col for col in df.columns if "name" in col]
            for col in name_cols:
                temp_dfs.append(df[df[col].str.contains(select_person)])
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

    if plot_type == "dataframe":
        st.dataframe(df, 800, 800)

    elif plot_type in ["bar", "pie"]:
        if groupby_select:
            max_value = int(df["total"].max())
            cutoff = st.slider(
                "Cutoff for other", 0, max_value, round(df["total"].median())
            )
            if cutoff > 0:
                df = get_cutoff_data(df, cutoff)
            if "name" in groupby_select:
                if plot_type == "bar":
                    fig = get_bar_fig(df)
                elif plot_type == "pie":
                    fig = get_pie_fig(df)
            else:
                if plot_type == "bar":
                    fig = px.bar(
                        df.sort_values(by="total", ascending=False),
                        y="total",
                        x=groupby_select[0],
                        color="total",
                    )
                elif plot_type == "pie":
                    if "color" in df.columns:
                        fig = px.pie(
                            df.sort_values(by="total", ascending=False),
                            names=groupby_select[0],
                            values="total",
                            color="color",
                        )
                    else:
                        fig = px.pie(
                            df.sort_values(by="total", ascending=False),
                            names=groupby_select[0],
                            values="total",
                        )
        else:
            fig = px.pie(df, values="person")

        st.plotly_chart(fig)

    st.write(f"Total values: {len(df)}")


if __name__ == "__main__":
    main()
