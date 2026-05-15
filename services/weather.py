
from __future__ import annotations

import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

from .api_client import fetch_first, result_summary


# Official IMO XML weather observations.
# ids = common stations across Iceland.
STATIONS = {
    "1": ("Reykjavík", 64.1466, -21.9426),
    "422": ("Akureyri", 65.6885, -18.1262),
    "990": ("Keflavíkurflugvöllur", 63.9850, -22.6056),
    "6208": ("Selfoss", 63.9331, -20.9971),
    "6015": ("Vestmannaeyjar", 63.4427, -20.2734),
    "4472": ("Bjargtangar", 65.5030, -24.5310),
    "2631": ("Flateyri", 66.0530, -23.5160),
    "3976": ("Grímsey", 66.5450, -18.0173),
    "4271": ("Egilsstaðir", 65.2669, -14.3948),
    "5544": ("Höfn í Hornafirði", 64.2539, -15.2082),
    "1596": ("Þingvellir", 64.2559, -21.1297),
    "7475": ("Reykjanesbraut", 63.9710, -22.5330),
}

IDS = ";".join(STATIONS.keys())

WEATHER_URLS = [
    f"https://xmlweather.vedur.is/?op_w=xml&type=obs&lang=is&view=xml&ids={IDS}&params=T;D;F;FX;FG;W;P;RH;R;V&time=1h&anytime=1",
    f"https://xmlweather.vedur.is/?op_w=xml&type=obs&lang=en&view=xml&ids={IDS}&params=T;D;F;FX;FG;W;P;RH;R;V&time=1h&anytime=1",
    # APIs.is kept last only.
    "https://apis.is/weather/observations/is",
    "http://apis.is/weather/observations/is",
]

FALLBACK_WEATHER = [
    {"station": "Reykjavík", "lat": 64.1466, "lon": -21.9426, "temp": 5.0, "wind": 7.0, "desc": "Sýnidæmi", "time": "", "source": "fallback"},
    {"station": "Selfoss", "lat": 63.9331, "lon": -20.9971, "temp": 4.0, "wind": 6.0, "desc": "Sýnidæmi", "time": "", "source": "fallback"},
    {"station": "Akureyri", "lat": 65.6885, "lon": -18.1262, "temp": 3.0, "wind": 5.0, "desc": "Sýnidæmi", "time": "", "source": "fallback"},
]


def _num(value, default=None):
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def _text(node, tag, default=""):
    found = node.find(tag)
    return (found.text or "").strip() if found is not None and found.text is not None else default


def _parse_imo_xml(xml_text: str, source_url: str) -> list[dict]:
    rows = []
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return rows

    for station_node in root.findall(".//station"):
        sid = station_node.attrib.get("id", "")
        default_name, lat, lon = STATIONS.get(sid, ("Veðurstöð", None, None))
        name = _text(station_node, "name", default_name)

        rows.append({
            "station": name,
            "lat": lat,
            "lon": lon,
            "temp": _num(_text(station_node, "T", "")),
            "wind": _num(_text(station_node, "F", "")),
            "wind_dir": _text(station_node, "D", ""),
            "gust": _num(_text(station_node, "FG", "")),
            "max_wind": _num(_text(station_node, "FX", "")),
            "desc": _text(station_node, "W", ""),
            "pressure": _num(_text(station_node, "P", "")),
            "humidity": _num(_text(station_node, "RH", "")),
            "rain": _num(_text(station_node, "R", "")),
            "visibility": _text(station_node, "V", ""),
            "time": _text(station_node, "time", ""),
            "valid": station_node.attrib.get("valid", ""),
            "source": source_url,
        })
    return rows


@st.cache_data(ttl=600, show_spinner=False)
def get_weather() -> tuple[pd.DataFrame, bool, str]:
    result, attempts = fetch_first(WEATHER_URLS, timeout=12)
    normalized = []

    if result and result.ok:
        if result.kind == "xml":
            normalized = _parse_imo_xml(result.data, result.url)

        elif result.kind == "json":
            raw = result.data
            if isinstance(raw, dict):
                rows = raw.get("results") or raw.get("data") or []
            elif isinstance(raw, list):
                rows = raw
            else:
                rows = []

            for item in rows:
                station = item.get("name") or item.get("station") or "Veðurstöð"
                normalized.append({
                    "station": station,
                    "lat": _num(item.get("lat") or item.get("latitude")),
                    "lon": _num(item.get("lon") or item.get("longitude")),
                    "temp": item.get("T") or item.get("temp") or item.get("temperature"),
                    "wind": item.get("F") or item.get("windSpeed") or item.get("wind"),
                    "desc": item.get("W") or item.get("description") or "",
                    "time": item.get("time") or "",
                    "source": result.url,
                })

    # Use only stations that have coords and at least some measurement.
    normalized = [
        w for w in normalized
        if w.get("lat") is not None and w.get("lon") is not None
    ]

    if not normalized:
        msg = "Veðurgögn náðust ekki — sýnidæmi notað.\n\n" + result_summary(attempts)
        return pd.DataFrame(FALLBACK_WEATHER), True, msg

    df = pd.DataFrame(normalized)
    ssl_note = " — SSL fallback notað" if result and not result.verify_ssl else ""
    msg = f"Veðurgögn virk: {result.url} — {len(df)} veðurstöðvar{ssl_note}."
    return df, False, msg
