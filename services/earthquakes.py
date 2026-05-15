
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from io import StringIO
import math
import re

import pandas as pd
import requests
import streamlit as st

from .api_client import fetch_url, result_summary


# v3.9 strategy:
# 1. Skjalftar.is bridge — simple earthquake table, data from IMO.
# 2. Vedur.is table/text.
# 3. USGS bridge over Iceland bounding box.
# 4. LUK/API emergency fallback.
# 5. Demo fallback.

SKJALFTAR_URLS = [
    "https://skjalftar.is/",
    "http://skjalftar.is/",
]

VEDUR_URLS = [
    "https://www.vedur.is/skjalftar-og-eldgos/jardskjalftar/",
    "https://en.vedur.is/earthquakes-and-volcanism/earthquakes/",
    "https://www.vedur.is/",
]

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

LUK_QUAKE_URLS = [
    "https://luk.vedur.is/arcgis/rest/services/skjalftar/skjalftar_isn93/MapServer/0/query?f=json&where=1%3D1&outFields=*&returnGeometry=true&outSR=4326",
    "https://luk.vedur.is/arcgis/rest/services/skjalftar/skjalftar_isn93/MapServer/1/query?f=json&where=1%3D1&outFields=*&returnGeometry=true&outSR=4326",
    "https://apis.is/earthquake/is",
    "http://apis.is/earthquake/is",
]

FALLBACK_QUAKES = [
    {"place": "Reykjanesskagi", "lat": 63.91, "lon": -22.25, "size": 2.4, "time": datetime.now().isoformat(), "depth": "", "quality": "sýnidæmi", "source": "fallback"},
    {"place": "Katla / Mýrdalsjökull", "lat": 63.63, "lon": -19.05, "size": 1.8, "time": datetime.now().isoformat(), "depth": "", "quality": "sýnidæmi", "source": "fallback"},
    {"place": "Vatnajökull", "lat": 64.41, "lon": -16.75, "size": 2.1, "time": datetime.now().isoformat(), "depth": "", "quality": "sýnidæmi", "source": "fallback"},
]


GAZETTEER = {
    "Eiturhóli": (64.11, -21.55), "Eiturhóll": (64.11, -21.55),
    "Kolbeinsey": (67.13, -18.69),
    "Eldeyjarboða": (63.72, -22.97), "Eldeyjarboði": (63.72, -22.97), "Eldey": (63.74, -22.95),
    "Grindavík": (63.84, -22.43), "Fagradalsfjall": (63.90, -22.27), "Keilir": (63.94, -22.17), "Keili": (63.94, -22.17),
    "Kleifarvatn": (63.93, -21.97), "Krýsuvík": (63.88, -22.05), "Brennisteinsfjöll": (63.93, -21.80),
    "Bláfjöll": (63.99, -21.65), "Bláfjöllum": (63.99, -21.65),
    "Hengill": (64.08, -21.33), "Hengli": (64.08, -21.33),
    "Hveragerði": (64.00, -21.19), "Selfoss": (63.93, -20.99), "Selfossi": (63.93, -20.99),
    "Hekla": (63.99, -19.70), "Torfajökull": (63.88, -19.07), "Torfajökli": (63.88, -19.07),
    "Katla": (63.63, -19.05), "Mýrdalsjökull": (63.63, -19.05), "Mýrdalsjökli": (63.63, -19.05),
    "Eyjafjallajökull": (63.63, -19.62), "Eyjafjallajökli": (63.63, -19.62),
    "Vatnajökull": (64.45, -16.80), "Vatnajökli": (64.45, -16.80),
    "Bárðarbunga": (64.64, -17.53), "Bárðarbungu": (64.64, -17.53),
    "Grímsvötn": (64.42, -17.33), "Grímsvötnum": (64.42, -17.33), "Grímsfjall": (64.42, -17.33),
    "Askja": (65.03, -16.75), "Herðubreið": (65.18, -16.35), "Herðubreiðartögl": (65.15, -16.20),
    "Mývatn": (65.60, -17.00), "Mývatni": (65.60, -17.00),
    "Húsavík": (66.04, -17.34), "Grímsey": (66.54, -18.02),
    "Tjörnes": (66.18, -17.10), "Tjörnesi": (66.18, -17.10),
    "Langjökull": (64.70, -20.50), "Langjökli": (64.70, -20.50),
    "Hofsjökull": (64.80, -18.80), "Hofsjökli": (64.80, -18.80),
    "Snæfellsnes": (64.85, -23.25), "Snæfellsnesi": (64.85, -23.25),
    "Reykjanesskagi": (63.90, -22.25), "Reykjanesskaga": (63.90, -22.25),
    "Reykjaneshryggur": (63.20, -23.60), "Reykjaneshrygg": (63.20, -23.60),
    "Mosfellsheiði": (64.10, -21.55),
    "Ölfus": (63.98, -21.20), "Ölfusi": (63.98, -21.20),
    "Þingvellir": (64.26, -21.13), "Þingvöllum": (64.26, -21.13),
    "Borgarfjörður": (64.55, -21.90), "Borgarfirði": (64.55, -21.90),
}

