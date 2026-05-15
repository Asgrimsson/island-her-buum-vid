
from __future__ import annotations

import pandas as pd
import streamlit as st

from .api_client import fetch_url, result_summary


LATEST_URL = "https://api.ust.is/aq/a/getLatest"
STATIONS_URL = "https://api.ust.is/aq/a/getStations"


def _as_rows(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ["results", "data", "items", "stations", "measurements", "values"]:
            if isinstance(raw.get(key), list):
                return raw.get(key)
        if raw and all(isinstance(v, dict) for v in raw.values()):
            rows = []
            for key, value in raw.items():
                row = dict(value)
                row.setdefault("station_key", key)
                rows.append(row)
            return rows
    return []


def _flatten(item: dict, prefix: str = "") -> dict:
    row = {}
    for k, v in item.items():
        key = f"{prefix}{k}" if not prefix else f"{prefix}_{k}"
        if isinstance(v, dict):
            row.update(_flatten(v, key))
        else:
            row[key] = v
    return row


def _first(row: dict, candidates: list[str], default=""):
    lowered = {str(k).lower(): v for k, v in row.items()}
    for c in candidates:
        if c in row and row[c] not in [None, ""]:
            return row[c]
        v = lowered.get(c.lower())
        if v not in [None, ""]:
            return v
    # fuzzy contains
    for k, v in row.items():
        lk = str(k).lower()
        if any(c.lower() in lk for c in candidates) and v not in [None, ""]:
            return v
    return default


def _num(value, default=None):
    try:
        if value in [None, ""]:
            return default
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def _norm_id(row):
    return str(_first(row, ["local_id", "localId", "station_id", "stationId", "id", "ID", "station_key"], "")).strip()


def _station_name(row):
    return _first(row, ["station", "name", "Name", "locality", "Locality", "station_name", "municipality"], "Loftgæðamælir")


def _lat_lon(row):
    lat = _num(_first(row, ["lat", "latitude", "Latitude", "breidd", "gps_lat", "location_lat", "station_latitude"], None))
    lon = _num(_first(row, ["lon", "lng", "longitude", "Longitude", "lengd", "gps_lon", "location_lon", "station_longitude"], None))

    # Some APIs use x/y for lon/lat.
    if lat is None or lon is None:
        x = _num(_first(row, ["x", "X"], None))
        y = _num(_first(row, ["y", "Y"], None))
        if x is not None and y is not None:
            # likely WGS84 x=lon y=lat
            if 62 <= y <= 68 and -26 <= x <= -12:
                lat, lon = y, x
            elif 62 <= x <= 68 and -26 <= y <= -12:
                lat, lon = x, y

    if lat is not None and lon is not None and 62 <= lat <= 68 and -26 <= lon <= -12:
        return lat, lon
    return None, None


@st.cache_data(ttl=900, show_spinner=False)
def get_air_quality() -> tuple[pd.DataFrame, bool, str]:
    attempts = []

    latest_result = fetch_url(LATEST_URL, timeout=10, verify_ssl=True)
    attempts.append(latest_result)
    stations_result = fetch_url(STATIONS_URL, timeout=10, verify_ssl=True)
    attempts.append(stations_result)

    latest_rows = []
    station_rows = []

    if latest_result.ok:
        latest_rows = [_flatten(x) for x in _as_rows(latest_result.data) if isinstance(x, dict)]
    if stations_result.ok:
        station_rows = [_flatten(x) for x in _as_rows(stations_result.data) if isinstance(x, dict)]

    station_by_id = {}
    for s in station_rows:
        sid = _norm_id(s)
        if sid:
            station_by_id[sid] = s

    merged = []

    # If latest has no coords, merge station metadata.
    for row in latest_rows:
        sid = _norm_id(row)
        combined = dict(row)
        if sid and sid in station_by_id:
            for k, v in station_by_id[sid].items():
                combined.setdefault(k, v)

        lat, lon = _lat_lon(combined)
        combined["local_id"] = sid
        combined["station"] = _station_name(combined)
        combined["lat"] = lat
        combined["lon"] = lon
        combined["source"] = LATEST_URL
        merged.append(combined)

    # If latest is empty, still use stations as map points.
    if not merged and station_rows:
        for s in station_rows:
            lat, lon = _lat_lon(s)
            s["local_id"] = _norm_id(s)
            s["station"] = _station_name(s)
            s["lat"] = lat
            s["lon"] = lon
            s["source"] = STATIONS_URL
            merged.append(s)

    # Keep rows even if no coords for Data Explorer, but map will skip missing coords.
    if not merged:
        return pd.DataFrame([]), True, "Loftgæði náðust ekki.\n\n" + result_summary(attempts)

    df = pd.DataFrame(merged)

    # Add display_measurement for map labels.
    def _display(row):
        for key in ["PM10", "pm10", "PM2.5", "pm25", "PM25", "NO2", "no2", "SO2", "so2", "H2S", "h2s", "CO", "co", "O3", "o3", "value", "measurement_value", "latest_value", "Value"]:
            if key in row and str(row.get(key)) not in ["", "nan", "None"]:
                return f"{key}: {row.get(key)}"
        for key in row.index:
            lk = str(key).lower()
            if any(x in lk for x in ["pm10", "pm2", "no2", "so2", "h2s", "co", "o3"]):
                val = row.get(key)
                if str(val) not in ["", "nan", "None"]:
                    return f"{str(key).split('_')[-1]}: {val}"
        return ""

    if not df.empty:
        df["display_measurement"] = df.apply(_display, axis=1)

    coord_count = int(df[["lat", "lon"]].notna().all(axis=1).sum()) if {"lat", "lon"}.issubset(df.columns) else 0

    if coord_count == 0:
        return df, True, f"Loftgæði náðust en engin hnit fundust fyrir kortapunkta — {len(df)} færslur.\n\n" + result_summary(attempts)

    return df, False, f"Loftgæði virk: {LATEST_URL} + {STATIONS_URL} — {len(df)} færslur, {coord_count} með hnit."
