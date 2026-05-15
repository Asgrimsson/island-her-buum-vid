
from __future__ import annotations

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


def _fmt(n):
    try:
        return f"{int(float(n)):,}".replace(",", ".")
    except Exception:
        return str(n)


def render_traffic_numbers(counters: pd.DataFrame, fallback: bool, message: str):
    st.subheader("🚦 Umferðartölur á vegum landsins")
    st.caption("Umferðarteljarar Vegagerðarinnar — nálægt rauntíma þegar teljarar skila gögnum.")
    st.info("Kortatalan er nú skýrð sem tímabil: helst **Í dag** = fjöldi ökutækja frá miðnætti að síðustu uppfærslu. Einnig má sjá **síðustu 15 mínútur**, **í gær** og **síðustu 7 daga** í sprettiglugga/töflu.")

    if fallback:
        st.warning(message)
    else:
        st.success(message)

    if counters is None or counters.empty:
        st.error("Engin umferðartölugögn fundust.")
        return

    values = pd.to_numeric(counters.get("traffic_value", 0), errors="coerce").fillna(0)
    total = int(values.sum())
    active = int((values > 0).sum())
    coord_count = int(counters[["lat", "lon"]].notna().all(axis=1).sum()) if {"lat", "lon"}.issubset(counters.columns) else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Teljarar", len(counters))
    m2.metric("Með hnit", coord_count)
    m3.metric("Teljarar með mæligildi", active)
    m4.metric("Samtala mæligilda", _fmt(total))

    tab_map, tab_table, tab_tasks = st.tabs(["🗺️ Kort", "📋 Tafla", "🎒 Verkefni"])

    with tab_map:
        df = counters.dropna(subset=["lat", "lon"]).copy() if {"lat", "lon"}.issubset(counters.columns) else pd.DataFrame([])
        if df.empty:
            st.info("Engin hnit fundust fyrir teljara í þessari keyrslu. Notaðu töfluna til að skoða gögnin.")
        else:
            m = folium.Map(location=[64.8, -18.8], zoom_start=6, tiles="CartoDB positron")
            max_val = max(float(pd.to_numeric(df["traffic_value"], errors="coerce").fillna(0).max()), 1)

            for _, row in df.iterrows():
                val = float(row.get("traffic_value") or 0)
                radius = 5 + min(14, (val / max_val) * 14)
                popup = f"""
                <b>🚦 {row.get('name','Umferðarteljari')}</b><br>
                <b>Vegur:</b> {row.get('road','')}<br>
                <b>Svæði:</b> {row.get('region','')}<br>
                <b>Mæligildi:</b> {_fmt(row.get('traffic_value',0))}<br>
                <b>Dálkur:</b> {row.get('traffic_field','')}<br>
                """
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=radius,
                    color="#f97316",
                    fill=True,
                    fill_opacity=0.72,
                    tooltip=f"{row.get('name')} — {_fmt(row.get('traffic_value',0))}",
                    popup=popup,
                ).add_to(m)

                # Always show visible label, also for fallback/sample values.
                if True:
                    folium.Marker(
                        location=[row["lat"], row["lon"]],
                        icon=folium.DivIcon(html=f"""
                        <div style="
                            transform: translate(10px,-18px);
                            background: rgba(255,255,255,.94);
                            border: 1px solid rgba(249,115,22,.38);
                            border-radius: 10px;
                            padding: 3px 7px;
                            font-size: 11px;
                            font-weight: 900;
                            color: #7c2d12;
                            box-shadow: 0 4px 12px rgba(15,23,42,.16);
                            white-space: nowrap;">
                            🚦 {_fmt(val)}
                        </div>
                        """)
                    ).add_to(m)

            st_folium(m, width=None, height=620, returned_objects=[])

    with tab_table:
        q = st.text_input("Leita að teljara / vegi / svæði", placeholder="t.d. Selfoss, Hringvegur, 1...", key="traffic_numbers_search")
        df = counters.copy()
        if q:
            qlow = q.lower()
            mask = pd.Series(False, index=df.index)
            for col in ["name", "road", "region", "traffic_field"]:
                if col in df.columns:
                    mask = mask | df[col].astype(str).str.lower().str.contains(qlow, na=False)
            df = df[mask]

        show_cols = [c for c in [
            "name", "road", "region", "direction", "station_type",
            "traffic_label", "traffic_period", "latest_time",
            "umf_15min", "umf_i_dag", "medalhradi_15min",
            "umf_dagur1", "umf_dagur2", "umf_dagur3", "umf_dagur4", "umf_dagur5", "umf_dagur6", "umf_dagur7",
            "lat", "lon", "source"
        ] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Sækja umferðartölur sem CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="umferdartolur-vegir.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with tab_tasks:
        st.markdown("""
### Verkefnahugmyndir

**1. Hvar er mest umferð?**  
Finnið þrjá teljara með hæstu mæligildin. Hvar eru þeir á landinu?

**2. Umferð og landafræði**  
Berið saman teljara nálægt höfuðborgarsvæðinu og teljara úti á landi. Hvað gæti skýrt muninn?

**3. Ferðaleið og umferð**  
Búið til ferðaleið í Ferðaleiðangri og skoðið hvort umferðarteljarar eru á leiðinni.

**4. Umferð, veður og færð**  
Veljið einn stað þar sem umferð er mikil. Skoðið veður og færð. Er eitthvað sem gæti haft áhrif á akstur?

**5. Tölfræðiverkefni**  
Reiknið meðaltal eða finnið hæsta/lægsta mæligildi í töflunni.
""")