DIRECTIONS = {
    "N": (1, 0), "S": (-1, 0), "A": (0, 1), "E": (0, 1), "V": (0, -1), "W": (0, -1),
    "NA": (1, 1), "NE": (1, 1), "NV": (1, -1), "NW": (1, -1),
    "SA": (-1, 1), "SE": (-1, 1), "SV": (-1, -1), "SW": (-1, -1),
    "ANA": (0.5, 1), "ENE": (0.5, 1), "ASA": (-0.5, 1), "ESE": (-0.5, 1),
    "VNV": (0.5, -1), "WNW": (0.5, -1), "VSV": (-0.5, -1), "WSW": (-0.5, -1),
    "NNA": (1, 0.5), "NNE": (1, 0.5), "NNV": (1, -0.5), "NNW": (1, -0.5),
    "SSA": (-1, 0.5), "SSE": (-1, 0.5), "SSV": (-1, -0.5), "SSW": (-1, -0.5),
}


def _num(value, default=None):
    if value in [None, ""]:
        return default
    try:
        return float(str(value).replace(",", ".").strip())
    except Exception:
        m = re.search(r"-?\d+(?:[\.,]\d+)?", str(value))
        if m:
            try:
                return float(m.group(0).replace(",", "."))
            except Exception:
                return default
    return default


def _offset(lat, lon, km, direction):
    direction = str(direction).upper().strip()
    ns, ew = DIRECTIONS.get(direction, (0, 0))
    if ns == 0 and ew == 0:
        return lat, lon

    norm = math.sqrt(ns * ns + ew * ew)
    ns /= norm
    ew /= norm

    dlat = (km * ns) / 111.0
    dlon = (km * ew) / (111.0 * math.cos(math.radians(lat)))
    return lat + dlat, lon + dlon


def _resolve_place(place_text: str):
    text = str(place_text).strip()
    text = re.sub(r"\s+", " ", text)

    # Icelandic: "1,9 km ANA af Eiturhóli"
    # English: "5.9 km NNE of Krýsuvík"
    m = re.search(r"([\d\.,]+)\s*km\s+([A-ZÁÐÉÍÓÚÝÞÆÖ]{1,3})\s+(?:af|frá|of)\s+(.+)", text, re.IGNORECASE)
    if m:
        km = _num(m.group(1), 0)
        direction = m.group(2).upper()
        base = m.group(3).strip()
        base = re.sub(r"\s+á\s+.*$", "", base).strip()
        base = re.sub(r"[.,;:]+$", "", base).strip()

        for name, (lat, lon) in GAZETTEER.items():
            if name.lower() in base.lower() or base.lower() in name.lower():
                return _offset(lat, lon, km, direction)

    # Sometimes string begins with direction and place, no km.
    for name, coords in GAZETTEER.items():
        if name.lower() in text.lower():
            return coords

    low = text.lower()
    if "reykjanes" in low:
        return (63.90, -22.25)
    if "suðurland" in low or "sudurland" in low or "southern iceland" in low:
        return (63.95, -20.70)
    if "norðurland" in low or "nordurland" in low or "northern iceland" in low:
        return (65.70, -18.50)
    if "austurland" in low or "east" in low:
        return (65.00, -14.80)
    if "vestfir" in low or "westfjords" in low:
        return (65.90, -23.50)
    if "iceland region" in low:
        return (64.80, -18.80)

    return None, None


