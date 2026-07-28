"""Palette definitions shared by every generated asset.

One source of truth: the banner, the stats cards and the contribution snake all
read their colours from here, so the profile can't drift out of sync.
"""

PALETTES = {
    # Warm amber on near-black. Editorial, and rare on GitHub — most profiles
    # sit on the same cyan/violet gradient.
    "ember": {
        "label": "Ember",
        "dark": {
            "bg": "#0A0B0E", "panel": "#111318", "panel2": "#15181E",
            "line": "#23262E", "text": "#EDEAE4", "muted": "#8C877D",
            "dim": "#5C594F", "accent": "#E8913A", "accent2": "#C9563C",
            "ok": "#B9A24A",
        },
        "light": {
            "bg": "#FBFAF8", "panel": "#FFFFFF", "panel2": "#F4F2EE",
            "line": "#E2DED6", "text": "#16150F", "muted": "#6B6659",
            "dim": "#8C877D", "accent": "#B4650F", "accent2": "#A33A22",
            "ok": "#7A6A1E",
        },
        # snake: [empty cell, ...ramp], snake body
        "snake_dark": ["#22262E", "#5C4A2E", "#8A6524", "#C07A1E", "#E8913A"],
        "snake_light": ["#EDEAE4", "#F0CFA0", "#E0A860", "#C4791F", "#8A5210"],
        "snake_body_dark": "#C9563C",
        "snake_body_light": "#A33A22",
    },
    # Near-monochrome slate with one electric accent. High contrast, modern.
    "lime": {
        "label": "Slate & Lime",
        "dark": {
            "bg": "#0B0D10", "panel": "#111419", "panel2": "#151920",
            "line": "#242830", "text": "#E8ECEF", "muted": "#828B96",
            "dim": "#575F6A", "accent": "#A3E635", "accent2": "#4ADE80",
            "ok": "#67C7A0",
        },
        "light": {
            "bg": "#FBFCFD", "panel": "#FFFFFF", "panel2": "#F2F4F7",
            "line": "#DFE3E8", "text": "#0D1117", "muted": "#5B646F",
            "dim": "#828B96", "accent": "#4D7C0F", "accent2": "#15803D",
            "ok": "#0F766E",
        },
        "snake_dark": ["#242830", "#3F5320", "#5C7A24", "#83AD2C", "#A3E635"],
        "snake_light": ["#E8ECEF", "#D7E9AC", "#B4D471", "#7FA92E", "#4D7C0F"],
        "snake_body_dark": "#4ADE80",
        "snake_body_light": "#15803D",
    },
    # Deep ink with copper and a cool teal counterweight. Warm/cool balance.
    "copper": {
        "label": "Ink & Copper",
        "dark": {
            "bg": "#090C11", "panel": "#0F141B", "panel2": "#131922",
            "line": "#212934", "text": "#E7EBF0", "muted": "#828E9C",
            "dim": "#57616E", "accent": "#D89A5E", "accent2": "#4FB3A5",
            "ok": "#7FA8C9",
        },
        "light": {
            "bg": "#FBFAF9", "panel": "#FFFFFF", "panel2": "#F2F4F6",
            "line": "#E0E4E9", "text": "#0B1017", "muted": "#5A6673",
            "dim": "#828E9C", "accent": "#9A5A18", "accent2": "#12766B",
            "ok": "#2C5F86",
        },
        "snake_dark": ["#212934", "#4A3A28", "#7A5A32", "#AD7B42", "#D89A5E"],
        "snake_light": ["#E7EBF0", "#EDD3B4", "#D9AC7A", "#B67B39", "#7E4712"],
        "snake_body_dark": "#4FB3A5",
        "snake_body_light": "#12766B",
    },
}


def get(name, mode):
    p = PALETTES[name]
    c = dict(p[mode])
    c["snake_dots"] = p["snake_dark" if mode == "dark" else "snake_light"]
    c["snake_body"] = p["snake_body_dark" if mode == "dark" else "snake_body_light"]
    c["label"] = p["label"]
    return c
