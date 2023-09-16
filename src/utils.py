import pandas as pd
import streamlit as st

import src.munge as munge


def get_cutoff_values(
    df: pd.DataFrame, selected_persons: list[str], max_value: int
) -> pd.DataFrame:
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
        df = munge.get_cutoff_data(df, int(cutoff))
    return df
