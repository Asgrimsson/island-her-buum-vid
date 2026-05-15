
from __future__ import annotations

import pandas as pd
import streamlit as st

from .api_client import fetch_first, xml_all_rows, result_summary


CAMERA_URLS = [
    "https://gagnaveita.vegagerdin.is/api/vefmyndavelar2014_1",
    "http://gagnaveita.vegagerdin.is/api/vefmyndavelar2014_1",
]

FALLBACK_CAMERAS = [
    {"name": "Selfoss / Suðurlandsvegur", "lat": 63.933, "lon": -20.997, "image": "", "road": "Hringvegur"},
    {"name": "Hellisheiði", "lat": 64.037, "lon": -21.402, "image": "", "road": "Hringvegur"},
    {"name": "Vík í Mýrdal", "lat": 63.419, "lon": -19.006, "image": "", "road": "Hringvegur"},
    {"name": "Hvolsvöllur", "lat": 63.753, "lon": -20.224, "image": "", "road": "Hringvegur"},
    {"name": "Reykjavík", "lat": 64.146, "lon": -21.942, "image": "", "road": "Höfuðborgarsvæði"},
]


def _first(item: dict, keys: list[str], default=""):
    for key in keys:
        if key in item and item[key] not in [None, ""]:
            return item[key]
    return default


def _num(value, default=None):
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def _normalize(item: dict) -> dict:
    return {
        "name": _first(item, ["Nafn", "nafn", "name", "Stod", "stod", "Heiti", "Name"], "Vefmyndavél"),
        "lat": _first(item, ["Breidd", "breidd", "lat", "latitude", "y", "Y"], None),
        "lon": _first(item, ["Lengd", "lengd", "lon", "lng", "longitude", "x", "X"], None),
        "image": _first(item, ["Slod", "slod", "Mynd", "mynd", "image", "url", "Url", "URL"], ""),
        "road": _first(item, ["Vegheiti", "vegheiti", "road", "Vegur"], ""),
    }


@st.cache_data(ttl=300, show_spinner=False)
def get_cameras() -> tuple[pd.DataFrame, bool, str]:
    result, attempts = fetch_first(CAMERA_URLS, timeout=10)

    rows = []
    if result and result.ok:
        if result.kind == "json":
            raw = result.data
            if isinstance(raw, list):
                rows = raw
            elif isinstance(raw, dict):
                rows = raw.get("results") or raw.get("data") or raw.get("features") or []
        elif result.kind == "xml":
            rows = xml_all_rows(result.data)

    normalized = []
    for item in rows:
        if isinstance(item, dict) and "attributes" in item and isinstance(item["attributes"], dict):
            item = item["attributes"]
        cam = _normalize(item)
        cam["lat"] = _num(cam["lat"], None)
        cam["lon"] = _num(cam["lon"], None)
        if cam["lat"] is not None and cam["lon"] is not None:
            normalized.append(cam)

    if not normalized:
        msg = "Myndavélagögn náðust ekki — sýnidæmi notað.\n\n" + result_summary(attempts)
        return pd.DataFrame(FALLBACK_CAMERAS), True, msg

    msg = f"Myndavélagögn virk: {result.url} — {len(normalized)} myndavélar."
    return pd.DataFrame(normalized), False, msg
