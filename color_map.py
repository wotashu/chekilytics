import matplotlib.colors as mcolors


COLOR_DESCRETE_MAP = {
    "Suzy": "red",
    "OTHERS": "grey",
    "七瀬千夏": "red",
    "天音ゆめ": "lavender",
    "恵深あむ": "yellow",
    "楠木りほ": "cyan",
    "大西春菜": "blue",
    "椎名まどか": "cyan",
    "中谷亜優": "white",
    "石田綾音": "fuchsia",
    "濱崎みき": "white",
    "瀬乃悠月": "crimson",
    "望月紗奈": "pink",
    "音羽のあ": "blue",
    "火野快飛": "azure",
    "メグ・ピッチ・オリオン": "lime",
    "コイヌ フユ": "yellow",
    "涼乃みほ": "lightblue",
    "松島朱里": "green",
    "星名 夢音": "lightgreen",
    "雨宮れいな": "white",
    "岬あやめ": "yellow",
    "鳴上綺羅": "lightblue",
    "桜衣みゆな": "pink",
    "Joyce": "green",
    "木戸怜緒奈": "cyan",
    "原田真帆": "coral",
    "侑之りせ": "white",
    "南 歩唯": "pink",
    "昊乃ひな": "orange",
    "日向なの": "orange",
    "きゃりー": "yellow"
}


xkcd_colors = {
    name: mcolors.XKCD_COLORS[f"xkcd:{color_name}"].upper()
    for name, color_name in COLOR_DESCRETE_MAP.items()
}