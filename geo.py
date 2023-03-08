import pandas as pd
import pydeck as pdk


def get_map_layer(df: pd.DataFrame, map_type: str):
    if map_type == "column":
        pitch = 50
        layer = pdk.Layer(
            "ColumnLayer",
            data=df,
            get_position="[longitude, latitude]",
            get_elevation="[count]",
            elevation_scale=100,
            elevation_range=[0, 100],
            pickable=True,
            extruded=True,
            on_click=True,
            radius=50,
        )
    if map_type == "scatter":
        pitch = 0
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            opacity=0.5,
            get_position="[longitude, latitude]",
            get_fill_color="[200, 30, 0, 160]",
            get_radius="[count]",
            pickable=True,
            min_radius_pixels=10,
            radiusScale=10,
            max_radius_pixels=200,
            on_click=True,
        )
    if map_type == "heat":
        pitch = 0
        layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            opacity=0.9,
            get_position="[longitude, latitude]",
            get_fill_color="[200, 30, 0, 160]",
            pickable=True,
            min_radius_pixels=10,
            on_click=True,
            get_weight="count",
        )
    return pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=35.678942,
            longitude=139.737892,
            zoom=10,
            pitch=pitch,
        ),
        tooltip={
            "html": "Location:{full_address}, count: {count}",
        },
        layers=[layer],
    )
