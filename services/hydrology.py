
from __future__ import annotations

import pandas as pd
import streamlit as st

from .api_client import fetch_url, result_summary


try:
    from pyproj import Transformer
    ISN93_TO_WGS84 = Transformer.from_crs("EPSG:3057", "EPSG:4326", always_xy=True)
except Exception:
    ISN93_TO_WGS84 = None


VHM_URLS = [
    # Layer 1: VHM in operation, layer 4: places, layer 5: single discharge measurements.
    "https://luk.vedur.is/arcgis/rest/services/stadir_vhm/stadir_vhm_isn93/MapServer/1/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
    "https://luk.vedur.is/arcgis/rest/services/stadir_vhm/stadir_vhm_isn93/MapServer/1/query?where=1%3D1&outFields=*&returnGeometry=true&f=pjson",
    "https://luk.vedur.is/arcgis/rest/services/stadir_vhm/stadir_vhm_isn93/MapServer/4/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
    "https://luk.vedur.is/arcgis/rest/services/stadir_vhm/stadir_vhm_isn93/MapServer/5/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
]

MAJOR_RIVERS = [
    {"river": "Þjórsá", "area": "Suðurland", "type": "jökulá / dragá", "lat": 63.88, "lon": -20.65, "note": "Lengsta á Íslands; mikilvæg fyrir orkuvinnslu og vatnafræði."},
    {"river": "Ölfusá", "area": "Suðurland", "type": "sameinuð stórá", "lat": 63.94, "lon": -21.00, "note": "Myndast þar sem Hvítá og Sog renna saman; rennur við Selfoss."},
    {"river": "Hvítá", "area": "Suðurland", "type": "jökulá", "lat": 64.33, "lon": -20.12, "note": "Kemur frá Langjökli; Gullfoss er í Hvítá."},
    {"river": "Sog", "area": "Suðurland", "type": "lindá / útfall", "lat": 64.08, "lon": -20.98, "note": "Rennur úr Þingvallavatni og sameinast Hvítá."},
    {"river": "Jökulsá á Fjöllum", "area": "Norðausturland", "type": "jökulá", "lat": 65.81, "lon": -16.40, "note": "Rennur frá Vatnajökli; Dettifoss er í ánni."},
    {"river": "Skjálfandafljót", "area": "Norðurland", "type": "jökulá / dragá", "lat": 65.68, "lon": -17.55, "note": "Goðafoss er í Skjálfandafljóti."},
    {"river": "Blanda", "area": "Norðurland", "type": "jökulá", "lat": 65.65, "lon": -20.30, "note": "Mikilvæg á í Húnavatnssýslu; tengd miðlun og orkuvinnslu."},
    {"river": "Héraðsvötn", "area": "Norðurland", "type": "jökulár", "lat": 65.72, "lon": -19.45, "note": "Mynduð af Austari- og Vestari-Jökulsá."},
    {"river": "Jökulsá á Dal", "area": "Austurland", "type": "jökulá", "lat": 65.27, "lon": -14.53, "note": "Stór jökulá á Austurlandi; tengd Kárahnjúkavirkjun."},
    {"river": "Lagarfljót", "area": "Austurland", "type": "fljót / stöðuvatnakerfi", "lat": 65.17, "lon": -14.72, "note": "Vatnakerfi við Egilsstaði; þekkt úr þjóðsögum og náttúrufræði."},
    {"river": "Markarfljót", "area": "Suðurland", "type": "jökulá", "lat": 63.68, "lon": -20.08, "note": "Getur tengst jökulhlaupum og flóðahættu frá Mýrdalsjökli/Eyjafjallajökli."},
    {"river": "Skeiðará", "area": "Suðausturland", "type": "jökulá", "lat": 63.98, "lon": -17.05, "note": "Þekkt fyrir jökulhlaup á Skeiðarársandi."},
]


def _num(value, default=None):
    try:
        if value in [None, ""]:
            return default
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def _plausible(lat, lon):
    try:
        return 62 <= float(lat) <= 68 and -26 <= float(lon) <= -12
    except Exception:
        return False


def _transform(x, y):
    x = _num(x); y = _num(y)
    if x is None or y is None:
        return None, None
    if _plausible(y, x):
        return y, x
    if _plausible(x, y):
        return x, y
    if ISN93_TO_WGS84:
        try:
            lon, lat = ISN93_TO_WGS84.transform(x, y)
            if _plausible(lat, lon):
                return lat, lon
        except Exception:
            pass
    return None, None


def _name(attrs):
    for key in ["NAFN", "Nafn", "nafn", "NAME", "name", "HEITI", "Heiti", "STADUR", "Stadur"]:
        if attrs.get(key):
            return attrs.get(key)
    for k, v in attrs.items():
        if "nafn" in str(k).lower() or "heiti" in str(k).lower():
            return v
    return "Vatnamælistöð"


def _parse_features(raw, source_url):
    out = []
    for f in raw.get("features", []):
        attrs = f.get("attributes") or {}
        geom = f.get("geometry") or {}
        x = geom.get("x")
        y = geom.get("y")
        lat, lon = _transform(x, y)
        if lat is None or lon is None:
            continue
        row = {str(k): v for k, v in attrs.items()}
        row["station"] = _name(attrs)
        row["lat"] = lat
        row["lon"] = lon
        row["source"] = source_url
        out.append(row)
    return out


@st.cache_data(ttl=900, show_spinner=False)
def get_hydrology() -> tuple[pd.DataFrame, pd.DataFrame, bool, str]:
    attempts = []
    river_df = pd.DataFrame(MAJOR_RIVERS)

    for url in VHM_URLS:
        result = fetch_url(url, timeout=12, verify_ssl=True)
        attempts.append(result)
        if not result.ok:
            continue
        raw = result.data
        if isinstance(raw, dict) and "features" in raw:
            rows = _parse_features(raw, result.url)
            if rows:
                df = pd.DataFrame(rows).drop_duplicates(subset=["lat", "lon", "station"], keep="first")
                return df, river_df, False, f"Vatnamælistöðvar virkar: {result.url} — {len(df)} stöðvar."

    return pd.DataFrame([]), river_df, True, (
        "Tókst ekki að sækja vatnamælistöðvar úr LUK ArcGIS í þessari keyrslu. "
        "Kerfið notar áfram fræðslutöflu um helstu ár landsins.\n\n" + result_summary(attempts)
    )
