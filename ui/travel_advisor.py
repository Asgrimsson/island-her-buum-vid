
from __future__ import annotations

import math
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


VALLASKOLI = {"name": "Vallaskóli / Selfoss", "lat": 63.933, "lon": -20.997}

DESTINATIONS = {
    "Reykjavík": {"lat": 64.1466, "lon": -21.9426, "roads": ["1"], "region": "Höfuðborgarsvæði"},
    "Hveragerði": {"lat": 64.0005, "lon": -21.1860, "roads": ["1"], "region": "Suðurland"},
    "Þorlákshöfn": {"lat": 63.8556, "lon": -21.3831, "roads": ["38"], "region": "Suðurland"},
    "Eyrarbakki": {"lat": 63.8632, "lon": -21.1481, "roads": ["34"], "region": "Suðurland"},
    "Stokkseyri": {"lat": 63.8374, "lon": -21.0647, "roads": ["34"], "region": "Suðurland"},
    "Hella": {"lat": 63.8357, "lon": -20.4008, "roads": ["1"], "region": "Suðurland"},
    "Hvolsvöllur": {"lat": 63.7533, "lon": -20.2242, "roads": ["1"], "region": "Suðurland"},
    "Vík í Mýrdal": {"lat": 63.4186, "lon": -19.0060, "roads": ["1"], "region": "Suðurland"},
    "Geysir": {"lat": 64.3103, "lon": -20.3024, "roads": ["35", "37"], "region": "Suðurland"},
    "Gullfoss": {"lat": 64.3271, "lon": -20.1199, "roads": ["35"], "region": "Suðurland"},
    "Þingvellir": {"lat": 64.2559, "lon": -21.1295, "roads": ["36"], "region": "Suðurland"},
    "Landeyjahöfn": {"lat": 63.5311, "lon": -20.1088, "roads": ["254"], "region": "Suðurland"},
    "Skógar": {"lat": 63.5320, "lon": -19.5114, "roads": ["1"], "region": "Suðurland"},
    "Kirkjubæjarklaustur": {"lat": 63.7886, "lon": -18.0586, "roads": ["1"], "region": "Suðurland"},
}

ROUTE_PRESETS = {
    "Reykjavík": ["Selfoss", "Hveragerði", "Hellisheiði", "Reykjavík"],
    "Hveragerði": ["Selfoss", "Hveragerði"],
    "Þorlákshöfn": ["Selfoss", "Þorlákshöfn"],
    "Eyrarbakki": ["Selfoss", "Eyrarbakki"],
    "Stokkseyri": ["Selfoss", "Stokkseyri"],
    "Hella": ["Selfoss", "Hella"],
    "Hvolsvöllur": ["Selfoss", "Hella", "Hvolsvöllur"],
    "Vík í Mýrdal": ["Selfoss", "Hella", "Hvolsvöllur", "Skógar", "Vík í Mýrdal"],
    "Geysir": ["Selfoss", "Laugarvatn", "Geysir"],
    "Gullfoss": ["Selfoss", "Laugarvatn", "Geysir", "Gullfoss"],
    "Þingvellir": ["Selfoss", "Laugarvatn", "Þingvellir"],
    "Landeyjahöfn": ["Selfoss", "Hvolsvöllur", "Landeyjahöfn"],
    "Skógar": ["Selfoss", "Hella", "Hvolsvöllur", "Skógar"],
    "Kirkjubæjarklaustur": ["Selfoss", "Hella", "Hvolsvöllur", "Vík í Mýrdal", "Kirkjubæjarklaustur"],
}

