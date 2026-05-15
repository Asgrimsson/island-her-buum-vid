
from __future__ import annotations

import streamlit as st


def render_full_data_activation(statuses: dict, cameras, quakes, traffic, weather, alerts, weather_texts=None):
    st.subheader("🛰️ Full Data Activation")
    st.caption("Yfirlit yfir gagnatengingar, virkni og hvaða endapunktar svara.")

    total = len(statuses)
    live = sum(1 for fallback, _ in statuses.values() if not fallback)
    fallback = total - live

    c1, c2, c3 = st.columns(3)
    c1.metric("Virk gagnalög", live)
    c2.metric("Fallback/sýnidæmi", fallback)
    c3.metric("Heildarlög", total)

    for name, (is_fallback, message) in statuses.items():
        if is_fallback:
            with st.expander(f"⚠️ {name} — fallback", expanded=True):
                st.warning(message)
        else:
            with st.expander(f"✅ {name} — virkt", expanded=False):
                st.success(message)

    st.markdown("### Gagnamagn")
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Myndavélar", len(cameras))
    d2.metric("Skjálftar", len(quakes))
    d3.metric("Færð", len(traffic))
    d4.metric("Veður", len(weather))
    d5.metric("Viðvaranir", len(alerts))

    st.metric("Textaspár", 0 if weather_texts is None else len(weather_texts))

    st.markdown("### Næstu gagnatengingar")
    st.info("""
Næst er hægt að bæta við:
- fleiri Veðurstofu-endapunktum fyrir viðvaranir eftir svæðum
- úrkomu / radar myndum
- Vegagerðar vefmyndum sem thumbnails í spjöldum
- sögulegum gögnum fyrir samanburð milli daga
- sjálfvirkri gagnaprófun við ræsingu
""")
