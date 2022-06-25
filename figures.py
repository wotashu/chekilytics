import pandas as pd
import plotly.express as px

from color_map import xkcd_colors


def get_bar_fig(df: pd.DataFrame, **kwargs):
    return px.bar(
        df.sort_values(by="count", ascending=False),
        x="count",
        y="name",
        color="name",
        text="count",
        title=f"結果: {df['count'].sum()}枚数",
        color_discrete_map=xkcd_colors,
    )


def get_pie_fig(df: pd.DataFrame):
    fig = px.pie(
        df.sort_values(by="count", ascending=True),
        names="name",
        values="count",
        color="name",
        color_discrete_map=xkcd_colors,
    )
    fig.update_traces(textposition="inside", textinfo="value+label")
    return fig
