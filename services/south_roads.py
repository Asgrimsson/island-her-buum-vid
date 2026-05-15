
from __future__ import annotations

from typing import Any
import math

import pandas as pd
import requests
import streamlit as st

from services.road_network import road_style


SOUTH_ROAD_NUMBERS = [
    # Stærstu leiðir sem skipta Vallaskóla/Selfoss og Suðurland miklu máli.
    1,      # Hringvegur / Suðurlandsvegur
    30, 31, 32, 33, 34, 35,      # Skeið, Flúðir, Þjórsárdalur, Biskupstungur
    36, 37, 38, 39,              # Þingvellir, Laugarvatn, Þorlákshöfn, Þrengsli
    41, 42, 43,                  # Reykjanes tengingar
    204, 208,                    # Hrunamanna-/Fjallabaksleiðir
    242, 243, 246, 249,          # Þórsmörk / Eyjafjöll / Markarfljótssvæði
    250, 251, 252, 253, 254,     # Landeyjar / Fljótshlíð / Hvolsvöllur
    255, 261, 264, 271,          # Rangárvellir / sveitaleiðir
    268, 269, 270, 272,          # Suðurlands sveitaleiðir
    275, 279,                    # Suðurland / hliðarleiðir
    305, 306, 308, 309,          # Árnessýsla / uppsveitir
    318, 321, 322, 324,          # Þjórsárdalur / uppsveitir
    327, 329, 330, 332,          # Biskupstungur / Hrunamannahreppur
    333, 334, 335, 336,          # Gullni hringurinn / uppsveitir
    337, 338, 339,               # Laugarvatn / Lyngdalsheiði / Grafningur
    340, 341,                    # Ölfus / Hveragerði
    351, 353, 354, 355,          # Flói / Árborg / Eyrarbakki/Stokkseyri
    356, 357, 358, 359,          # Árborg / Grímsnes / sveitaleiðir
    360,                         # Grafningsvegur / Nesjavellir
    363, 365, 366,               # Þingvellir / Grafningur
    374, 375, 376,               # Suðurland / staðbundnar leiðir
    380, 381, 382,               # Ölfus / Selvogur
    425, 426, 427,               # Reykjanes / Suðurstrandavegur
    428, 429,                    # Reykjanes / Krýsuvík
    550,                         # Kaldidalur
    939,                         # Öxi, ef nemendur bera saman Austur/Suður
    2040, 2042, 2043             # Ef þjónustan inniheldur undirnúmer/afleggjara
]

SOUTH_BBOX = {
    "xmin": -22.9,
    "ymin": 63.25,
    "xmax": -16.4,
    "ymax": 64.65,
}

ROAD_ARCGIS_LAYER = "https://vegasja.vegagerdin.is/arcgis/rest/services/data/vegakerfi/MapServer/6/query"

# Hand curated teaching route summaries for the South Iceland page.
SOUTH_ROUTE_GUIDE = [
    {
        "flokkur": "Aðalleið",
        "vegur": "1",
        "heiti": "Suðurlandsvegur / Hringvegur",
        "lysing": "Aðalæð Suðurlands. Tengir Reykjavík, Hveragerði, Selfoss, Hella, Hvolsvöll, Vík og áfram austur.",
        "kennsluhugmynd": "Berið saman veður, færð og umferð milli Hellisheiðar, Selfoss og Víkur.",
    },
    {
        "flokkur": "Ferðamannaleið",
        "vegur": "35 / 36 / 37",
        "heiti": "Gullni hringurinn",
        "lysing": "Tengir Þingvelli, Laugarvatn, Geysi/Gullfoss og uppsveitir Árnessýslu.",
        "kennsluhugmynd": "Nemendur hanna dagsferð og skoða hvaða lifandi gögn skipta máli.",
    },
    {
        "flokkur": "Strandleið",
        "vegur": "427",
        "heiti": "Suðurstrandavegur",
        "lysing": "Leið meðfram suðurströnd Reykjanesskaga og tenging við Þorlákshöfn/Ölfus.",
        "kennsluhugmynd": "Ræða áhrif sjós, veðurs og jarðhræringa á samgöngur.",
    },
    {
        "flokkur": "Skólasvæði",
        "vegur": "34 / 35 / 36 / 38",
        "heiti": "Selfoss og nágrenni",
        "lysing": "Leiðir í kringum Árborg, Flóa, Ölfus, Grímsnes og uppsveitir.",
        "kennsluhugmynd": "Finna hvaða vegir eru mikilvægastir fyrir daglegt líf í Árborg.",
    },
    {
        "flokkur": "Höfn / ferja",
        "vegur": "254",
        "heiti": "Landeyjahafnarvegur",
        "lysing": "Tenging við Landeyjahöfn og Vestmannaeyjar.",
        "kennsluhugmynd": "Skoða hvernig veður og sjór geta haft áhrif á ferðalög.",
    },
    {
        "flokkur": "Fjallaleið",
        "vegur": "208 / F208",
        "heiti": "Fjallabaksleið",
        "lysing": "Hálendisleið sem tengist Landmannalaugum og Fjallabaki.",
        "kennsluhugmynd": "Ræða mun á stofnvegum og hálendisleiðum.",
    },
    {
        "flokkur": "Þórsmörk",
        "vegur": "249",
        "heiti": "Þórsmerkurvegur",
        "lysing": "Leið inn að Þórsmörk, krefjandi vegna vatnsfalla og náttúru.",
        "kennsluhugmynd": "Af hverju þarf að skoða vatnafar og veður áður en farið er inn á þessa leið?",
    },
    {
        "flokkur": "Sveitaleið",
        "vegur": "30 / 32",
        "heiti": "Uppsveitir og Þjórsárdalur",
        "lysing": "Leiðir um landbúnaðarsvæði, orkuvinnslu og náttúruperlur.",
        "kennsluhugmynd": "Tengja byggð, ár, virkjanir og samgöngur.",
    },
]


