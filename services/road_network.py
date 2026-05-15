
from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd
import requests
import streamlit as st


MAX_TOTAL_ROAD_FEATURES = 650
MAX_FEATURES_PER_ROAD = 140

ROAD_ARCGIS_LAYER = "https://vegasja.vegagerdin.is/arcgis/rest/services/data/vegakerfi/MapServer/6/query"

# Main road numbers to fetch first. This keeps the layer usable and not too heavy.
DEFAULT_ROAD_NUMBERS = [1, 35, 36, 37, 38, 39, 41, 42, 43, 54, 60, 61, 76, 82, 85, 92, 96, 254, 427, 550]

ROAD_CLASS = {
    1: "Stofnvegur",
    2: "Tengivegur",
    3: "Héraðsvegur",
    4: "Landsvegur",
    5: "Stofnbraut",
    6: "Tengibraut",
    7: "Safnvegur",
    8: "Aðrir vegir",
}

ROAD_PART = {
    1: "Vegur, miðlína",
    3: "Aðrein",
    4: "Frárein",
    5: "Hringtorg",
    6: "Vegslóði",
}

DIRECTION = {
    -1: "Einstefna á móti línustefnu",
    1: "Einstefna með línustefnu",
    2: "Tvístefna",
}


def _num(value, default=None):
    try:
        if value in [None, "", "nan"]:
            return default
        n = float(value)
        if math.isnan(n):
            return default
        return n
    except Exception:
        return default


def _safe_int(value, default=None):
    n = _num(value, default)
    if n is None:
        return default
    try:
        return int(n)
    except Exception:
        return default


def _decode(value, lookup: dict, default=""):
    i = _safe_int(value, None)
    if i is None:
        return default if default else str(value or "")
    return lookup.get(i, str(i))


def _query_road_number(road_number: int, max_records: int = MAX_FEATURES_PER_ROAD) -> dict[str, Any] | None:
    params = {
        "f": "geojson",
        "where": f"NUMVEGUR = {int(road_number)}",
        "outFields": "OBJECTID,NRVEGUR,NUMVEGUR,NUMKAFLI,KAFLIVEGURHEITI,KAFLILENGD,VEGFLOKKUR,VEGTEGUND,VEGHLUTI,STEFNA,IDVEGEIGANDI,IDUMSJON",
        "returnGeometry": "true",
        "outSR": "4326",
        "resultRecordCount": max_records,
    }
    r = requests.get(ROAD_ARCGIS_LAYER, params=params, timeout=25, headers={"User-Agent": "Island-her-buum-vid/4.1.5"})
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict) or "features" not in data:
        return None
    return data


def _fallback_geojson() -> dict[str, Any]:
    # Used only if ArcGIS is unreachable. Simpler than v4.1.4 lines, but still usable.
    features = []
    fallback = [
        ("1", "Hringvegur — yfirlitslína", [[-21.94, 64.15], [-20.99, 63.94], [-19.01, 63.42], [-15.21, 64.25], [-14.39, 65.27], [-18.13, 65.69], [-21.92, 64.54], [-21.94, 64.15]]),
        ("41", "Reykjanesbraut — yfirlitslína", [[-21.94, 64.15], [-22.20, 64.04], [-22.56, 64.00]]),
        ("35", "Gullni hringurinn / Kjalvegur — yfirlitslína", [[-20.99, 63.94], [-20.31, 64.13], [-20.12, 64.31], [-19.50, 64.90]]),
    ]
    for i, (num, name, coords) in enumerate(fallback, 1):
        features.append({
            "type": "Feature",
            "properties": {
                "OBJECTID": i,
                "NRVEGUR": num,
                "NUMVEGUR": int(num),
                "KAFLIVEGURHEITI": name,
                "KAFLILENGD": None,
                "VEGFLOKKUR_TEXT": "Yfirlit",
                "VEGHLUTI_TEXT": "Yfirlitslína",
                "STEFNA_TEXT": "",
                "source": "fallback",
            },
            "geometry": {"type": "LineString", "coordinates": coords},
        })
    return {"type": "FeatureCollection", "features": features}


