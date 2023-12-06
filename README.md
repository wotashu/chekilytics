# Chekilytics

A personal project for visualizing my personal collection of idol cheki pictures.

チェキを管理する個人アプリ。

## Motivation

The current work has been on the visualization of various metrics relating to the provenance of each cheki, and to grow my personal skills during my free time.

私用の趣味を分かるように、技術能力を磨くために。

## Technologies

* Poetry
* Streamlit
* Plotly
* Mapbox
* GCP
* Pandas
* Pydantic

### Dev dependencies

* Ruff
* Mypy
* Black
* Pytest

## Secrets

Add a [secrets file](https://docs.streamlit.io/library/advanced-features/secrets-management).

The application currently wants credentials for GCP and mapbox.

## Startup

Use poetry to generate the virtual environment.

```bash
poetry install && poetry shell
```

Then begin the streamlit application.

```bash
streamlit run streamlit_app.py
```

## Future roadmap

* Migrate out of google sheets, or improve the ETL processes to accept data from more sources.
* Add integration with actual pictures of the cheki in cloud storage.
* Better maintenance of metadata.
* 日本語
* Data input through interface.