def _query_where(where: str, max_records: int = 2000) -> dict[str, Any] | None:
    params = {
        "f": "geojson",
        "where": where,
        "outFields": "OBJECTID,NRVEGUR,NUMVEGUR,NUMKAFLI,KAFLIVEGURHEITI,KAFLILENGD,VEGFLOKKUR,VEGTEGUND,VEGHLUTI,STEFNA,IDVEGEIGANDI,IDUMSJON",
        "returnGeometry": "true",
        "outSR": "4326",
        "resultRecordCount": max_records,
    }
    r = requests.get(ROAD_ARCGIS_LAYER, params=params, timeout=25, headers={"User-Agent": "Island-her-buum-vid/4.1.6"})
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and "features" in data:
        return data
    return None


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


def _inside_south_feature(feature: dict[str, Any]) -> bool:
    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates")
    if not coords:
        return False

    # Flatten coordinates for LineString / MultiLineString.
    flat = []
    if geom.get("type") == "LineString":
        flat = coords
    elif geom.get("type") == "MultiLineString":
        for part in coords:
            flat.extend(part)

    for pair in flat[:50]:
        if not isinstance(pair, list) or len(pair) < 2:
            continue
        lon, lat = _num(pair[0]), _num(pair[1])
        if lon is None or lat is None:
            continue
        if SOUTH_BBOX["xmin"] <= lon <= SOUTH_BBOX["xmax"] and SOUTH_BBOX["ymin"] <= lat <= SOUTH_BBOX["ymax"]:
            return True
    return False


def _enrich(feature: dict[str, Any]) -> dict[str, Any]:
    from services.road_network import _enrich_feature
    return _enrich_feature(feature)


@st.cache_data(ttl=86400, show_spinner=False)
def get_south_road_network() -> tuple[dict[str, Any], pd.DataFrame, bool, str]:
    attempts = []
    features = []

    # 1. Fetch by road numbers, then filter to South Iceland bbox.
    for road in SOUTH_ROAD_NUMBERS:
        try:
            data = _query_where(f"NUMVEGUR = {int(road)}", max_records=1200)
            if data and data.get("features"):
                for f in data["features"]:
                    if _inside_south_feature(f):
                        features.append(_enrich(f))
        except Exception as e:
            attempts.append(f"Vegur {road}: {e}")

    # 2. If number-based fetch is too limited, try named search for common South Iceland terms.
    terms = ["Suðurlandsvegur", "Hringvegur", "Þingvallavegur", "Biskupstungnabraut", "Landeyjahafnarvegur", "Þrengslavegur", "Suðurstrandavegur", "Þorlákshafnarvegur"]
    for term in terms:
        try:
            data = _query_where(f"UPPER(KAFLIVEGURHEITI) LIKE UPPER('%{term}%')", max_records=1000)
            if data and data.get("features"):
                for f in data["features"]:
                    if _inside_south_feature(f):
                        features.append(_enrich(f))
        except Exception as e:
            attempts.append(f"Heiti {term}: {e}")

    # Deduplicate by OBJECTID.
    unique = {}
    for f in features:
        oid = (f.get("properties") or {}).get("OBJECTID")
        if oid is not None:
            unique[oid] = f
    features = list(unique.values())

    if features:
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
                "source": p.get("source", "Vegagerðin ArcGIS"),
            })
        df = pd.DataFrame(rows).sort_values(["vegnumer", "kafli", "heiti"]).reset_index(drop=True)
        geojson = {"type": "FeatureCollection", "features": features}
        msg = f"Suðurlandsvegir virkir: {len(features)} vegkaflar frá Vegagerðinni, {df['vegnumer'].nunique()} vegnúmer."
        return geojson, df, False, msg

    # Fallback: use curated guide only.
    df = pd.DataFrame(SOUTH_ROUTE_GUIDE)
    geojson = {"type": "FeatureCollection", "features": []}
    msg = "Suðurlandsvegir náðust ekki úr ArcGIS — kennsluyfirlit notað.\n\n" + "\n".join(attempts[:10])
    return geojson, df, True, msg


def get_south_route_guide() -> pd.DataFrame:
    return pd.DataFrame(SOUTH_ROUTE_GUIDE)


def filter_south_traffic_counters(counters: pd.DataFrame) -> pd.DataFrame:
    if counters is None or counters.empty or "lat" not in counters.columns or "lon" not in counters.columns:
        return pd.DataFrame([])

    df = counters.copy()
    lat = pd.to_numeric(df["lat"], errors="coerce")
    lon = pd.to_numeric(df["lon"], errors="coerce")
    mask = (
        lon.between(SOUTH_BBOX["xmin"], SOUTH_BBOX["xmax"])
        & lat.between(SOUTH_BBOX["ymin"], SOUTH_BBOX["ymax"])
    )
    return df[mask].copy()
