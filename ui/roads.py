
from __future__ import annotations

import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium

from services.road_network import road_style
from ui.map import MAIN_ROADS


def _render_old_overview():
    m = folium.Map(location=[64.85, -18.8], zoom_start=6, tiles="OpenStreetMap")
    colors = ["#1d4ed8", "#16a34a", "#dc2626", "#9333ea", "#ea580c", "#0891b2", "#4f46e5"]
    for i, road in enumerate(MAIN_ROADS):
        folium.PolyLine(
            road["coords"],
            color=colors[i % len(colors)],
            weight=5,
            opacity=0.78,
            tooltip=f"{road['road']} — {road['name']}",
            popup=f"<b>🛣️ {road['name']}</b><br>Vegnúmer: {road['road']}<br>Fjöldi punkta: {len(road['coords'])}",
        ).add_to(m)
    return m


def render_roads(road_network=None, road_df=None, road_fallback=True, road_msg=""):
    st.subheader("🛣️ Vegir og leiðir")
    st.caption("Nákvæmari vegalínur frá Vegagerðinni þegar þjónustan svarar. Annars einfalt kennsluyfirlit.")

    if road_fallback:
        st.warning(road_msg or "Nákvæmar vegalínur náðust ekki — yfirlitslínur notaðar.")
    else:
        st.success(road_msg)

    if road_df is None:
        road_df = pd.DataFrame([])

    m1, m2, m3 = st.columns(3)
    m1.metric("Vegkaflar", 0 if road_df.empty else len(road_df))
    m2.metric("Vegnúmer", 0 if road_df.empty or "vegnumer" not in road_df else road_df["vegnumer"].nunique())
    m3.metric("Uppruni", "Vegagerðin" if not road_fallback else "Fallback")

    tab_map, tab_table, tab_tasks = st.tabs(["🗺️ Kort", "📋 Tafla", "🎒 Verkefni"])

    with tab_map:
        if road_network and road_network.get("features"):
            m = folium.Map(location=[64.85, -18.8], zoom_start=6, tiles="OpenStreetMap")

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
                road_network,
                name="Vegakerfi",
                style_function=road_style,
                tooltip=folium.GeoJsonTooltip(
                    fields=["NUMVEGUR_LABEL", "KAFLIVEGURHEITI", "VEGFLOKKUR_TEXT"],
                    aliases=["Vegur", "Kafli", "Flokkur"],
                    localize=True,
                    sticky=True,
                ),
                popup=_popup,
            ).add_to(m)
        else:
            m = _render_old_overview()

        st_folium(m, width=None, height=650, returned_objects=[])

    with tab_table:
        if road_df is None or road_df.empty:
            st.info("Engin tafla fannst fyrir vegalínur.")
        else:
            q = st.text_input("Leita að vegi/kafla", placeholder="t.d. 1, Suðurlandsvegur, Hringvegur...", key="roads_search")
            df = road_df.copy()
            if q:
                qlow = q.lower()
                mask = pd.Series(False, index=df.index)
                for col in df.columns:
                    mask = mask | df[col].astype(str).str.lower().str.contains(qlow, na=False)
                df = df[mask]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Sækja vegakafla sem CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="vegir-og-leidir-vegagerdin.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab_tasks:
        st.markdown("""
### Verkefnahugmyndir

**1. Smelltu á veg**  
Smelltu á veglínu og finndu vegnúmer, kaflaheiti og lengd kafla.

**2. Vegur 1**  
Leitaðu að vegi 1. Hvaða landshluta tengir hann saman?

**3. Umferðarpunktar og vegir**  
Kveiktu á umferðartölum á Íslandskorti. Berðu saman popup á vegi og popup á umferðarteljara.

**4. Ferðaleið**  
Veldu leið frá Selfossi til Akureyrar. Hvaða vegnúmer koma við sögu?

**5. Vegflokkar**  
Finndu stofnveg, tengiveg eða héraðsveg og útskýrðu muninn.
""")
