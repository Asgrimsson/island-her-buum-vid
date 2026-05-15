from __future__ import annotations

import pandas as pd
import streamlit as st


def status_badge(label: str, fallback: bool):
    if fallback:
        st.warning(f"⚠️ {label}: sýnidæmi")
    else:
        st.success(f"✅ {label}: lifandi gögn")


def render_metric_row(cameras, quakes, traffic, weather):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📷 Myndavélar", len(cameras))
    c2.metric("🌋 Skjálftar", len(quakes))
    c3.metric("🚗 Færðarpunktar", len(traffic))
    c4.metric("🌦️ Veðurraðir", len(weather))
    c5.metric("🎒 Verkefni", 10)


def render_data_health(statuses: dict):
    with st.expander("🩺 Gagnaheilsa / Realtime Engine", expanded=False):
        for name, info in statuses.items():
            fallback, message = info
            if fallback:
                st.warning(f"{name}: {message}")
            else:
                st.success(f"{name}: {message}")


def render_risk_panel(alerts: pd.DataFrame, quakes: pd.DataFrame, traffic: pd.DataFrame):
    st.subheader("🛡️ Öryggismælir ferða")

    risk = 0
    reasons = []

    if not quakes.empty and float(quakes["size"].max()) >= 3:
        risk += 1
        reasons.append("Skjálfti yfir M3 hefur mælst.")
    if not traffic.empty and (traffic["severity"] == "red").any():
        risk += 2
        reasons.append("Rauður færðarpunktur fannst.")
    if not alerts.empty and alerts.iloc[0].get("level") != "green":
        risk += 2
        reasons.append("Veðurviðvörun gæti verið í gildi.")

    if risk <= 0:
        st.success("Grænt: Ekkert stórt flagg í gögnunum okkar.")
    elif risk <= 2:
        st.warning("Gult: Skoða gögn betur áður en farið er af stað.")
    else:
        st.error("Rautt: Þarf að skoða opinberar viðvaranir og færð áður en ferð er skipulögð.")

    if reasons:
        for r in reasons:
            st.caption(f"• {r}")
    else:
        st.caption("Mælirinn er einföld kennsluútgáfa og kemur ekki í stað opinberra upplýsinga.")
