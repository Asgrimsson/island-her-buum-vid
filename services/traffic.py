
from __future__ import annotations

import pandas as pd
import streamlit as st

from .api_client import fetch_first, xml_all_rows, result_summary


TRAFFIC_URLS = [
    "https://gagnaveita.vegagerdin.is/api/faerdpunktar2017_1",
    "https://gagnaveita.vegagerdin.is/api/faerd2017_1",
    "http://gagnaveita.vegagerdin.is/api/faerdpunktar2017_1",
    "http://gagnaveita.vegagerdin.is/api/faerd2017_1",
    "https://vegasja.vegagerdin.is/arcgis/rest/services/data/faerd/MapServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&f=json",
]

FALLBACK_TRAFFIC = [
    {"name": "Hellisheiði", "status": "Athuga færð", "lat": 64.037, "lon": -21.402, "severity": "yellow", "source": "fallback"},
    {"name": "Suðurlandsvegur við Selfoss", "status": "Opið / sýnidæmi", "lat": 63.933, "lon": -20.997, "severity": "green", "source": "fallback"},
    {"name": "Víkursvæði", "status": "Fylgjast með veðri", "lat": 63.419, "lon": -19.006, "severity": "yellow", "source": "fallback"},
]

APPROX = {
    "hellisheiði": (64.037, -21.402),
    "hellisheidi": (64.037, -21.402),
    "selfoss": (63.933, -20.997),
    "vík": (63.419, -19.006),
    "vik": (63.419, -19.006),
    "reykjavík": (64.146, -21.942),
    "reykjavik": (64.146, -21.942),
    "þingvellir": (64.255, -21.130),
    "thingvellir": (64.255, -21.130),
    "akureyri": (65.688, -18.126),
    "egilsstaðir": (65.266, -14.394),
    "egilsstadir": (65.266, -14.394),
    "höfn": (64.253, -15.208),
    "hofn": (64.253, -15.208),
    "ísafjörður": (66.074, -23.134),
    "isafjordur": (66.074, -23.134),
    "blönduós": (65.660, -20.280),
    "blonduos": (65.660, -20.280),
}


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


def _severity(status: str) -> str:
    text = str(status).lower()
    if any(x in text for x in ["loka", "ófært", "ofært", "closed", "impassable"]):
        return "red"
    if any(x in text for x in ["hál", "hal", "snjór", "snjor", "þæfing", "thaefing", "varúð", "varud", "athug", "slæmt", "hálka"]):
        return "yellow"
    return "green"


def _approx(name: str):
    text = str(name).lower()
    for key, coords in APPROX.items():
        if key in text:
            return coords
    return None, None


@st.cache_data(ttl=300, show_spinner=False)
def get_traffic() -> tuple[pd.DataFrame, bool, str]:
    result, attempts = fetch_first(TRAFFIC_URLS, timeout=10)

    raw_rows = []
    if result and result.ok:
        if result.kind == "json":
            raw = result.data
            if isinstance(raw, dict) and "features" in raw:
                for f in raw.get("features", [])[:800]:
                    attrs = f.get("attributes", {}) or {}
                    geom = f.get("geometry", {}) or {}
                    lat = lon = None
                    if "x" in geom and "y" in geom:
                        lon, lat = geom["x"], geom["y"]
                    elif "paths" in geom and geom["paths"] and geom["paths"][0]:
                        lon, lat = geom["paths"][0][0][0], geom["paths"][0][0][1]
                    attrs["_lat"] = lat
                    attrs["_lon"] = lon
                    raw_rows.append(attrs)
            elif isinstance(raw, dict):
                raw_rows = raw.get("results") or raw.get("data") or []
            elif isinstance(raw, list):
                raw_rows = raw
        elif result.kind == "xml":
            raw_rows = xml_all_rows(result.data)

    rows = []
    for item in raw_rows[:1000]:
        name = _first(item, ["Nafn", "nafn", "name", "Vegur", "VEGUR", "Vegheiti", "Kafli", "road", "Heiti"], "Færð / vegkafli")
        status = _first(item, ["Ast", "ASTAND", "FAERD", "Lysing", "LYSING", "status", "Faerd", "faerd", "Astand"], "Upplýsingar um færð")
        lat = _first(item, ["Breidd", "breidd", "lat", "latitude", "y", "Y", "_lat"], None)
        lon = _first(item, ["Lengd", "lengd", "lon", "lng", "longitude", "x", "X", "_lon"], None)

        lat = _num(lat, None)
        lon = _num(lon, None)

        if lat is None or lon is None:
            lat, lon = _approx(name)

        if lat is None or lon is None:
            # Keep in table, skip map by assigning blank later? Folium needs coords, so skip map rows.
            continue

        rows.append({
            "name": name,
            "status": status,
            "lat": lat,
            "lon": lon,
            "severity": _severity(status),
            "source": result.url if result else "",
        })

    if not rows:
        msg = "Færðargögn náðust en gátu ekki verið staðsett á korti — sýnidæmi notað.\n\n" + result_summary(attempts)
        return pd.DataFrame(FALLBACK_TRAFFIC), True, msg

    ssl_note = " — SSL fallback notað" if result and not result.verify_ssl else ""
    msg = f"Færðargögn virk: {result.url} — {len(rows)} staðsettir punktar{ssl_note}."
    return pd.DataFrame(rows), False, msg
