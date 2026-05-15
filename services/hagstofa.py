
from __future__ import annotations

from io import StringIO
import re
from typing import Any

import pandas as pd
import requests
import streamlit as st


PXWEB_POPULATION_URLS = [
    # Current table found through Hagstofa / PXWeb for byggðakjarnar.
    "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/2_byggdir/Byggdakjarnar/MAN030101",
    "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/2_byggdir/Byggdakjarnar/MAN030101.px",
]

HEADERS = {
    "User-Agent": "Vallaskoli-Live-Lab/3.5 educational geography dashboard",
    "Content-Type": "application/json",
}

# If Hagstofa names differ from our teaching place names.
PLACE_ALIASES = {
    "Reykjavík": ["Reykjavík"],
    "Kópavogur": ["Kópavogur"],
    "Hafnarfjörður": ["Hafnarfjörður"],
    "Garðabær": ["Garðabær"],
    "Mosfellsbær": ["Mosfellsbær"],
    "Seltjarnarnes": ["Seltjarnarnes"],
    "Selfoss": ["Selfoss"],
    "Hveragerði": ["Hveragerði"],
    "Þorlákshöfn": ["Þorlákshöfn"],
    "Eyrarbakki": ["Eyrarbakki"],
    "Stokkseyri": ["Stokkseyri"],
    "Hella": ["Hella"],
    "Hvolsvöllur": ["Hvolsvöllur"],
    "Vík í Mýrdal": ["Vík í Mýrdal", "Vík"],
    "Kirkjubæjarklaustur": ["Kirkjubæjarklaustur"],
    "Vestmannaeyjar": ["Vestmannaeyjar"],
    "Akranes": ["Akranes"],
    "Borgarnes": ["Borgarnes"],
    "Stykkishólmur": ["Stykkishólmur"],
    "Grundarfjörður": ["Grundarfjörður"],
    "Ólafsvík": ["Ólafsvík"],
    "Ísafjörður": ["Ísafjörður"],
    "Bolungarvík": ["Bolungarvík"],
    "Patreksfjörður": ["Patreksfjörður"],
    "Blönduós": ["Blönduós"],
    "Sauðárkrókur": ["Sauðárkrókur"],
    "Hvammstangi": ["Hvammstangi"],
    "Akureyri": ["Akureyri"],
    "Húsavík": ["Húsavík"],
    "Dalvík": ["Dalvík"],
    "Siglufjörður": ["Siglufjörður"],
    "Ólafsfjörður": ["Ólafsfjörður"],
    "Egilsstaðir": ["Egilsstaðir"],
    "Seyðisfjörður": ["Seyðisfjörður"],
    "Neskaupstaður": ["Neskaupstaður"],
    "Reyðarfjörður": ["Reyðarfjörður"],
    "Eskifjörður": ["Eskifjörður"],
    "Höfn": ["Höfn", "Höfn í Hornafirði"],
    "Djúpivogur": ["Djúpivogur"],
    "Keflavík": ["Keflavík"],
    "Njarðvík": ["Njarðvík"],
    "Grindavík": ["Grindavík"],
    "Sandgerði": ["Sandgerði"],
    "Garður": ["Garður"],
}


def _normalize_name(value: str) -> str:
    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    value = value.replace(" - ", " ")
    return value


def _is_total_label(label: str) -> bool:
    text = str(label).lower()
    return any(x in text for x in ["alls", "allir", "samtals", "total"])


def _pick_variable(metadata: dict[str, Any], keywords: list[str]) -> dict[str, Any] | None:
    for var in metadata.get("variables", []):
        code = str(var.get("code", "")).lower()
        text = str(var.get("text", "")).lower()
        if any(k.lower() in code or k.lower() in text for k in keywords):
            return var
    return None


def _pick_latest(values: list[str]) -> str:
    # Values are often years as strings.
    numeric = []
    for v in values:
        try:
            numeric.append((int(str(v)[:4]), v))
        except Exception:
            pass
    if numeric:
        return sorted(numeric)[-1][1]
    return values[-1]


def _pick_total_value(var: dict[str, Any]) -> str | None:
    values = var.get("values", [])
    labels = var.get("valueTexts", values)
    for v, label in zip(values, labels):
        if _is_total_label(label) or _is_total_label(v):
            return v
    # If no total label, keep first value to avoid failing.
    return values[0] if values else None


