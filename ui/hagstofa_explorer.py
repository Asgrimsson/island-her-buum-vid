
from __future__ import annotations

import pandas as pd
import streamlit as st


def render_hagstofa_explorer(places: pd.DataFrame, population: pd.DataFrame, fallback: bool, message: str):
    st.subheader("📊 Hagstofa gögn")
    st.caption("Mannfjöldagögn tengd við staði og bæi í landafræðihlutanum.")

    if fallback:
        st.warning(message)
    else:
        st.success(message)

    tab_places, tab_raw, tab_compare, tab_tasks = st.tabs(["🏘️ Staðir + mannfjöldi", "📋 Hrá gögn", "⚖️ Samanburður", "🎒 Verkefni"])

    with tab_places:
        cols = [
            "name", "region", "municipality", "population",
            "population_year", "population_source", "population_hagstofa_name",
            "straight_line_from_vallaskoli_km", "estimated_road_from_vallaskoli_km"
        ]
        existing = [c for c in cols if c in places.columns]
        st.dataframe(places[existing].sort_values("region"), use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Sækja staði með mannfjölda sem CSV",
            data=places.to_csv(index=False).encode("utf-8"),
            file_name="stadir-med-mannfjolda.csv",
            mime="text/csv",
            use_container_width=True
        )

    with tab_raw:
        if population is None or population.empty:
            st.info("Engin hrá Hagstofugögn í þessari keyrslu.")
        else:
            q = st.text_input("Leita í Hagstofugögnum", placeholder="t.d. Selfoss, Akureyri, Vík...", key="hagstofa_raw_search")
            df = population.copy()
            if q:
                df = df[df["place_hagstofa"].astype(str).str.contains(q, case=False, na=False)]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Sækja hrá Hagstofugögn sem CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="hagstofa-mannfjoldi-byggdakjarnar.csv",
                mime="text/csv",
                use_container_width=True
            )

    with tab_compare:
        names = places["name"].tolist()
        default_a = "Selfoss" if "Selfoss" in names else names[0]
        default_b = "Akureyri" if "Akureyri" in names else names[min(1, len(names)-1)]

        c1, c2 = st.columns(2)
        with c1:
            a = st.selectbox("Staður A", names, index=names.index(default_a), key="compare_place_a")
        with c2:
            b = st.selectbox("Staður B", names, index=names.index(default_b), key="compare_place_b")

        row_a = places[places["name"] == a].iloc[0]
        row_b = places[places["name"] == b].iloc[0]

        ca, cb = st.columns(2)
        with ca:
            st.metric(a, row_a.get("population", "—"))
            st.caption(f"{row_a.get('region','')} · {row_a.get('population_source','')}")
        with cb:
            st.metric(b, row_b.get("population", "—"))
            st.caption(f"{row_b.get('region','')} · {row_b.get('population_source','')}")

        def _num_pop(x):
            try:
                return int(str(x).replace(".", "").replace("≈", "").strip())
            except Exception:
                return None

        pa = _num_pop(row_a.get("population"))
        pb = _num_pop(row_b.get("population"))

        if pa and pb:
            diff = abs(pa - pb)
            bigger = a if pa > pb else b
            st.info(f"{bigger} er fjölmennari. Munurinn er um {diff:,} íbúar.".replace(",", "."))
            chart_df = pd.DataFrame({"staður": [a, b], "íbúar": [pa, pb]})
            st.bar_chart(chart_df.set_index("staður"))

    with tab_tasks:
        st.markdown("""
### Verkefnahugmyndir

**1. Berðu saman tvo staði**  
Veldu Selfoss og annan stað. Hvað munar mörgum íbúum?

**2. Landshluti og byggð**  
Hvaða staðir í sama landshluta eru fjölmennastir?

**3. Íbúafjöldi og fjarlægð**  
Er staður sem er lengra frá Vallaskóla alltaf fámennari? Rökstyðjið.

**4. Ferðaleið + mannfjöldi**  
Búið til ferðaleið í Ferðaleiðangur og reiknið saman íbúafjölda staðanna á leiðinni.

**5. Spurning fyrir nemendur**  
Af hverju haldið þið að sumir staðir séu fjölmennari en aðrir?
""")