def _enrich_feature(feature: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties") or {}

    props["NUMVEGUR_LABEL"] = str(_safe_int(props.get("NUMVEGUR"), props.get("NRVEGUR", "")))
    props["VEGFLOKKUR_TEXT"] = _decode(props.get("VEGFLOKKUR"), ROAD_CLASS, "")
    props["VEGHLUTI_TEXT"] = _decode(props.get("VEGHLUTI"), ROAD_PART, "")
    props["STEFNA_TEXT"] = _decode(props.get("STEFNA"), DIRECTION, "")
    props["KAFLILENGD_KM"] = round((_num(props.get("KAFLILENGD"), 0) or 0) / 1000, 2) if props.get("KAFLILENGD") not in [None, ""] else None
    props["source"] = props.get("source", "Vegagerðin ArcGIS")

    feature["properties"] = props
    return feature


@st.cache_data(ttl=86400, show_spinner=False)
def get_road_network(road_numbers: list[int] | None = None) -> tuple[dict[str, Any], pd.DataFrame, bool, str]:
    road_numbers = road_numbers or DEFAULT_ROAD_NUMBERS
    features = []
    attempts = []

    for road in road_numbers:
        if len(features) >= MAX_TOTAL_ROAD_FEATURES:
            break
        try:
            data = _query_road_number(road)
            if data and data.get("features"):
                for f in data["features"][:MAX_FEATURES_PER_ROAD]:
                    features.append(_enrich_feature(f))
                    if len(features) >= MAX_TOTAL_ROAD_FEATURES:
                        break
        except Exception as e:
            attempts.append(f"Vegur {road}: {e}")

    if features:
        geojson = {"type": "FeatureCollection", "features": features}
        rows = []
        for f in features:
            p = f.get("properties") or {}
            rows.append({
                "vegnumer": p.get("NUMVEGUR_LABEL", ""),
                "kafli": p.get("NUMKAFLI", ""),
                "heiti": p.get("KAFLIVEGURHEITI", ""),
                "lengd_km": p.get("KAFLILENGD_KM", ""),
                "vegflokkur": p.get("VEGFLOKKUR_TEXT", ""),
                "veghluti": p.get("VEGHLUTI_TEXT", ""),
                "stefna": p.get("STEFNA_TEXT", ""),
                "source": p.get("source", ""),
            })
        df = pd.DataFrame(rows)
        msg = f"Nákvæmari vegalínur virkar: Vegagerðin ArcGIS — {len(features)} vegkaflar, {len(set(df['vegnumer']))} vegnúmer."
        return geojson, df, False, msg

    geojson = _fallback_geojson()
    df = pd.DataFrame([{
        "vegnumer": f["properties"].get("NUMVEGUR_LABEL", f["properties"].get("NUMVEGUR")),
        "kafli": "",
        "heiti": f["properties"].get("KAFLIVEGURHEITI", ""),
        "lengd_km": "",
        "vegflokkur": f["properties"].get("VEGFLOKKUR_TEXT", ""),
        "veghluti": f["properties"].get("VEGHLUTI_TEXT", ""),
        "stefna": "",
        "source": "fallback",
    } for f in geojson["features"]])

    msg = "Nákvæmari vegalínur náðust ekki úr ArcGIS — einfalt yfirlit notað.\n\n" + "\n".join(attempts)
    return geojson, df, True, msg


def road_style(feature: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties") or {}
    road = str(props.get("NUMVEGUR_LABEL", props.get("NUMVEGUR", "")))

    if road == "1":
        color = "#ef4444"
        weight = 4.5
    elif road in ["35", "36", "37", "41", "42", "43"]:
        color = "#f97316"
        weight = 4
    elif road in ["60", "61", "76", "82", "85", "87", "92", "96"]:
        color = "#2563eb"
        weight = 3.4
    else:
        color = "#475569"
        weight = 2.8

    return {
        "color": color,
        "weight": weight,
        "opacity": 0.82,
    }
