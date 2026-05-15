
from __future__ import annotations

import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

from .api_client import fetch_first, result_summary


TEXT_URLS = [
    # 2: Veðurhorfur á landinu, 3: höfuðborgarsvæðið, 5/6 næstu dagar, 9 yfirlit, 31/32/39 regions
    "https://xmlweather.vedur.is/?op_w=xml&type=txt&lang=is&view=xml&ids=2;3;5;6;9;10;31;32;39",
]


@st.cache_data(ttl=900, show_spinner=False)
def get_weather_texts() -> tuple[pd.DataFrame, bool, str]:
    result, attempts = fetch_first(TEXT_URLS, timeout=12)
    rows = []

    if result and result.ok and result.kind == "xml":
        try:
            root = ET.fromstring(result.data)
            for t in root.findall(".//text"):
                rows.append({
                    "title": (t.findtext("title") or "").strip(),
                    "creation": (t.findtext("creation") or "").strip(),
                    "valid_from": (t.findtext("valid_from") or "").strip(),
                    "valid_to": (t.findtext("valid_to") or "").strip(),
                    "content": (t.findtext("content") or "").strip(),
                    "source": result.url,
                })
        except Exception:
            rows = []

    if not rows:
        return pd.DataFrame([]), True, "Textaspár náðust ekki.\n\n" + result_summary(attempts)

    return pd.DataFrame(rows), False, f"Textaspár virkar: {result.url} — {len(rows)} textar."