def _get_metadata(url: str) -> dict[str, Any]:
    r = requests.get(url, timeout=15, headers={"User-Agent": HEADERS["User-Agent"]})
    r.raise_for_status()
    return r.json()


def _query_csv(url: str, metadata: dict[str, Any]) -> tuple[pd.DataFrame, str]:
    variables = metadata.get("variables", [])

    time_var = _pick_variable(metadata, ["ár", "year", "time"])
    place_var = _pick_variable(metadata, ["byggð", "byggdakjarni", "kjarni", "staður", "place"])
    sex_var = _pick_variable(metadata, ["kyn", "sex"])
    age_var = _pick_variable(metadata, ["aldur", "age"])

    if not time_var:
        time_var = variables[-1]
    if not place_var:
        place_var = variables[0]

    latest_year = _pick_latest(time_var.get("values", []))

    query = []

    for var in variables:
        code = var.get("code")
        values = var.get("values", [])

        if var is time_var:
            selected = [latest_year]
        elif var is place_var:
            selected = values
        elif var is sex_var or var is age_var:
            total = _pick_total_value(var)
            selected = [total] if total is not None else values[:1]
        else:
            # Other dimensions: take all if small, otherwise first.
            selected = values if len(values) <= 20 else values[:1]

        query.append({
            "code": code,
            "selection": {
                "filter": "item",
                "values": selected,
            }
        })

    payload = {
        "query": query,
        "response": {"format": "CSV"}
    }

    r = requests.post(url, json=payload, timeout=30, headers=HEADERS)
    r.raise_for_status()

    df = pd.read_csv(StringIO(r.text))
    return df, str(latest_year)


def _find_columns(df: pd.DataFrame) -> tuple[str, str]:
    cols = list(df.columns)
    place_col = None
    value_col = cols[-1]

    for c in cols:
        low = str(c).lower()
        if any(x in low for x in ["byggð", "byggd", "kjarni", "staður", "stadur", "place"]):
            place_col = c
            break

    # Population value column is often "Mannfjöldi" or the last numeric column.
    for c in reversed(cols):
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() > 0:
            value_col = c
            break

    if place_col is None:
        place_col = cols[0]

    return place_col, value_col


def _clean_population_df(raw: pd.DataFrame, year: str, source_url: str) -> pd.DataFrame:
    place_col, value_col = _find_columns(raw)

    out = raw[[place_col, value_col]].copy()
    out.columns = ["place_hagstofa", "population_value"]
    out["population_value"] = pd.to_numeric(out["population_value"], errors="coerce")
    out = out.dropna(subset=["population_value"])
    out["population_value"] = out["population_value"].astype(int)
    out["population_label"] = out["population_value"].apply(lambda x: f"{x:,}".replace(",", "."))
    out["year"] = year
    out["source"] = source_url
    out["match_key"] = out["place_hagstofa"].apply(_normalize_name)
    return out.sort_values("population_value", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=86400, show_spinner=False)
def get_hagstofa_population() -> tuple[pd.DataFrame, bool, str]:
    attempts = []

    for url in PXWEB_POPULATION_URLS:
        try:
            metadata = _get_metadata(url)
            raw, year = _query_csv(url, metadata)
            df = _clean_population_df(raw, year, url)
            if not df.empty:
                return df, False, f"Hagstofa mannfjöldi virkur: {url} — {len(df)} byggðakjarnar/stöðugildi, ár {year}."
        except Exception as e:
            attempts.append(f"{url} — {e}")

    msg = "Hagstofa mannfjöldi náðist ekki. Notum u.þ.b. kennslugildi.\n\n" + "\n".join(attempts)
    return pd.DataFrame([]), True, msg


