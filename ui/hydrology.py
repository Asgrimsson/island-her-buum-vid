
from __future__ import annotations

import folium
import streamlit as st
from streamlit_folium import st_folium


def render_hydrology(hydro_live, rivers, fallback: bool, message: str, river_lines=None):
    st.subheader("💧 Vatnamælistöðvar, rennsli og helstu ár")
    st.caption("Vatnafar fyrir landafræði, náttúrufræði, öryggi og verkefnavinnu.")

    if fallback:
        st.warning(message)
    else:
        st.success(message)

    tab_map, tab_live, tab_rivers, tab_tasks = st.tabs(["🗺️ Árakort", "📍 Vatnamælistöðvar", "🏞️ Helstu ár", "🎒 Verkefni"])

    with tab_map:
        m = folium.Map(location=[64.8, -18.7], zoom_start=6, tiles="CartoDB positron")
        if river_lines is not None and not river_lines.empty:
            for _, row in river_lines.iterrows():
                coords = row.get("coords")
                if coords:
                    folium.PolyLine(
                        locations=coords,
                        color="#0ea5e9",
                        weight=4,
                        opacity=0.85,
                        tooltip=row.get("river", "Á"),
                        popup=f"<b>💧 {row.get('river','Á')}</b><br>{row.get('area','')}<br>{row.get('type','')}<br>{row.get('note','')}",
                    ).add_to(m)

        for _, row in rivers.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=7,
                color="#0ea5e9",
                fill=True,
                fill_opacity=0.85,
                tooltip=row["river"],
                popup=f"<b>{row['river']}</b><br>{row['area']}<br>{row['type']}<br>{row['note']}"
            ).add_to(m)
        st_folium(m, width=None, height=620, returned_objects=[])

    with tab_live:
        if hydro_live is None or hydro_live.empty:
            st.info("Engar vatnamælistöðvar náðust í þessari keyrslu.")
            st.write("Við höldum samt inni hlutanum svo hægt sé að tengja vélræna gagnaleið um leið og hún finnst.")
        else:
            st.dataframe(hydro_live, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Sækja vatnamælingar sem CSV",
                data=hydro_live.to_csv(index=False).encode("utf-8"),
                file_name="vatnamaelingar.csv",
                mime="text/csv",
                use_container_width=True
            )

    with tab_rivers:
        st.dataframe(rivers, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Sækja helstu ár sem CSV",
            data=rivers.to_csv(index=False).encode("utf-8"),
            file_name="helstu-ar-islands.csv",
            mime="text/csv",
            use_container_width=True
        )

    with tab_tasks:
        st.markdown("""
### Verkefnahugmyndir

**1. Ferðaráð Vallaskóla**  
Veljið eina á á Suðurlandi. Hvernig gæti vatnsrennsli, rigning eða leysingar haft áhrif á ferðalag?

**2. Jökulár vs. dragár**  
Berið saman Þjórsá, Hvítá, Jökulsá á Fjöllum og Sog. Hvað gæti valdið mismunandi rennsli?

**3. Flóðahætta**  
Veljið á sem getur tengst flóðum eða jökulhlaupum. Hvaða gögn þyrfti að fylgjast með?

**4. Kortaverkefni**  
Merkið helstu ár á Íslandskort og útskýrið hvaðan vatnið kemur og hvert það fer.

**5. Stærðfræði**  
Ef rennsli er 100 m³/s, hversu margir rúmmetrar renna framhjá á einni mínútu?
""")