def _looks_like_quake_place(text: str) -> bool:
    low = str(text).lower()
    return any(x in low for x in [
        "km", "af ", "of ", "reykjanes", "jök", "jok", "kolbeinsey", "eld", "hengi",
        "katla", "keili", "krýsuvík", "krysuvik", "vatnaj", "grím", "grim", "tjörnes",
        "iceland", "ridge", "peninsula"
    ])


def _parse_quake_line(line: str, source_url: str) -> dict | None:
    line = re.sub(r"\s+", " ", str(line)).strip()
    if not line:
        return None

    # Common row shapes:
    # "2026-05-15 09:20:00 1.2 2.3 km NNA af Grindavík True"
    # "15. maí 09:20:00 1,2 Yfirfarinn 2,3 km NNA af Grindavík"
    # "09:20:00 1.2 2.3 km NNE of Krýsuvík"
    size = None
    time = ""
    quality = ""

    # Time/date.
    tmatch = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\d{1,2}\.\s+\w+\s+\d{2}:\d{2}:\d{2}|\d{2}:\d{2}:\d{2})", line)
    if tmatch:
        time = tmatch.group(1)

    # Size: prefer number after time, else first decimal.
    rest = line[tmatch.end():] if tmatch else line
    nums = re.findall(r"\d+[\.,]\d+", rest)
    if nums:
        size = _num(nums[0])

    if size is None:
        return None

    # Place starts around the first "km DIR af/of ..."
    pm = re.search(r"(\d+[\.,]\d+\s*km\s+[A-ZÁÐÉÍÓÚÝÞÆÖ]{1,3}\s+(?:af|frá|of)\s+.+)$", line, re.IGNORECASE)
    if pm:
        place = pm.group(1)
    else:
        # Try after quality words.
        parts = re.split(r"\b(?:Yfirfarinn|Óyfirfarinn|reviewed|automatic|true|false)\b", line, flags=re.IGNORECASE)
        place = parts[-1].strip() if len(parts) > 1 else rest

    place = re.sub(r"\s+(?:True|False|true|false)$", "", place).strip()
    place = re.sub(r"^[\d\.,]+\s+", "", place).strip()

    if not _looks_like_quake_place(place):
        return None

    if re.search(r"Yfirfarinn|reviewed|True", line, re.IGNORECASE):
        quality = "staðfest/yfirfarið"
    elif re.search(r"Óyfirfarinn|automatic|False", line, re.IGNORECASE):
        quality = "óyfirfarið"

    lat, lon = _resolve_place(place)
    if lat is None or lon is None:
        return None

    return {
        "place": place,
        "lat": lat,
        "lon": lon,
        "size": size,
        "time": time,
        "depth": "",
        "quality": quality,
        "source": source_url,
    }


def _parse_table_rows(df: pd.DataFrame, source_url: str) -> list[dict]:
    rows = []
    if df is None or df.empty:
        return rows

    cols = [str(c).lower() for c in df.columns]
    time_col = next((c for c in df.columns if any(k in str(c).lower() for k in ["tími", "timi", "time"])), None)
    size_col = next((c for c in df.columns if any(k in str(c).lower() for k in ["stærð", "staerd", "magnitude", "size"])), None)
    place_col = next((c for c in df.columns if any(k in str(c).lower() for k in ["staður", "stadur", "location", "place"])), None)
    quality_col = next((c for c in df.columns if any(k in str(c).lower() for k in ["staðfest", "stadfest", "gæði", "quality", "confirmed"])), None)

    if time_col and size_col and place_col:
        for _, r in df.iterrows():
            place = str(r.get(place_col, "")).strip()
            if not place or place.lower() == "nan":
                continue

            lat, lon = _resolve_place(place)
            if lat is None or lon is None:
                continue

            rows.append({
                "place": place,
                "lat": lat,
                "lon": lon,
                "size": _num(r.get(size_col), 0),
                "time": str(r.get(time_col, "")),
                "depth": "",
                "quality": str(r.get(quality_col, "")) if quality_col else "",
                "source": source_url,
            })
        return rows

    # Fallback: stringify every row and parse.
    for _, r in df.iterrows():
        row_text = " ".join([str(x) for x in r.tolist()])
        parsed = _parse_quake_line(row_text, source_url)
        if parsed:
            rows.append(parsed)

    return rows


