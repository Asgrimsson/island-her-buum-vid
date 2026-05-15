
from __future__ import annotations

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from services.road_network import road_style
from services.south_roads import get_south_route_guide, filter_south_traffic_counters


def _fmt(value):
    try:
        if value is None or str(value).lower() == "nan":
            return "—"
        return f"{int(float(value)):,}".replace(",", ".")
    except Exception:
        return str(value)


def _traffic_popup(row):
    return f"""
    <div style="font-family:system-ui;min-width:260px;">
      <h3 style="margin:0 0 8px 0;">🚦 {row.get('name','Umferðarteljari')}</h3>
      <div><b>Vegur:</b> {row.get('road','')}</div>
      <div><b>Kortatala:</b> {row.get('traffic_label','')}</div>
      <div><b>Tímabil:</b> {row.get('traffic_period','')}</div>
      <div><b>Síðasta uppfærsla:</b> {row.get('latest_time','')}</div>
      <hr>
      <div><b>Síðustu 15 mín:</b> {_fmt(row.get('umf_15min',''))}</div>
      <div><b>Frá miðnætti:</b> {_fmt(row.get('umf_i_dag',''))}</div>
      <div><b>Í gær:</b> {_fmt(row.get('umf_dagur1',''))}</div>
      <div><b>Meðalhraði 15 mín:</b> {_fmt(row.get('medalhradi_15min',''))} km/klst</div>
    </div>
    """


