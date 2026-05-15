
from __future__ import annotations

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


def _haversine(lat1, lon1, lat2, lon2):
    import math
    r = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _road_factor_for_segment(a_region: str, b_region: str) -> float:
    regions = {a_region, b_region}
    if "Vestfirðir" in regions:
        return 1.55
    if "Austurland" in regions:
        return 1.42
    if "Norðurland eystra" in regions or "Norðurland vestra" in regions:
        return 1.35
    if "Suðurland" in regions or "Höfuðborgarsvæði" in regions or "Suðurnes" in regions:
        return 1.18
    return 1.30


def _make_route_df(places, selected_names):
    selected = places.set_index("name").loc[selected_names].reset_index()
    rows = []
    total_line = 0
    total_road = 0

    for i in range(len(selected) - 1):
        a = selected.iloc[i]
        b = selected.iloc[i + 1]
        line = _haversine(a["lat"], a["lon"], b["lat"], b["lon"])
        factor = _road_factor_for_segment(a["region"], b["region"])
        road = line * factor
        total_line += line
        total_road += road
        rows.append({
            "frá": a["name"],
            "til": b["name"],
            "loftlína_km": round(line, 1),
            "áætluð_akstursvegalengd_km": round(road, 1),
            "athugasemd": "Áætlun, ekki nákvæm vegaleið.",
        })

    return pd.DataFrame(rows), round(total_line, 1), round(total_road, 1), selected


def render_route_mission(places, weather=None, traffic=None, cameras=None):
    st.subheader("🧭 Ferðaleiðangur")
    st.caption("Búðu til ferðaleið milli staða og láttu nemendur rökstyðja hana með landafræði og lifandi gögnum.")

    st.info(
        "Vegalengdir hér eru merktar sérstaklega: **loftlína** er reiknuð nákvæmlega út frá hnitum, "
        "en **áætluð akstursvegalengd** er kennsluáætlun og ekki nákvæm vegaleið."
    )

    default_route = ["Selfoss", "Hveragerði", "Reykjavík", "Borgarnes", "Akureyri"]
    available = places["name"].tolist()

    selected = st.multiselect(
        "Veldu staði í ferðaleið",
        available,
        default=[x for x in default_route if x in available],
        key="route_mission_places",
    )

    if len(selected) < 2:
        st.warning("Veldu að minnsta kosti tvo staði.")
        return

    route_df, total_line, total_road, selected_df = _make_route_df(places, selected)

    c1, c2, c3 = st.columns(3)
    c1.metric("Stopp", len(selected))
    c2.metric("Heildarloftlína", f"{total_line} km")
    c3.metric("Áætlaður akstur", f"{total_road} km")

    m = folium.Map(location=[64.8, -18.8], zoom_start=6, tiles="CartoDB positron")

    coords = []
    for i, row in selected_df.iterrows():
        coords.append([row["lat"], row["lon"]])
        folium.Marker(
            location=[row["lat"], row["lon"]],
            tooltip=f"{i+1}. {row['name']}",
            popup=f"<b>{i+1}. {row['name']}</b><br>{row['region']}<br>{row['note']}",
            icon=folium.Icon(color="purple" if i not in [0, len(selected_df)-1] else "green", icon="flag"),
        ).add_to(m)

    folium.PolyLine(coords, color="#7c3aed", weight=5, opacity=0.75, tooltip="Ferðaleið / loftlína").add_to(m)

    st_folium(m, width=None, height=560, returned_objects=[])

    st.markdown("### 📏 Leiðarkaflar")
    st.dataframe(route_df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Sækja ferðaleið sem CSV",
        data=route_df.to_csv(index=False).encode("utf-8"),
        file_name="route-mission.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("### 🎒 Verkefni fyrir nemendur")
    st.markdown(f"""
**Ferðaleið:** {' → '.join(selected)}

1. Hvaða landshluta farið þið um?
2. Hvaða staður er lengst frá Vallaskóla?
3. Hvaða kafli er lengstur?
4. Hvaða lifandi gögn þyrfti að skoða áður en lagt er af stað?
   - veður
   - færð
   - myndavélar
   - ár/farvegir
   - jarðskjálftar
5. Veljið eitt stopp og búið til stutt landafræðispjald um það.
6. Útskýrið muninn á **loftlínu** og **akstursvegalengd**.
""")

    with st.expander("📋 Texti til að setja í Google Classroom"):
        classroom = f"""Ferðaleiðangur — Vallaskóli Live Lab

Leið: {' → '.join(selected)}

Heildarloftlína: {total_line} km
Áætluð akstursvegalengd: {total_road} km

Verkefni:
1. Teiknið leiðina á kort.
2. Skráið landshluta sem þið farið um.
3. Finnið lengsta kaflann.
4. Skoðið lifandi gögn áður en þið ákveðið hvort ferðin sé örugg.
5. Útskýrið muninn á loftlínu og akstursvegalengd.
"""
        st.code(classroom, language="markdown")