def _fetch_html_text(url: str) -> tuple[str, str]:
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Vallaskoli-Live-Lab/3.9"})
        r.raise_for_status()
        return r.text, ""
    except Exception as e:
        return "", str(e)


def _parse_html_quakes(url: str) -> tuple[list[dict], str]:
    html, err = _fetch_html_text(url)
    if err:
        return [], err

    all_rows = []

    # 1. HTML tables.
    try:
        tables = pd.read_html(StringIO(html))
        for table in tables:
            all_rows.extend(_parse_table_rows(table, url))
    except Exception:
        pass

    if all_rows:
        return all_rows, ""

    # 2. Plain text from HTML.
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        plain = soup.get_text("\n")
    except Exception:
        plain = re.sub(r"<[^>]+>", "\n", html)

    for line in plain.splitlines():
        parsed = _parse_quake_line(line, url)
        if parsed:
            all_rows.append(parsed)

    return all_rows, ""


def _parse_usgs_geojson(raw, source_url: str) -> list[dict]:
    if not isinstance(raw, dict):
        return []

    rows = []
    for f in raw.get("features", []):
        props = f.get("properties", {}) or {}
        geom = f.get("geometry", {}) or {}
        coords = geom.get("coordinates") or []
        if not isinstance(coords, list) or len(coords) < 2:
            continue

        lon = _num(coords[0])
        lat = _num(coords[1])
        depth = coords[2] if len(coords) >= 3 else ""

        if lat is None or lon is None or not (62 <= lat <= 68 and -26 <= lon <= -12):
            continue

        t = props.get("time")
        try:
            time_str = datetime.fromtimestamp(int(t) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if t else ""
        except Exception:
            time_str = str(t or "")

        rows.append({
            "place": props.get("place") or "Iceland region",
            "lat": lat,
            "lon": lon,
            "size": _num(props.get("mag"), 0),
            "time": time_str,
            "depth": depth,
            "quality": props.get("status") or props.get("magType") or "USGS",
            "source": source_url,
        })
    return rows


def _fetch_usgs_bridge(days: int = 30, minmag: float = -1.0) -> tuple[list[dict], str]:
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "format": "geojson",
        "starttime": start,
        "minlatitude": 62,
        "maxlatitude": 68,
        "minlongitude": -26,
        "maxlongitude": -12,
        "minmagnitude": minmag,
        "orderby": "time",
        "limit": 2000,
        "eventtype": "earthquake",
    }

    try:
        r = requests.get(USGS_URL, params=params, timeout=15, headers={"User-Agent": "Vallaskoli-Live-Lab/3.9"})
        r.raise_for_status()
        return _parse_usgs_geojson(r.json(), r.url), ""
    except Exception as e:
        return [], str(e)