ROUTE_POINTS = {
    "Selfoss": (63.933, -20.997),
    "Hveragerði": (64.0005, -21.1860),
    "Hellisheiði": (64.035, -21.36),
    "Reykjavík": (64.1466, -21.9426),
    "Þorlákshöfn": (63.8556, -21.3831),
    "Eyrarbakki": (63.8632, -21.1481),
    "Stokkseyri": (63.8374, -21.0647),
    "Hella": (63.8357, -20.4008),
    "Hvolsvöllur": (63.7533, -20.2242),
    "Skógar": (63.5320, -19.5114),
    "Vík í Mýrdal": (63.4186, -19.0060),
    "Kirkjubæjarklaustur": (63.7886, -18.0586),
    "Laugarvatn": (64.214, -20.733),
    "Geysir": (64.3103, -20.3024),
    "Gullfoss": (64.3271, -20.1199),
    "Þingvellir": (64.2559, -21.1295),
    "Landeyjahöfn": (63.5311, -20.1088),
}


def _haversine(lat1, lon1, lat2, lon2):
    r = 6371
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _nearest(df, lat, lon, n=5, max_km=60):
    if df is None or df.empty or "lat" not in df.columns or "lon" not in df.columns:
        return pd.DataFrame([])

    out = df.copy()
    out["distance_km"] = out.apply(
        lambda r: _haversine(lat, lon, float(r["lat"]), float(r["lon"]))
        if pd.notna(r.get("lat")) and pd.notna(r.get("lon")) else 9999,
        axis=1
    )
    out = out[out["distance_km"] <= max_km]
    return out.sort_values("distance_km").head(n).reset_index(drop=True)


def _route_distance(route_points):
    total = 0
    for a, b in zip(route_points[:-1], route_points[1:]):
        total += _haversine(a[0], a[1], b[0], b[1])
    return round(total * 1.18, 1)  # rough road factor


def _score_trip(traffic_near, weather_near, cameras_near, destination, route_roads):
    score = 100
    reasons = []

    if traffic_near is None or traffic_near.empty:
        score -= 12
        reasons.append("Engir nærliggjandi umferðarpunktar fundust.")
    else:
        values = pd.to_numeric(traffic_near.get("traffic_value", 0), errors="coerce").fillna(0)
        high = values.max() if len(values) else 0
        if high > 5000:
            score -= 20
            reasons.append("Mikil umferð virðist vera á einum eða fleiri punktum.")
        elif high > 1500:
            score -= 10
            reasons.append("Nokkur umferð er á leiðinni.")

    if weather_near is None or weather_near.empty:
        score -= 10
        reasons.append("Veðurstöðvar í nágrenni fundust ekki í þessari keyrslu.")
    else:
        # Generic warning: we don't know exact schema, but presence helps.
        reasons.append("Veðurgögn í nágrenni fundust og ætti að skoða þau fyrir ferð.")

    if cameras_near is None or cameras_near.empty:
        score -= 6
        reasons.append("Engar nærliggjandi myndavélar fundust.")
    else:
        reasons.append("Myndavélar í nágrenni fundust og hægt er að skoða færð sjónrænt.")

    # Destination-specific educational risk notes.
    if destination in ["Vík í Mýrdal", "Skógar", "Kirkjubæjarklaustur"]:
        score -= 6
        reasons.append("Leiðin er löng og getur orðið veðurviðkvæm á Suðurströnd.")
    if destination in ["Landeyjahöfn"]:
        score -= 10
        reasons.append("Landeyjahöfn tengist ferjusiglingum og veður/sjór geta skipt miklu máli.")
    if destination in ["Gullfoss", "Geysir", "Þingvellir"]:
        score -= 4
        reasons.append("Ferðamannaleiðir geta verið annasamar og veður/færð skipta máli.")
    if "1" in route_roads:
        reasons.append("Leiðin notar Hringveg/Suðurlandsveg sem er mikilvæg stofnleið.")

    if score >= 78:
        light = "🟢 Grænt"
        title = "Góð ferð — miðað við gögnin sem náðust."
    elif score >= 55:
        light = "🟡 Gult"
        title = "Fylgjast betur með áður en lagt er af stað."
    else:
        light = "🔴 Rautt"
        title = "Skoða þarf aðstæður betur eða velja aðra leið."

    return score, light, title, reasons