def render_south_roads(south_geojson, south_df, south_fallback, south_msg, traffic_counters=None):
    st.subheader("🛣️ Suðurlandsvegir")
    st.caption("Sérfókus á vegi, leiðir og umferðarpunkta á Suðurlandi — sérstaklega gagnlegt fyrir Vallaskóla/Selfoss.")

    if south_fallback:
        st.warning(south_msg)
    else:
        st.success(south_msg)

    guide = get_south_route_guide()
    south_counters = filter_south_traffic_counters(traffic_counters)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vegkaflar", 0 if south_df is None or south_df.empty else len(south_df))
    c2.metric("Vegnúmer", 0 if south_df is None or south_df.empty or "vegnumer" not in south_df else south_df["vegnumer"].nunique())
    c3.metric("Umferðarpunktar", 0 if south_counters is None or south_counters.empty else len(south_counters))
    c4.metric("Kennsluleiðir", len(guide))

    tab_map, tab_routes, tab_table, tab_traffic, tab_tasks = st.tabs([
        "🗺️ Suðurlandskort",
        "🧭 Helstu leiðir",
        "📋 Vegatafla",
        "🚦 Umferðarpunktar",
        "🎒 Verkefni"
    ])

    with tab_map:
        m = folium.Map(location=[63.88, -20.25], zoom_start=8, tiles="OpenStreetMap")

        if south_geojson and south_geojson.get("features"):
            def _popup(feature):
                p = feature.get("properties") or {}
                return folium.Popup(f"""
                <div style="font-family:system-ui;min-width:260px;">
                  <h3 style="margin:0 0 8px 0;">🛣️ Vegur {p.get('NUMVEGUR_LABEL', p.get('NUMVEGUR',''))}</h3>
                  <div><b>Heiti kafla:</b> {p.get('KAFLIVEGURHEITI','')}</div>
                  <div><b>Kafli:</b> {p.get('NUMKAFLI','')}</div>
                  <div><b>Lengd kafla:</b> {p.get('KAFLILENGD_KM','')} km</div>
                  <div><b>Vegflokkur:</b> {p.get('VEGFLOKKUR_TEXT','')}</div>
                  <div><b>Veghluti:</b> {p.get('VEGHLUTI_TEXT','')}</div>
                  <div><b>Stefna:</b> {p.get('STEFNA_TEXT','')}</div>
                </div>
                """, max_width=420)

            folium.GeoJson(
                south_geojson,
                name="🛣️ Suðurlandsvegir",
                style_function=road_style,
                tooltip=folium.GeoJsonTooltip(
                    fields=["NUMVEGUR_LABEL", "KAFLIVEGURHEITI", "VEGFLOKKUR_TEXT"],
                    aliases=["Vegur", "Kafli", "Flokkur"],
                    localize=True,
                    sticky=True,
                ),
                popup=_popup,
            ).add_to(m)

        if south_counters is not None and not south_counters.empty:
            max_val = max(float(pd.to_numeric(south_counters.get("traffic_value", 0), errors="coerce").fillna(0).max()), 1)
            for _, row in south_counters.iterrows():
                try:
                    lat = float(row.get("lat"))
                    lon = float(row.get("lon"))
                except Exception:
                    continue
                val = float(row.get("traffic_value") or 0)
                radius = 7 + min(17, (val / max_val) * 17)
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    color="#f97316",
                    fill=True,
                    fill_opacity=0.78,
                    tooltip=f"🚦 {row.get('name','Teljari')} — {row.get('traffic_label','')}",
                    popup=_traffic_popup(row),
                ).add_to(m)
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(html=f"""
                    <div style="
                        transform: translate(10px,-18px);
                        background: rgba(255,255,255,.96);
                        border: 2px solid rgba(249,115,22,.55);
                        border-radius: 11px;
                        padding: 4px 8px;
                        font-size: 12px;
                        font-weight: 950;
                        color: #7c2d12;
                        box-shadow: 0 5px 14px rgba(15,23,42,.22);
                        white-space: nowrap;">
                        🚦 {row.get('traffic_label','')}
                    </div>
                    """)
                ).add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)
        st_folium(m, width=None, height=680, returned_objects=[])

    with tab_routes:
        st.markdown("### Helstu leiðir á Suðurlandi")
        st.dataframe(guide, use_container_width=True, hide_index=True)
        for _, row in guide.iterrows():
            with st.expander(f"🧭 {row['heiti']} — vegur {row['vegur']}"):
                st.write(row["lysing"])
                st.info(row["kennsluhugmynd"])

    with tab_table:
        if south_df is None or south_df.empty:
            st.info("Engin vegatafla fannst.")
        else:
            q = st.text_input("Leita í Suðurlandsvegum", placeholder="t.d. Selfoss, Hringvegur, 1, Þorlákshöfn...", key="south_road_search")
            df = south_df.copy()
            if q:
                qlow = q.lower()
                mask = pd.Series(False, index=df.index)
                for col in df.columns:
                    mask = mask | df[col].astype(str).str.lower().str.contains(qlow, na=False)
                df = df[mask]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Sækja Suðurlandsvegi sem CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="sudurlandsvegir.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab_traffic:
        if south_counters is None or south_counters.empty:
            st.info("Engir umferðarpunktar fundust á Suðurlandssvæðinu í þessari keyrslu.")
        else:
            show_cols = [c for c in [
                "name", "road", "region", "traffic_label", "traffic_period", "latest_time",
                "umf_15min", "umf_i_dag", "umf_dagur1", "medalhradi_15min", "lat", "lon", "source"
            ] if c in south_counters.columns]
            st.dataframe(south_counters[show_cols], use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Sækja umferðarpunkta á Suðurlandi",
                data=south_counters.to_csv(index=False).encode("utf-8"),
                file_name="umferdarpunktar-sudurland.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab_tasks:
        st.markdown("""
### Verkefnahugmyndir — Suðurland

**1. Vallaskóli og samgöngur**  
Hvaða vegir skipta mestu máli fyrir nemendur og fjölskyldur á Selfossi?

**2. Ferð til Víkur**  
Veldu leið frá Selfossi til Víkur. Hvaða vegir, veðurstöðvar og umferðarpunktar skipta máli?

**3. Gullni hringurinn**  
Finndu helstu vegi Gullna hringsins og rökstuddu hvaða gögn þarf að skoða áður en farið er með bekk í ferð.

**4. Þórsmörk og vatnafar**  
Skoðaðu Þórsmerkurveg. Af hverju þarf að hugsa sérstaklega um ár, veður og færð þar?

**5. Umferð í dag**  
Finndu þrjá umferðarpunkta á Suðurlandi. Hver er með mesta umferð og hvað segir það okkur?

**6. Staðir + vegir**  
Veldu þrjá bæi á Suðurlandi og finndu hvaða vegir tengja þá saman.
""")
