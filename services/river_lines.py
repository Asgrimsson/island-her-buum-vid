
from __future__ import annotations

import pandas as pd
import streamlit as st


# Approximate teaching geometries, not official hydrographic lines.
# Coordinates are WGS84 lat/lon and designed for classroom map visualization.
RIVER_LINES = [
    {
        "river": "Þjórsá",
        "area": "Suðurland",
        "type": "jökulá / dragá",
        "note": "Kennslulína: frá hálendi til suðurstrandar.",
        "coords": [
            (64.55, -18.55), (64.25, -19.05), (64.05, -19.55),
            (63.92, -20.15), (63.86, -20.65), (63.79, -20.95)
        ],
    },
    {
        "river": "Ölfusá",
        "area": "Suðurland",
        "type": "sameinuð stórá",
        "note": "Rennur við Selfoss til sjávar.",
        "coords": [
            (64.00, -20.95), (63.94, -20.99), (63.90, -21.08),
            (63.85, -21.18), (63.80, -21.25)
        ],
    },
    {
        "river": "Hvítá",
        "area": "Suðurland",
        "type": "jökulá",
        "note": "Kemur frá Langjökli; Gullfoss er í Hvítá.",
        "coords": [
            (64.65, -20.45), (64.48, -20.25), (64.33, -20.12),
            (64.15, -20.35), (64.02, -20.80), (63.98, -20.95)
        ],
    },
    {
        "river": "Sog",
        "area": "Suðurland",
        "type": "lindá / útfall",
        "note": "Rennur úr Þingvallavatni og sameinast Hvítá.",
        "coords": [
            (64.17, -21.05), (64.08, -20.98), (64.02, -20.95), (63.98, -20.95)
        ],
    },
    {
        "river": "Markarfljót",
        "area": "Suðurland",
        "type": "jökulá",
        "note": "Tengist flóðum og jökulhlaupum.",
        "coords": [
            (63.90, -19.25), (63.78, -19.55), (63.68, -20.05), (63.58, -20.25)
        ],
    },
    {
        "river": "Jökulsá á Fjöllum",
        "area": "Norðausturland",
        "type": "jökulá",
        "note": "Dettifoss er í ánni.",
        "coords": [
            (64.55, -16.35), (64.95, -16.45), (65.35, -16.35),
            (65.75, -16.42), (66.05, -16.55)
        ],
    },
    {
        "river": "Skjálfandafljót",
        "area": "Norðurland",
        "type": "jökulá / dragá",
        "note": "Goðafoss er í ánni.",
        "coords": [
            (64.95, -17.75), (65.25, -17.55), (65.55, -17.45), (65.90, -17.35)
        ],
    },
    {
        "river": "Blanda",
        "area": "Norðurland",
        "type": "jökulá",
        "note": "Tengd miðlun og orkuvinnslu.",
        "coords": [
            (64.75, -19.65), (65.05, -19.80), (65.35, -20.05), (65.65, -20.28)
        ],
    },
    {
        "river": "Jökulsá á Dal",
        "area": "Austurland",
        "type": "jökulá",
        "note": "Tengd Kárahnjúkum og Austurlandi.",
        "coords": [
            (64.75, -15.45), (65.05, -15.25), (65.25, -14.95), (65.40, -14.65)
        ],
    },
    {
        "river": "Lagarfljót",
        "area": "Austurland",
        "type": "fljót / stöðuvatnakerfi",
        "note": "Vatnakerfi við Egilsstaði.",
        "coords": [
            (65.35, -14.80), (65.20, -14.72), (65.05, -14.65), (64.90, -14.55)
        ],
    },
]


@st.cache_data(ttl=3600, show_spinner=False)
def get_river_lines() -> pd.DataFrame:
    return pd.DataFrame(RIVER_LINES)