def apply_population_to_places(places: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    df = places.copy()

    if population is None or population.empty:
        df["population_source"] = "Kennslugildi / fallback"
        df["population_year"] = ""
        return df

    pop_by_key = population.set_index("match_key").to_dict("index")

    def _lookup(row):
        aliases = PLACE_ALIASES.get(row["name"], [row["name"]])
        for alias in aliases:
            key = _normalize_name(alias)
            if key in pop_by_key:
                hit = pop_by_key[key]
                return hit["population_label"], hit["year"], "Hagstofa", hit["place_hagstofa"]

        # fuzzy fallback
        row_key = _normalize_name(row["name"])
        for key, hit in pop_by_key.items():
            if row_key in key or key in row_key:
                return hit["population_label"], hit["year"], "Hagstofa fuzzy", hit["place_hagstofa"]

        return row.get("population", "Bætum við síðar"), "", "Kennslugildi / fallback", ""

    values = df.apply(_lookup, axis=1, result_type="expand")
    values.columns = ["population", "population_year", "population_source", "population_hagstofa_name"]

    for col in values.columns:
        df[col] = values[col]

    return df


def _query_trend_csv(url: str, metadata: dict[str, Any]) -> pd.DataFrame:
    """
    Query all years for all places, with total sex/age where those dimensions exist.
    """
    variables = metadata.get("variables", [])

    time_var = _pick_variable(metadata, ["ár", "year", "time"])
    place_var = _pick_variable(metadata, ["byggð", "byggdakjarni", "kjarni", "staður", "place"])
    sex_var = _pick_variable(metadata, ["kyn", "sex"])
    age_var = _pick_variable(metadata, ["aldur", "age"])

    if not time_var:
        time_var = variables[-1]
    if not place_var:
        place_var = variables[0]

    query = []
    for var in variables:
        code = var.get("code")
        values = var.get("values", [])

        if var is time_var:
            selected = values
        elif var is place_var:
            selected = values
        elif var is sex_var or var is age_var:
            total = _pick_total_value(var)
            selected = [total] if total is not None else values[:1]
        else:
            selected = values if len(values) <= 20 else values[:1]

        query.append({
            "code": code,
            "selection": {"filter": "item", "values": selected}
        })

    payload = {
        "query": query,
        "response": {"format": "CSV"}
    }

    r = requests.post(url, json=payload, timeout=45, headers=HEADERS)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text))


def _find_time_column(df: pd.DataFrame) -> str:
    for c in df.columns:
        low = str(c).lower()
        if any(x in low for x in ["ár", "year", "time"]):
            return c
    # fallback: first column that looks like year
    for c in df.columns:
        vals = df[c].astype(str).head(20).tolist()
        if any(re.match(r"^\d{4}$", v[:4]) for v in vals):
            return c
    return df.columns[-2] if len(df.columns) >= 2 else df.columns[0]


def _clean_trend_df(raw: pd.DataFrame, source_url: str) -> pd.DataFrame:
    place_col, value_col = _find_columns(raw)
    year_col = _find_time_column(raw)

    out = raw[[place_col, year_col, value_col]].copy()
    out.columns = ["place_hagstofa", "year", "population_value"]

    out["year"] = out["year"].astype(str).str.extract(r"(\d{4})", expand=False)
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["population_value"] = pd.to_numeric(out["population_value"], errors="coerce")

    out = out.dropna(subset=["year", "population_value"])
    out["year"] = out["year"].astype(int)
    out["population_value"] = out["population_value"].astype(int)
    out["match_key"] = out["place_hagstofa"].apply(_normalize_name)
    out["source"] = source_url
    return out.sort_values(["place_hagstofa", "year"]).reset_index(drop=True)


@st.cache_data(ttl=86400, show_spinner=False)
def get_hagstofa_population_trends() -> tuple[pd.DataFrame, bool, str]:
    attempts = []

    for url in PXWEB_POPULATION_URLS:
        try:
            metadata = _get_metadata(url)
            raw = _query_trend_csv(url, metadata)
            df = _clean_trend_df(raw, url)
            if not df.empty:
                min_year = int(df["year"].min())
                max_year = int(df["year"].max())
                return df, False, f"Hagstofa byggðaþróun virk: {url} — {len(df)} raðir, ár {min_year}–{max_year}."
        except Exception as e:
            attempts.append(f"{url} — {e}")

    return pd.DataFrame([]), True, "Hagstofa byggðaþróun náðist ekki.\n\n" + "\n".join(attempts)


def _fallback_base_population(value) -> int | None:
    try:
        return int(str(value).replace(".", "").replace("≈", "").replace(" ", "").strip())
    except Exception:
        return None


