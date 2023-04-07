import pandas as pd
import plotly.express as px

from color_map import xkcd_colors


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


def get_tree_map(df: pd.DataFrame):
    fig = px.treemap(
        data_frame=df.sort_values(by="total", ascending=False),
        names="name",
        values="total",
        color="name",
        color_discrete_map=xkcd_colors,
    )
