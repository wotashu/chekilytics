import pandas as pd
import plotly.express as px

from src.color_map import xkcd_colors


def get_bar_fig(df: pd.DataFrame, **kwargs):
    return px.bar(
        df.sort_values(by="total", ascending=False),
        x="total",
        y="name",
        color="name",
        text="total",
        title=f"結果: {df['total'].sum()}枚数",
        color_discrete_map=xkcd_colors,
    )


def get_pie_fig(df: pd.DataFrame):
    fig = px.pie(
        df.sort_values(by="total", ascending=True),
        names="name",
        values="total",
        color="name",
        color_discrete_map=xkcd_colors,
    )
    fig.update_traces(textposition="inside", textinfo="value+label")
    return fig


def get_treemap_fig(df: pd.DataFrame, use_groups: bool = True):
    groupby_paths = ["name"]
    if use_groups:
        groupby_paths = ["group", "name"]
    return px.treemap(
        data_frame=df,
        path=groupby_paths,
        values="total",
        color="name",
        color_discrete_map=xkcd_colors,
    )
