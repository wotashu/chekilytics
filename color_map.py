import matplotlib.colors as mcolors


COLOR_DESCRETE_MAP = {
    "Suzy": "red",
    "OTHERS": "grey",
    "七瀬千夏": "red",
    "天音ゆめ": "lavender",
    "恵深あむ": "red",
    "楠木りほ": "cyan",
    "雅春奈": "red",
    "椎名まどか": "cyan",
    "中谷亜優": "white",
    "石田綾音": "fuchsia",
    "濱崎みき": "white",
    "瀬乃悠月": "red",
    "天使 さな": "yellow",
    "のえる": "purple",
    "火野快飛": "azure",
    "メグ・ピッチ・オリオン": "lime",
    "コイヌ フユ": "yellow",
    "涼乃みほ": "cyan",
    "松島朱里": "green",
    "星名 夢音": "lightgreen",
    "雨宮れいな": "white",
    "岬あやめ": "yellow",
    "鳴上綺羅": "cyan",
    "桜衣みゆな": "pink",
    "Joyce": "green",
    "木戸怜緒奈": "cyan",
    "原田真帆": "coral",
    "侑之りせ": "white",
    "南 歩唯": "pink",
    "昊乃ひな": "orange",
    "日向なの": "orange",
    "きゃりー": "yellow",
    "もしかして、るか": "yellow"

}


xkcd_colors = {
    name: mcolors.XKCD_COLORS[f"xkcd:{color_name}"].upper()
    for name, color_name in COLOR_DESCRETE_MAP.items()
}