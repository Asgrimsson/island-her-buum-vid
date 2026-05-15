
from __future__ import annotations

from datetime import datetime
import streamlit as st


def render_data_explorer(cameras, quakes, traffic, weather, alerts):
    st.subheader("🧭 Gagnaskoðari")
    st.caption("Skoðaðu lifandi gögnin sem töflur, leitaðu í þeim og sæktu sem CSV.")

    datasets = {
        "📷 Myndavélar": (cameras, "name", "myndavelar.csv"),
        "🌋 Jarðskjálftar": (quakes, "place", "jardskjalftar.csv"),
        "🚗 Færð / umferð": (traffic, "name", "faerd-umferd.csv"),
        "🌦️ Veður": (weather, "station", "vedur.csv"),
        "⚠️ Viðvaranir": (alerts, "title", "vidvaranir.csv"),
    }

    dataset = st.selectbox("Veldu gagnasafn", list(datasets.keys()), key="data_explorer_dataset")
    df, search_col, filename = datasets[dataset]
    df = df.copy()

    q = st.text_input("Leita í gögnum", placeholder="Sláðu inn leitarorð...", key="data_explorer_search")
    if q and search_col in df.columns:
        df = df[df[search_col].astype(str).str.contains(q, case=False, na=False)]

    c1, c2, c3 = st.columns(3)
    c1.metric("Raðir", len(df))
    c2.metric("Dálkar", len(df.columns))
    c3.metric("Uppfært", datetime.now().strftime("%H:%M"))

    st.dataframe(df, use_container_width=True, hide_index=True, height=420)

    if not df.empty:
        st.download_button(
            "⬇️ Sækja gögn sem CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )

    with st.expander("💡 Kennsluhugmynd úr þessum gögnum"):
        ideas = {
            "🌋 Jarðskjálftar": "Láttu nemendur finna stærsta skjálftann, staðsetja hann á korti og skrifa 5 setningar um hvað gögnin segja.",
            "📷 Myndavélar": "Láttu nemendur velja þrjár myndavélar, bera saman aðstæður og ákveða hvort ferð væri skynsamleg.",
            "🚗 Færð / umferð": "Láttu nemendur flokka vegi í grænt/gult/rautt og rökstyðja ferðarákvörðun.",
            "🌦️ Veður": "Láttu nemendur bera saman veðurstöðvar og finna hvar veður er hagstæðast fyrir útikennslu.",
            "⚠️ Viðvaranir": "Láttu nemendur lesa viðvörun og búa til einfalda öryggisáætlun fyrir skólaferðalag.",
        }
        st.write(ideas.get(dataset, "Búðu til rannsóknarspurningu úr gögnunum."))
