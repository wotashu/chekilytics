import datetime

import numpy as np
import pandas as pd
import streamlit as st
from loguru import logger


def get_records_df(
    names_df: pd.DataFrame,
    person_df: pd.DataFrame,
    groupby_select: str | None = None,
    sort_level: str | None = None,
):
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

    df = df.sort_values(by=["total"] + n_shown_columns, ascending=False).reset_index()

    df.columns = [str(col) for col in df.columns]
    df_p = person_df[["name1", "group1"]]
    df_p = df_p.rename(columns={"name1": "name", "group1": "group"})
    df = pd.merge(df, df_p, how="left", on="name")
    df["group"] = df["group"].fillna("Solo")
    logger.debug(f"df columns: {df.columns}")
    df
    return df


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
