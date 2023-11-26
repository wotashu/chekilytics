import numpy as np
import src.munge as munge
import streamlit as st
from src.loaders import get_datetime_cols, get_worksheet, get_worksheet_location
from src.tabs import get_cheki_tab, get_name_tab


def main():
    sheet_url = st.secrets["private_gsheets_url"]
    cheki_df = get_worksheet(sheet_url, 0)
    dated_cheki_df = get_datetime_cols(cheki_df)
    names_df = munge.group_cheki_by_name(dated_cheki_df)
    person_df = get_worksheet(sheet_url, 1)
    venue_df = get_worksheet_location(sheet_url, 3)

    col1, col2 = st.columns(2)

    with col1:
        date_range = munge.get_dates(names_df)
        st.write(f"Selected dates are {date_range[0]} - {date_range[1]}")

    with col2:
        all_persons = munge.get_all_names(person_df)
        selected_persons = st.multiselect(
            "Search for a name", np.insert(all_persons, 0, "")
        )
        if selected_persons:
            st.write(f"Selected {selected_persons}")
        else:
            st.write("No names selected.")

    names_df = names_df[names_df.date.between(date_range[0], date_range[1])]

    name_tab, cheki_tab = st.tabs(["💃name", "🎴cheki"])

    with name_tab:
        get_name_tab(
            names_df=names_df, person_df=person_df, selected_persons=selected_persons
        )

    with cheki_tab:
        get_cheki_tab(
            first_date=date_range[0],
            last_date=date_range[1],
            venue_df=venue_df,
            selected_persons=selected_persons,
            dated_cheki_df=dated_cheki_df,
        )

    st.write(f"Total values: {len(dated_cheki_df)}")


if __name__ == "__main__":
    main()
