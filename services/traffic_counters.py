
from __future__ import annotations

from io import StringIO
import re
from typing import Any

import pandas as pd
import requests
import streamlit as st

try:
    from pyproj import Transformer
    ISN93_TO_WGS84 = Transformer.from_crs("EPSG:3057", "EPSG:4326", always_xy=True)
except Exception:
    ISN93_TO_WGS84 = None


# Vegagerðin documents this WFS layer for traffic counters.
# It is "near realtime" / frequently updated depending on counter type.
WFS_URLS = [
    "https://gagnaveita.vegagerdin.is/geoserver/gis/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=gis:umferdvika_2021_1&outputFormat=application/json&srsName=EPSG:4326",
    "https://gagnaveita.vegagerdin.is/geoserver/gis/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=gis:umferdvika_2021_1&outputFormat=json&srsName=EPSG:4326",
    "https://gagnaveita.vegagerdin.is/geoserver/gis/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=gis:umferdvika_2021_1&outputFormat=application/json&srsName=EPSG:4326",
    "https://gagnaveita.vegagerdin.is/geoserver/gis/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=gis:umferdvika_2021_1&outputFormat=json",
]

FALLBACK_COUNTERS = [
    {
        "name": "Selfoss / Suðurlandsvegur", "road": "1", "region": "Suðurland",
        "lat": 63.94, "lon": -20.99, "umf_15min": 18, "umf_i_dag": 420, "umf_dagur1": 2688,
        "umf_dagur2": 2410, "umf_dagur3": 2325, "umf_dagur4": 2510, "umf_dagur5": 2700, "umf_dagur6": 2860, "umf_dagur7": 2605,
        "medalhradi_15min": 72, "latest_time": "sýnidæmi", "direction": "Samanlögð umferð", "station_type": "sýnidæmi",
        "traffic_value": 420, "traffic_label": "Í dag: 420", "traffic_period": "frá miðnætti", "traffic_field": "UMF_I_DAG", "source": "fallback"
    },
    {
        "name": "Hellisheiði", "road": "1", "region": "Suðurland",
        "lat": 64.03, "lon": -21.36, "umf_15min": 11, "umf_i_dag": 310, "umf_dagur1": 1783,
        "umf_dagur2": 1905, "umf_dagur3": 2051, "umf_dagur4": 1740, "umf_dagur5": 2200, "umf_dagur6": 2320, "umf_dagur7": 2100,
        "medalhradi_15min": 84, "latest_time": "sýnidæmi", "direction": "Samanlögð umferð", "station_type": "sýnidæmi",
        "traffic_value": 310, "traffic_label": "Í dag: 310", "traffic_period": "frá miðnætti", "traffic_field": "UMF_I_DAG", "source": "fallback"
    },
    {
        "name": "Hringvegur við Borgarnes", "road": "1", "region": "Vesturland",
        "lat": 64.54, "lon": -21.92, "umf_15min": 9, "umf_i_dag": 260, "umf_dagur1": 6600,
        "umf_dagur2": 6100, "umf_dagur3": 5900, "umf_dagur4": 6300, "umf_dagur5": 6500, "umf_dagur6": 6800, "umf_dagur7": 6000,
        "medalhradi_15min": 78, "latest_time": "sýnidæmi", "direction": "Samanlögð umferð", "station_type": "sýnidæmi",
        "traffic_value": 260, "traffic_label": "Í dag: 260", "traffic_period": "frá miðnætti", "traffic_field": "UMF_I_DAG", "source": "fallback"
    },
    {
        "name": "Akureyri / Eyjafjörður", "road": "1", "region": "Norðurland",
        "lat": 65.69, "lon": -18.13, "umf_15min": 7, "umf_i_dag": 220, "umf_dagur1": 1450,
        "umf_dagur2": 1510, "umf_dagur3": 1390, "umf_dagur4": 1600, "umf_dagur5": 1700, "umf_dagur6": 1820, "umf_dagur7": 1550,
        "medalhradi_15min": 65, "latest_time": "sýnidæmi", "direction": "Samanlögð umferð", "station_type": "sýnidæmi",
        "traffic_value": 220, "traffic_label": "Í dag: 220", "traffic_period": "frá miðnætti", "traffic_field": "UMF_I_DAG", "source": "fallback"
    },
    {
        "name": "Reykjanesbraut / Keflavík", "road": "41", "region": "Suðurnes",
        "lat": 63.99, "lon": -22.55, "umf_15min": 16, "umf_i_dag": 380, "umf_dagur1": 4100,
        "umf_dagur2": 3900, "umf_dagur3": 4050, "umf_dagur4": 4300, "umf_dagur5": 4500, "umf_dagur6": 4700, "umf_dagur7": 4200,
        "medalhradi_15min": 82, "latest_time": "sýnidæmi", "direction": "Samanlögð umferð", "station_type": "sýnidæmi",
        "traffic_value": 380, "traffic_label": "Í dag: 380", "traffic_period": "frá miðnætti", "traffic_field": "UMF_I_DAG", "source": "fallback"
    },
]


