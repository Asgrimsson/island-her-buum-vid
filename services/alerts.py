
from __future__ import annotations

import pandas as pd
import streamlit as st

from .api_client import fetch_first, result_summary


ALERT_URLS = [
    "https://www.vedur.is/vidvaranir",
    "https://www.vedur.is",
]

FALLBACK_ALERTS = [
    {"area": "Allt landið", "level": "green", "title": "Engin staðfest viðvörun í sýnidæmi", "summary": "Viðvaranir verða tengdar betur í næstu útgáfu.", "source": "fallback"}
]


@st.cache_data(ttl=600, show_spinner=False)
def get_alerts() -> tuple[pd.DataFrame, bool, str]:
    result, attempts = fetch_first(ALERT_URLS, timeout=10)
    if not result or not result.ok or not isinstance(result.data, str):
        msg = "Viðvörunarsíða svaraði ekki — sýnidæmi notað.\n\n" + result_summary(attempts)
        return pd.DataFrame(FALLBACK_ALERTS), True, msg

    lower = result.data.lower()

    if "engar viðvaranir" in lower or "no warnings" in lower:
        rows = [{
            "area": "Allt landið",
            "level": "green",
            "title": "Engar viðvaranir í gildi",
            "summary": "Viðvörunarsíða gefur til kynna að engar viðvaranir séu í gildi.",
            "source": result.url,
        }]
    else:
        # First pass: page reachable but detailed official warning parser comes next.
        rows = [{
            "area": "Ísland",
            "level": "yellow",
            "title": "Athuga veðurviðvaranir",
            "summary": "Viðvörunarsíða er virk. Opnaðu vedur.is til að staðfesta nákvæm svæði/lit.",
            "source": result.url,
        }]

    return pd.DataFrame(rows), False, f"Viðvaranir virkar: {result.url}."