def render_travel_advisor(
    places=None,
    weather=None,
    traffic=None,
    cameras=None,
    traffic_counters=None,
    south_road_network=None,
    road_network=None,
):
    st.subheader("🧭 Ferðaráð Vallaskóla")
    st.caption("Gagnastudd ferðaráðgjöf fyrir kennslu — tengir saman vegi, umferð, veður, myndavélar og landafræði.")

    st.info(
        "Veldu áfangastað frá Vallaskóla/Selfossi. Kerfið býr til einfalt ferðaljósamat og bendir á gögn sem nemendur þurfa að skoða. "
        "Þetta er kennslumat, ekki opinber ferðaráðgjöf."
    )

    left, right = st.columns([0.38, 0.62], gap="large")

    with left:
        destination = st.selectbox("Veldu áfangastað", list(DESTINATIONS.keys()), index=list(DESTINATIONS.keys()).index("Vík í Mýrdal"))
        group_size = st.number_input("Fjöldi nemenda í ferð", min_value=1, max_value=200, value=25, step=1)
        trip_type = st.selectbox("Tegund ferðar", ["Stutt vettvangsferð", "Dagsferð", "Lengri rannsóknarferð", "Sýndarferð í kennslustund"])
        require_three_data = st.checkbox("Nemendur þurfa að nota minnst þrjú gagnalög", value=True)

    dest = DESTINATIONS[destination]
    route_names = ROUTE_PRESETS.get(destination, ["Selfoss", destination])
    route_coords = [ROUTE_POINTS[name] for name in route_names if name in ROUTE_POINTS]
    route_roads = dest.get("roads", [])

    # Nearby data around route destination and route points.
    traffic_near = _nearest(traffic_counters, dest["lat"], dest["lon"], n=8, max_km=70)
    weather_near = _nearest(weather, dest["lat"], dest["lon"], n=5, max_km=80)
    cameras_near = _nearest(cameras, dest["lat"], dest["lon"], n=6, max_km=80)

    score, light, title, reasons = _score_trip(traffic_near, weather_near, cameras_near, destination, route_roads)
    distance = _route_distance(route_coords) if len(route_coords) >= 2 else round(_haversine(VALLASKOLI["lat"], VALLASKOLI["lon"], dest["lat"], dest["lon"]) * 1.18, 1)

    with right:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ferðaljós", light)
        c2.metric("Mat", f"{score}/100")
        c3.metric("Áætluð vegalengd", f"{distance} km")
        c4.metric("Vegir", ", ".join(route_roads) if route_roads else "—")

        st.markdown(f"### {title}")
        for r in reasons:
            st.write(f"- {r}")

    tab_map, tab_data, tab_student, tab_classroom = st.tabs(["🗺️ Leiðarkort", "🔎 Gögn á leið", "🎒 Nemendaverkefni", "📋 Classroom texti"])

    with tab_map:
        m = folium.Map(location=[63.9, -20.5], zoom_start=8, tiles="OpenStreetMap")

        if len(route_coords) >= 2:
            folium.PolyLine(
                route_coords,
                color="#7c3aed",
                weight=6,
                opacity=0.82,
                tooltip=f"Leið: {' → '.join(route_names)}",
            ).add_to(m)

        # Add points
        for idx, name in enumerate(route_names):
            if name not in ROUTE_POINTS:
                continue
            lat, lon = ROUTE_POINTS[name]
            folium.Marker(
                [lat, lon],
                tooltip=f"{idx+1}. {name}",
                popup=f"<b>{idx+1}. {name}</b><br>Hluti af ferðaleiðinni.",
                icon=folium.Icon(color="green" if idx == 0 else "purple", icon="flag"),
            ).add_to(m)

        # Traffic counters with labels
        if traffic_near is not None and not traffic_near.empty:
            for _, row in traffic_near.iterrows():
                try:
                    lat = float(row["lat"])
                    lon = float(row["lon"])
                except Exception:
                    continue
                label = row.get("traffic_label", "umferð")
                folium.CircleMarker(
                    [lat, lon],
                    radius=9,
                    color="#f97316",
                    fill=True,
                    fill_opacity=0.78,
                    tooltip=f"🚦 {row.get('name','Teljari')} — {label}",
                    popup=f"""
                    <b>🚦 {row.get('name','Umferðarteljari')}</b><br>
                    Vegur: {row.get('road','')}<br>
                    Tímabil: {row.get('traffic_period','')}<br>
                    Kortatala: {label}<br>
                    Síðasta uppfærsla: {row.get('latest_time','')}<br>
                    Fjarlægð frá áfangastað: {round(row.get('distance_km',0),1)} km
                    """,
                ).add_to(m)
                folium.Marker(
                    [lat, lon],
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
                        🚦 {label}
                    </div>
                    """)
                ).add_to(m)

        st_folium(m, width=None, height=650, returned_objects=[])

    with tab_data:
        st.markdown("### 🚦 Næstu umferðarpunktar")
        if traffic_near is None or traffic_near.empty:
            st.warning("Engir umferðarpunktar fundust nálægt áfangastaðnum.")
        else:
            cols = [c for c in ["name", "road", "traffic_label", "traffic_period", "latest_time", "umf_15min", "umf_i_dag", "umf_dagur1", "distance_km"] if c in traffic_near.columns]
            st.dataframe(traffic_near[cols], use_container_width=True, hide_index=True)

        st.markdown("### 🌦️ Næstu veðurstöðvar")
        if weather_near is None or weather_near.empty:
            st.warning("Engar veðurstöðvar fundust nálægt áfangastaðnum.")
        else:
            st.dataframe(weather_near.head(5), use_container_width=True, hide_index=True)

        st.markdown("### 📷 Næstu myndavélar")
        if cameras_near is None or cameras_near.empty:
            st.warning("Engar myndavélar fundust nálægt áfangastaðnum.")
        else:
            st.dataframe(cameras_near.head(6), use_container_width=True, hide_index=True)

    with tab_student:
        st.markdown(f"""
### Verkefni: Ferðaráð til {destination}

Þið eruð ferðaráð Vallaskóla. Ykkar hlutverk er að ákveða hvort ferð til **{destination}** sé góð hugmynd í dag.

**Leið:** {' → '.join(route_names)}  
**Áætluð vegalengd:** {distance} km  
**Ferðaljós kerfisins:** {light}  
**Mat:** {score}/100

#### Þið þurfið að svara:
1. Hvaða vegi/notið þið á leiðinni?
2. Hvað segja umferðartölurnar?
3. Hvað segja veður- eða myndavélagögn?
4. Hvaða staðir eru mikilvægir á leiðinni?
5. Mynduð þið gefa ferðinni grænt, gult eða rautt ljós? Rökstyðjið.

#### Skilyrði:
{"Notið að minnsta kosti þrjú gagnalög úr vefnum." if require_three_data else "Notið að minnsta kosti eitt gagnalag úr vefnum."}
""")

    with tab_classroom:
        classroom = f"""Ferðaráð Vallaskóla — {destination}

Við ætlum að skoða hvort ferð frá Vallaskóla/Selfossi til {destination} sé góð hugmynd.

Leið:
{' → '.join(route_names)}

Áætluð vegalengd:
{distance} km

Ferðaljós kerfisins:
{light}

Gögn sem á að skoða:
- Vegir og leiðir
- Umferðartölur
- Veður
- Myndavélar
- Staðir og bæir
- Færð, ef hún er tiltæk

Verkefni:
1. Hvaða vegir eru á leiðinni?
2. Hvað segja umferðartölurnar?
3. Hvað segja veður- eða myndavélagögn?
4. Hvaða áhættur eða atriði þarf að fylgjast með?
5. Gefið ferðinni grænt, gult eða rautt ljós og rökstyðjið með gögnum.
"""
        st.code(classroom, language="markdown")
        st.download_button(
            "⬇️ Sækja Classroom texta",
            data=classroom.encode("utf-8"),
            file_name=f"ferdarad-vallaskola-{destination.lower().replace(' ', '-')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