def _num(value, default=None):
    try:
        if value in [None, ""]:
            return default
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def _flatten_feature(feature: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties") or {}
    geom = feature.get("geometry") or {}
    row = dict(props)

    coords = geom.get("coordinates")

    # GeoJSON can be Point [x,y] or occasionally nested.
    if isinstance(coords, list) and coords and isinstance(coords[0], list):
        coords = coords[0]

    if isinstance(coords, list) and len(coords) >= 2:
        x = _num(coords[0])
        y = _num(coords[1])

        # WGS84 lon,lat
        if y is not None and x is not None and 62 <= y <= 68 and -26 <= x <= -12:
            row["lat"] = y
            row["lon"] = x

        # WGS84 lat,lon reversed
        elif x is not None and y is not None and 62 <= x <= 68 and -26 <= y <= -12:
            row["lat"] = x
            row["lon"] = y

        # ISN93 coordinates, if GeoServer ignores requested projection.
        elif ISN93_TO_WGS84 is not None and x is not None and y is not None:
            try:
                lon, lat = ISN93_TO_WGS84.transform(x, y)
                if 62 <= lat <= 68 and -26 <= lon <= -12:
                    row["lat"] = lat
                    row["lon"] = lon
            except Exception:
                pass

    return row


def _guess_col(df: pd.DataFrame, candidates: list[str]):
    lowered = {str(c).lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lowered:
            return lowered[c.lower()]
    for c in df.columns:
        low = str(c).lower()
        if any(k.lower() in low for k in candidates):
            return c
    return None


def _field_value(row: pd.Series, names: list[str], default=None):
    lowered = {str(k).lower(): k for k in row.index}
    for name in names:
        key = lowered.get(name.lower())
        if key is not None:
            val = row.get(key)
            if val not in [None, "", "nan"]:
                return val
    return default


def _field_num(row: pd.Series, names: list[str], default=None):
    return _num(_field_value(row, names, default), default)


def _is_missing(value) -> bool:
    try:
        return value is None or value == "" or str(value).lower() in ["nan", "nat", "none"]
    except Exception:
        return True


def _safe_int_label(value, prefix: str = "", suffix: str = "") -> str:
    try:
        if _is_missing(value):
            return "—"
        number = float(value)
        if pd.isna(number):
            return "—"
        return f"{prefix}{int(number):,}{suffix}".replace(",", ".")
    except Exception:
        return "—"


def _safe_float_value(value, default=0):
    try:
        if _is_missing(value):
            return default
        number = float(value)
        if pd.isna(number):
            return default
        return number
    except Exception:
        return default


def _format_datetime(value):
    if value in [None, "", "nan"]:
        return ""
    text = str(value)
    try:
        dt = pd.to_datetime(value, errors="coerce")
        if pd.notna(dt):
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass
    return text


def _station_type(value):
    try:
        n = int(float(value))
        return {1: "Veðurstöð með umferðarteljara", 2: "Umferðarteljari", 4: "Umferðargreinir"}.get(n, str(value))
    except Exception:
        return str(value or "")


def _direction_text(value):
    if value in [None, "", "nan"]:
        return ""
    return str(value)


def _traffic_value_from_row(row: pd.Series):
    # Look for likely count columns. The exact schema can vary.
    candidates = [
        "fjoldi", "fjöldi", "umferð", "umferd", "traffic", "count",
        "fjoldi15min", "fjoldi_15min", "fjoldi_dag", "f_dag", "dagur", "summa", "heild", "magn", "vehicles", "cars",
        "klst", "hour", "samtals", "total"
    ]
    best_key = ""
    best_val = None

    for key in row.index:
        low = str(key).lower()
        if any(c in low for c in candidates):
            val = _num(row.get(key))
            if val is not None:
                if best_val is None or val > best_val:
                    best_val = val
                    best_key = str(key)

    return best_key, best_val


def _normalize_rows(raw: Any, source_url: str) -> pd.DataFrame:
    rows = []

    if isinstance(raw, dict) and "features" in raw:
        rows = [_flatten_feature(f) for f in raw.get("features", [])]
    elif isinstance(raw, list):
        rows = raw

    if not rows:
        return pd.DataFrame([])

    df = pd.DataFrame(rows)

    name_col = _guess_col(df, ["nafn", "name", "stod", "stöð", "station", "stadur", "staður"])
    road_col = _guess_col(df, ["vegur", "vegnr", "road", "veg"])
    region_col = _guess_col(df, ["landshluti", "svaedi", "svæði", "region"])
    lat_col = _guess_col(df, ["lat", "latitude", "breidd"])
    lon_col = _guess_col(df, ["lon", "lng", "longitude", "lengd"])

    out = []
    for _, row in df.iterrows():
        traffic_key, traffic_val = _traffic_value_from_row(row)

        name = str(row.get(name_col, "")) if name_col else ""
        road = str(row.get(road_col, "")) if road_col else ""
        region = str(row.get(region_col, "")) if region_col else ""

        if not name or name.lower() == "nan":
            name = f"Umferðarteljari {len(out)+1}"

        lat = _num(row.get(lat_col)) if lat_col else _num(row.get("lat"))
        lon = _num(row.get(lon_col)) if lon_col else _num(row.get("lon"))

        # Some geoserver layers can be in ISN93 if not outputFormat=json. In that case lat/lon won't pass.
        has_coords = lat is not None and lon is not None and 62 <= lat <= 68 and -26 <= lon <= -12

        umf_15min = _field_num(row, ["UMF_15MIN", "umf_15min"], None)
        speed_15min = _field_num(row, ["MEDALHRADI_15MIN", "medalhradi_15min"], None)
        umf_i_dag = _field_num(row, ["UMF_I_DAG", "umf_i_dag"], None)
        latest_time = _format_datetime(_field_value(row, ["DAGS_SIDUSTUGAGNA", "dags_sidustugagna"], ""))
        direction = _direction_text(_field_value(row, ["STEFNA", "stefna"], ""))
        station_type = _station_type(_field_value(row, ["MAELISTOD_TEGUND", "maelistod_tegund"], ""))

        daily = {}
        daily_dates = {}
        for i in range(1, 8):
            daily[f"umf_dagur{i}"] = _field_num(row, [f"UMF_DAGUR{i}", f"umf_dagur{i}"], None)
            daily_dates[f"dags_dagur{i}"] = _format_datetime(_field_value(row, [f"DAGS_DAGUR{i}", f"dags_dagur{i}"], ""))

        # Main map label should be explicit. Prefer current day from midnight,
        # then 15 min, then yesterday. NaN values are treated as missing.
        if not _is_missing(umf_i_dag):
            main_val = _safe_float_value(umf_i_dag)
            main_field = "UMF_I_DAG"
            main_period = "frá miðnætti að síðustu uppfærslu"
            main_label = _safe_int_label(main_val, "Í dag: ")
        elif not _is_missing(umf_15min):
            main_val = _safe_float_value(umf_15min)
            main_field = "UMF_15MIN"
            main_period = "síðustu 15 mínútur"
            main_label = _safe_int_label(main_val, "15 mín: ")
        elif not _is_missing(daily.get("umf_dagur1")):
            main_val = _safe_float_value(daily.get("umf_dagur1"))
            main_field = "UMF_DAGUR1"
            main_period = "í gær"
            main_label = _safe_int_label(main_val, "Í gær: ")
        else:
            main_val = _safe_float_value(traffic_val, 0)
            main_field = traffic_key
            main_period = "óþekkt tímabil"
            main_label = _safe_int_label(main_val) if main_val else "—"

        out.append({
            "name": name,
            "road": road if road.lower() != "nan" else "",
            "region": region if region.lower() != "nan" else "",
            "lat": lat if has_coords else None,
            "lon": lon if has_coords else None,
            "umf_15min": umf_15min,
            "medalhradi_15min": speed_15min,
            "umf_i_dag": umf_i_dag,
            "latest_time": latest_time,
            "direction": direction,
            "station_type": station_type,
            **daily,
            **daily_dates,
            "traffic_value": main_val if main_val is not None else 0,
            "traffic_field": main_field,
            "traffic_period": main_period,
            "traffic_label": main_label,
            "source": source_url,
        })

    return pd.DataFrame(out)


def _fetch_json_or_text(url: str):
    r = requests.get(url, timeout=18, headers={"User-Agent": "Island-her-buum-vid/4.1"})
    r.raise_for_status()
    ctype = r.headers.get("content-type", "").lower()
    text = r.text

    if "json" in ctype or text.strip().startswith("{"):
        return r.json()

    # Very rough GML fallback: return empty; UI keeps fallback rather than breaking.
    return None


@st.cache_data(ttl=900, show_spinner=False)
def get_traffic_counters() -> tuple[pd.DataFrame, bool, str]:
    attempts = []

    for url in WFS_URLS:
        try:
            raw = _fetch_json_or_text(url)
            df = _normalize_rows(raw, url)
            if not df.empty:
                coord_count = int(df[["lat", "lon"]].notna().all(axis=1).sum()) if {"lat", "lon"}.issubset(df.columns) else 0
                total = int(pd.to_numeric(df["traffic_value"], errors="coerce").fillna(0).sum()) if "traffic_value" in df.columns else 0
                msg = f"Umferðarteljarar virkir: {url} — {len(df)} teljarar, {coord_count} með hnit, samtala mæligilda {total}."
                return df, False, msg
        except Exception as e:
            attempts.append(f"{url} — {e}")

    msg = "Umferðarteljarar náðust ekki úr WFS í þessari keyrslu — sýnidæmi notað.\n\n" + "\n".join(attempts)
    return pd.DataFrame(FALLBACK_COUNTERS), True, msg