def _parse_luk_or_apis(result):
    raw = result.data
    if isinstance(raw, dict) and "error" in raw:
        return []

    if isinstance(raw, dict) and "features" in raw:
        rows = []
        for f in raw.get("features", []):
            attrs = f.get("attributes") or f.get("properties") or {}
            geom = f.get("geometry") or {}

            lat = _num(attrs.get("lat") or attrs.get("LAT") or attrs.get("Latitude"))
            lon = _num(attrs.get("lng") or attrs.get("lon") or attrs.get("LNG") or attrs.get("Longitude"))
            if lon and 12 <= lon <= 26:
                lon = -lon

            if (lat is None or lon is None) and "x" in geom and "y" in geom:
                lon = _num(geom.get("x"))
                lat = _num(geom.get("y"))
                if lon and 12 <= lon <= 26:
                    lon = -lon

            if lat is None or lon is None or not (62 <= lat <= 68 and -26 <= lon <= -12):
                continue

            rows.append({
                "place": attrs.get("location") or attrs.get("name") or f"{lat:.3f}, {lon:.3f}",
                "lat": lat,
                "lon": lon,
                "size": _num(attrs.get("mag") or attrs.get("MAG") or attrs.get("M"), 0),
                "time": attrs.get("datetime") or attrs.get("start_time") or "",
                "depth": attrs.get("depth") or "",
                "quality": attrs.get("quality") or "",
                "source": result.url,
            })
        return rows

    if isinstance(raw, dict):
        data = raw.get("results") or raw.get("data") or []
    elif isinstance(raw, list):
        data = raw
    else:
        data = []

    rows = []
    for item in data:
        lat = _num(item.get("latitude") or item.get("lat"))
        lon = _num(item.get("longitude") or item.get("lon") or item.get("lng"))
        if lon and 12 <= lon <= 26:
            lon = -lon
        if lat is None or lon is None or not (62 <= lat <= 68 and -26 <= lon <= -12):
            continue
        rows.append({
            "place": item.get("humanReadableLocation") or item.get("location") or "Jarðskjálfti",
            "lat": lat,
            "lon": lon,
            "size": _num(item.get("size") or item.get("magnitude"), 0),
            "time": item.get("timestamp") or item.get("time") or "",
            "depth": item.get("depth") or "",
            "quality": "",
            "source": result.url,
        })
    return rows


def _dedupe(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["size"] = pd.to_numeric(df["size"], errors="coerce").fillna(0)
    df = df.drop_duplicates(subset=["place", "time", "size"], keep="first")
    if "time" in df.columns:
        df = df.sort_values(["time", "size"], ascending=[False, False], na_position="last")
    else:
        df = df.sort_values("size", ascending=False)
    return df.reset_index(drop=True)


@st.cache_data(ttl=300, show_spinner=False)
def get_earthquakes() -> tuple[pd.DataFrame, bool, str]:
    attempts = []

    # 1. Skjalftar.is bridge.
    for url in SKJALFTAR_URLS:
        rows, err = _parse_html_quakes(url)
        if rows:
            df = _dedupe(rows).head(500)
            return df, False, f"Skjálftagögn virk: Skjálftar.is bridge — {len(df)} skjálftar síðustu 48 klst. Gögn birt þar eru frá Veðurstofu Íslands; staðsetning á korti er leyst úr staðarheiti."
        if err:
            attempts.append(type("Obj", (), {"ok": False, "url": url, "kind": "html", "error": err, "elapsed_ms": 0, "verify_ssl": True})())

    # 2. Vedur.is table/text.
    for url in VEDUR_URLS:
        rows, err = _parse_html_quakes(url)
        if rows:
            df = _dedupe(rows).head(500)
            return df, False, f"Skjálftagögn virk: vedur.is tafla/texti — {len(df)} skjálftar. Staðsetning á korti er gróflega leyst úr staðarheiti."
        if err:
            attempts.append(type("Obj", (), {"ok": False, "url": url, "kind": "html", "error": err, "elapsed_ms": 0, "verify_ssl": True})())

    # 3. USGS bridge.
    rows, err = _fetch_usgs_bridge(days=30, minmag=-1.0)
    if rows:
        df = _dedupe(rows).head(500)
        return df, False, f"Skjálftagögn virk: USGS GeoJSON bridge — {len(df)} skjálftar á Íslandssvæði síðustu 30 daga. Ath. brúarleið, ekki upprunalegt IMO/LUK lag."
    if err:
        attempts.append(type("Obj", (), {"ok": False, "url": USGS_URL, "kind": "geojson", "error": err, "elapsed_ms": 0, "verify_ssl": True})())

    # 4. Emergency LUK/APIs fallback.
    for url in LUK_QUAKE_URLS:
        result = fetch_url(url, timeout=12, verify_ssl=True)
        attempts.append(result)
        if not result.ok:
            continue
        parsed = _parse_luk_or_apis(result)
        if parsed:
            df = _dedupe(parsed).head(500)
            return df, False, f"Skjálftagögn virk: {result.url} — {len(df)} færslur."

    msg = "Skjálftagögn náðust ekki úr Skjálftar.is, vedur.is, USGS, LUK eða APIs.is — sýnidæmi notað.\n\n" + result_summary(attempts)
    return pd.DataFrame(FALLBACK_QUAKES), True, msg