def build_place_trends(places: pd.DataFrame, trends: pd.DataFrame) -> pd.DataFrame:
    """
    Map Hagstofa trend rows to our place list.
    If official trend data is unavailable for a place, create a simple fallback trend
    from the current teaching population so the UI still works.
    """
    rows = []

    if trends is not None and not trends.empty:
        by_key = {key: group.copy() for key, group in trends.groupby("match_key")}

        for _, place in places.iterrows():
            aliases = PLACE_ALIASES.get(place["name"], [place["name"]])
            hit = None
            hit_name = ""

            for alias in aliases:
                key = _normalize_name(alias)
                if key in by_key:
                    hit = by_key[key]
                    hit_name = alias
                    break

            if hit is None:
                place_key = _normalize_name(place["name"])
                for key, group in by_key.items():
                    if place_key in key or key in place_key:
                        hit = group
                        hit_name = group["place_hagstofa"].iloc[0]
                        break

            if hit is not None and not hit.empty:
                for _, r in hit.iterrows():
                    rows.append({
                        "name": place["name"],
                        "region": place.get("region", ""),
                        "municipality": place.get("municipality", ""),
                        "year": int(r["year"]),
                        "population_value": int(r["population_value"]),
                        "source": "Hagstofa",
                        "hagstofa_name": r.get("place_hagstofa", hit_name),
                    })
                continue

            base = _fallback_base_population(place.get("population"))
            if base:
                for year, factor in [(2014, 0.86), (2019, 0.93), (2024, 1.00)]:
                    rows.append({
                        "name": place["name"],
                        "region": place.get("region", ""),
                        "municipality": place.get("municipality", ""),
                        "year": year,
                        "population_value": int(base * factor),
                        "source": "Fallback trend",
                        "hagstofa_name": "",
                    })

    else:
        for _, place in places.iterrows():
            base = _fallback_base_population(place.get("population"))
            if base:
                for year, factor in [(2014, 0.86), (2019, 0.93), (2024, 1.00)]:
                    rows.append({
                        "name": place["name"],
                        "region": place.get("region", ""),
                        "municipality": place.get("municipality", ""),
                        "year": year,
                        "population_value": int(base * factor),
                        "source": "Fallback trend",
                        "hagstofa_name": "",
                    })

    if not rows:
        return pd.DataFrame([])

    return pd.DataFrame(rows).sort_values(["name", "year"]).reset_index(drop=True)


def summarize_place_trend(place_trends: pd.DataFrame, place_name: str) -> dict:
    df = place_trends[place_trends["name"] == place_name].sort_values("year")
    if df.empty:
        return {}

    latest = df.iloc[-1]
    first = df.iloc[0]

    def _value_years_back(years: int):
        target = int(latest["year"]) - years
        prev = df[df["year"] <= target]
        if prev.empty:
            return None
        return prev.iloc[-1]

    five = _value_years_back(5)
    ten = _value_years_back(10)

    latest_pop = int(latest["population_value"])
    first_pop = int(first["population_value"])
    total_change = latest_pop - first_pop
    total_pct = round((total_change / first_pop) * 100, 1) if first_pop else 0

    summary = {
        "latest_year": int(latest["year"]),
        "latest_population": latest_pop,
        "first_year": int(first["year"]),
        "first_population": first_pop,
        "total_change": total_change,
        "total_pct": total_pct,
        "source": latest.get("source", ""),
    }

    if five is not None:
        val = int(five["population_value"])
        summary["change_5y"] = latest_pop - val
        summary["change_5y_pct"] = round(((latest_pop - val) / val) * 100, 1) if val else 0
        summary["year_5y"] = int(five["year"])

    if ten is not None:
        val = int(ten["population_value"])
        summary["change_10y"] = latest_pop - val
        summary["change_10y_pct"] = round(((latest_pop - val) / val) * 100, 1) if val else 0
        summary["year_10y"] = int(ten["year"])

    if total_pct > 5:
        summary["story"] = "Staðurinn hefur stækkað á tímabilinu."
    elif total_pct < -5:
        summary["story"] = "Staðurinn hefur minnkað á tímabilinu."
    else:
        summary["story"] = "Staðurinn hefur verið nokkuð stöðugur á tímabilinu."

    return summary
