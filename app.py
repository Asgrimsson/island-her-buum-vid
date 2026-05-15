from __future__ import annotations

from datetime import datetime

import streamlit as st
from streamlit_folium import st_folium

from services.cameras import get_cameras
from services.earthquakes import get_earthquakes
from services.weather import get_weather
from services.traffic import get_traffic
from services.traffic_counters import get_traffic_counters
from services.road_network import get_road_network
from services.south_roads import get_south_road_network
from services.alerts import get_alerts
from services.weather_texts import get_weather_texts
from services.hydrology import get_hydrology
from services.river_lines import get_river_lines
from services.places import get_places
from services.hagstofa import get_hagstofa_population, apply_population_to_places, get_hagstofa_population_trends, build_place_trends

from ui.map import build_live_map
from ui.widgets import render_metric_row, render_data_health, render_risk_panel
from ui.sidebar import render_teacher_helper, render_quiz
from ui.missions import render_mission_mode
from ui.leaderboard import render_leaderboard
from ui.ai_tasks import render_ai_task_maker
from ui.teacher_center import render_teacher_center
from ui.data_explorer import render_data_explorer
from ui.full_data_activation import render_full_data_activation
from ui.realtime_lab import render_realtime_lab
from ui.hydrology import render_hydrology
from ui.quake_debug import render_quake_debug
from ui.geography import render_geography
from ui.route_mission import render_route_mission
from ui.hagstofa_explorer import render_hagstofa_explorer
from ui.geography_challenge import render_geography_challenge
from ui.teacher_mission_builder import render_teacher_mission_builder
from ui.settlement_trends import render_settlement_trends
from ui.classroom_export import render_classroom_export
from ui.reports import render_reports
from ui.traffic_numbers import render_traffic_numbers
from ui.roads import render_roads
from ui.south_roads import render_south_roads
from ui.travel_advisor import render_travel_advisor


st.set_page_config(
    page_title="Ísland hér búum við v4.3.2.1",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)



st.markdown("""
<style>
:root{
    --bg:#f5f8fc; --panel:#ffffff; --border:#dfe8f4; --text:#0f172a; --muted:#52637a;
    --blue:#0b78f0; --green:#16a34a; --red:#ef233c; --orange:#fb8500; --purple:#8b5cf6;
    --shadow:0 16px 42px rgba(15,23,42,.08);
}
html, body, .stApp{background:#f5f8fc !important;color:var(--text) !important;}
.block-container{padding-top:1.6rem !important;max-width:1580px;}
.hero-card{
    background:linear-gradient(180deg,#fff,#f8fbff);
    border:1px solid var(--border);
    border-radius:26px;
    padding:24px 26px;
    box-shadow:var(--shadow);
    margin-bottom:18px;
}
.hero-title{
    font-size:3.1rem;font-weight:950;color:#0f172a;letter-spacing:-0.06em;line-height:.95;margin:0;
}
.version-badge{
    display:inline-flex;align-items:center;padding:6px 11px;border-radius:12px;background:#eff6ff;
    border:1px solid #93c5fd;color:#0b78f0;font-weight:950;font-size:.95rem;margin-left:8px;vertical-align:middle;
}
.hero-subtitle{color:#475569;font-size:1.04rem;margin-top:8px;}
.system-card{
    background:white;border:1px solid var(--border);border-radius:18px;padding:14px 16px;box-shadow:var(--shadow);
    color:#0f172a;text-align:left;
}
.system-dot{width:13px;height:13px;background:#22c55e;border-radius:999px;display:inline-block;margin-right:8px;}
[data-testid="stMetric"]{
    background:white;border:1px solid var(--border);padding:18px 20px;border-radius:24px;
    box-shadow:var(--shadow);min-height:112px;
}
[data-testid="stMetricLabel"]{color:#334155;font-weight:800;}
[data-testid="stMetricValue"]{color:#0f172a;font-weight:950;}
div[data-testid="stExpander"]{
    background:white;border:1px solid var(--border);border-radius:20px;overflow:hidden;
    box-shadow:0 12px 34px rgba(15,23,42,.055);
}
.stTabs [data-baseweb="tab-list"]{gap:10px;border-bottom:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{background:transparent;color:#334155;font-weight:850;padding:12px 18px;border-radius:0;}
.stTabs [aria-selected="true"]{color:#0b78f0;border-bottom:3px solid #0b78f0;background:transparent;}
.stButton>button{
    border:none;background:linear-gradient(135deg,#0b78f0,#38bdf8);color:white;border-radius:14px;
    padding:0.72rem 1rem;font-weight:850;box-shadow:0 8px 24px rgba(37,99,235,.18);
}
.stTextInput input,.stTextArea textarea{
    border-radius:16px !important;border:1px solid var(--border) !important;background:white !important;color:#0f172a !important;
}
.stRadio > div{background:white;border:1px solid var(--border);padding:12px;border-radius:18px;}
.stAlert{border-radius:18px;}
.command-map{
    background:white;border-radius:26px;padding:16px;border:1px solid var(--border);box-shadow:var(--shadow);
}
.sidebar-card{
    background:white;border-radius:24px;border:1px solid var(--border);padding:14px;box-shadow:var(--shadow);
}
.small-note{color:#64748b;font-size:.88rem;}
hr{border:none;border-top:1px solid #dbe4f0;}
@media(max-width:900px){.hero-title{font-size:2.25rem;}}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#ffffff,#f7fbff) !important;
    border-right: 1px solid #dfe8f4;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #0f172a;
}
section[data-testid="stSidebar"] a {
    border-radius: 14px;
    font-weight: 800;
}


.sidebar-logo-wrap{
    background:#ffffff;
    border:1px solid #dfe8f4;
    border-radius:18px;
    padding:10px;
    margin-bottom:12px;
    box-shadow:0 10px 26px rgba(15,23,42,.06);
}
.sidebar-logo{
    width:100%;
    max-width:210px;
    display:block;
    margin:0 auto;
}
section[data-testid="stSidebar"] .stButton>button{
    justify-content:flex-start;
    text-align:left;
    background:#ffffff !important;
    color:#0f172a !important;
    border:1px solid #edf2f7 !important;
    box-shadow:none !important;
    border-radius:14px !important;
    margin:2px 0;
}
section[data-testid="stSidebar"] .stButton>button:hover{
    background:#eaf4ff !important;
    color:#075fc7 !important;
    border:1px solid #bfdbfe !important;
}

/* v4.3.2 Deployment Ready for Render — flokkuð valmynd */
section[data-testid="stSidebar"] details {
    background: rgba(255,255,255,.78);
    border: 1px solid #dbe7f5;
    border-radius: 16px;
    padding: 4px 8px;
    margin: 8px 0;
    box-shadow: 0 4px 14px rgba(15,23,42,.04);
}
section[data-testid="stSidebar"] summary {
    font-weight: 950 !important;
    color: #0f172a !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: white !important;
    color: #0f172a !important;
    border: 1px solid #dbe7f5 !important;
    box-shadow: none !important;
    border-radius: 12px !important;
    padding: .55rem .7rem !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #60a5fa !important;
    background: #eff6ff !important;
}

</style>
""", unsafe_allow_html=True)





LOGO_URL = "https://vallaskoli.is/wp-content/uploads/bb-plugin/cache/logo-med-hvitu-borda-2-300x156-landscape-1f88abc64591c414446c74a40697ddeb-5fc7b0eede877.png"

NAV_GROUPS = {
    "🌐 Lifandi gögn": [
        "🏠 Forsíða",
        "📍 Staðan núna",
        "📈 Gagnaheilsa",
        "🗺️ Íslandskort",
        "🛣️ Vegir og leiðir",
        "🛣️ Suðurlandsvegir",
        "🧭 Ferðaráð Vallaskóla",
        "🌋 Jarðskjálftabrú",
        "💧 Vatnafar og ár",
        "🧪 Skjálftaprófun",
    ],
    "🧭 Landafræði": [
        "🏘️ Staðir og bæir",
        "📊 Hagstofugögn",
        "📈 Byggðaþróun",
        "🧭 Ferðaleiðangur",
    ],
    "🎯 Verkefni og leikir": [
        "🎒 Verkefnaleiðangur",
        "🎯 Landafræðiáskorun",
        "👥 Lið og stig",
        "🏆 Stigalisti",
        "📋 Verkefni",
    ],
    "👨‍🏫 Kennari": [
        "👨‍🏫 Kennarastjórnborð",
        "🤖 Verkefnasmiður",
        "👨‍🏫 Verkefnabanki kennara",
        "📦 Útflutningur í Classroom",
    ],
    "⚙️ Kerfi": [
        "🧭 Gagnaskoðari",
        "📄 Skýrslur",
        "⚙️ Stillingar",
    ],
}

NAV_ITEMS = [item for group_items in NAV_GROUPS.values() for item in group_items]

if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "🏠 Forsíða"

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-logo-wrap">
          <img src="{LOGO_URL}" class="sidebar-logo" alt="Vallaskóli logo">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("### Ísland hér búum við")

    for group_name, group_items in NAV_GROUPS.items():
        expanded = st.session_state["selected_page"] in group_items or group_name in ["🌐 Lifandi gögn", "🧭 Landafræði"]
        with st.expander(group_name, expanded=expanded):
            for item in group_items:
                active = st.session_state["selected_page"] == item
                label = f"● {item}" if active else item
                if st.button(label, key=f"nav_button_{item}", use_container_width=True):
                    st.session_state["selected_page"] = item
                    st.rerun()

    st.divider()
    st.info("🏫 Vallaskóli Live Lab\n\nIceland Command Center\n\nv4.3.2\n\nKennsluútgáfa + flokkuð valmynd")

selected_page = st.session_state["selected_page"]

h1, h2 = st.columns([0.74, 0.26])
with h1:
    st.markdown("""
    <div class="hero-card">
      <div class="hero-title">🇮🇸 Ísland hér búum við <span class="version-badge">v4.3.2</span></div>
      <div class="hero-subtitle">Kennsluútgáfa — lifandi gögn, landafræði, verkefni, leikir og kennaratól á einum stað.</div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div class="system-card">
      <b><span class="system-dot"></span>Kerfi í gangi</b><br>
      <span style="color:#64748b;font-size:.86rem;">Síðasta uppfærsla: {datetime.now().strftime("%H:%M:%S")}</span>
    </div>
    """, unsafe_allow_html=True)

with st.spinner("Sæki lifandi gögn..."):
    cameras, cam_fallback, cam_msg = get_cameras()
    quakes, quake_fallback, quake_msg = get_earthquakes()
    weather, weather_fallback, weather_msg = get_weather()
    traffic, traffic_fallback, traffic_msg = get_traffic()
    traffic_counters, traffic_counters_fallback, traffic_counters_msg = get_traffic_counters()
    road_network, road_df, road_fallback, road_msg = get_road_network()
    south_road_network, south_road_df, south_road_fallback, south_road_msg = get_south_road_network()
    alerts, alert_fallback, alert_msg = get_alerts()
    weather_texts, weather_texts_fallback, weather_texts_msg = get_weather_texts()
    hydro_live, rivers, hydro_fallback, hydro_msg = get_hydrology()
    river_lines = get_river_lines()
    places = get_places()
    hagstofa_population, hagstofa_fallback, hagstofa_msg = get_hagstofa_population()
    places = apply_population_to_places(places, hagstofa_population)
    hagstofa_trends, trends_fallback, trends_msg = get_hagstofa_population_trends()
    place_trends = build_place_trends(places, hagstofa_trends)

statuses = {
    "📷 Myndavélar": (cam_fallback, cam_msg),
    "🌋 Jarðskjálftar": (quake_fallback, quake_msg),
    "🌦️ Veður": (weather_fallback, weather_msg),
    "🚗 Færð": (traffic_fallback, traffic_msg),
    "🚦 Umferðartölur": (traffic_counters_fallback, traffic_counters_msg),
    "🛣️ Vegalínur": (road_fallback, road_msg),
    "🛣️ Suðurlandsvegir": (south_road_fallback, south_road_msg),
    "⚠️ Viðvaranir": (alert_fallback, alert_msg),
    "📝 Textaspár": (weather_texts_fallback, weather_texts_msg),
    "💧 Vatnafar": (hydro_fallback, hydro_msg),
    "📊 Hagstofa mannfjöldi": (hagstofa_fallback, hagstofa_msg),
    "📈 Byggðaþróun": (trends_fallback, trends_msg),
}

render_metric_row(cameras, quakes, traffic, weather)

if any(v[0] for v in statuses.values()):
    st.warning("Sum gögn eru í fallback/sýnidæmum. Realtime Engine heldur samt áfram að virka fyrir kennslu.")
else:
    st.success("Allar kjarnatengingar svöruðu. Realtime Engine er lifandi.")

render_data_health(statuses)


def render_map_and_status():
    left, right = st.columns([1.45, 0.55], gap="large")

    with left:
        st.markdown('<div class="command-map">', unsafe_allow_html=True)
        st.subheader("🗺️ Iceland Command Map")

        c1, c2, c3, c4 = st.columns(4)
        show_cameras = c1.toggle("📷 Myndavélar", value=True, key="map_toggle_cameras")
        show_quakes = c2.toggle("🌋 Skjálftar", value=True, key="map_toggle_quakes")
        show_traffic = c3.toggle("🚗 Færð", value=True, key="map_toggle_traffic")
        show_weather = c4.toggle("🌦️ Veður", value=False, key="map_toggle_weather")

        c5, c6, c7 = st.columns(3)
        show_places = c5.toggle("🏘️ Staðir og bæir", value=True, key="map_toggle_places")
        show_rivers = c6.toggle("💧 Ár/farvegir", value=True, key="map_toggle_rivers")
        show_traffic_counters = c7.toggle("🚦 Umferðartölur", value=False, key="map_toggle_traffic_counters")
        show_exact_roads = st.toggle("🛣️ Nákvæmari vegalínur", value=True, key="map_toggle_exact_roads")
        show_school = st.toggle("🏫 Vallaskóli", value=True, key="map_toggle_school")

        m = build_live_map(
            cameras=cameras,
            quakes=quakes,
            traffic=traffic,
            traffic_counters=traffic_counters,
            weather=weather,
            places=places,
            river_lines=river_lines,
            road_network=road_network,
            show_cameras=show_cameras,
            show_quakes=show_quakes,
            show_traffic=show_traffic,
            show_traffic_counters=show_traffic_counters,
            show_weather=show_weather,
            show_places=show_places,
            show_rivers=show_rivers,
            show_exact_roads=show_exact_roads,
            show_school=show_school,
        )
        st_folium(m, width=None, height=720, returned_objects=[])
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.subheader("📍 Staðan núna")

        with st.expander("⚠️ Viðvaranir", expanded=True):
            for _, row in alerts.head(3).iterrows():
                st.write(f"**{row.get('title')}**")
                st.caption(row.get("summary", ""))

        render_risk_panel(alerts, quakes, traffic)

        with st.expander("📷 Myndavélar", expanded=False):
            for _, row in cameras.head(6).iterrows():
                st.write(f"**{row.get('name')}**")
                if row.get("road"):
                    st.caption(row.get("road"))

        with st.expander("🌋 Nýlegir skjálftar", expanded=False):
            for _, row in quakes.head(6).iterrows():
                st.write(f"**{row.get('place')}**")
                st.caption(f"Stærð: {row.get('size')} | {row.get('time')}")

        render_teacher_helper()
        render_quiz()
        st.markdown("</div>", unsafe_allow_html=True)


if selected_page == "🏠 Forsíða":
    st.markdown("""
    # 🏠 Kennsluútgáfa

    Velkomin í **Vallaskóli Live Lab**. Valmyndin er nú skipt í skýra kennsluflokka svo auðveldara sé að nota vefinn í kennslustund.

    **🌐 Lifandi gögn** — veður, færð, kort, jarðskjálftar og vatnafar.  
    **🧭 Landafræði** — staðir, bæir, Hagstofugögn, byggðaþróun og ferðaleiðir.  
    **🎯 Verkefni og leikir** — áskoranir, lið, stig og verkefni.  
    **👨‍🏫 Kennari** — verkefnasmiður, verkefnabanki og Classroom útflutningur.  
    **⚙️ Kerfi** — gagnaskoðari, skýrslur og stillingar.
    """)

    k1, k2, k3 = st.columns(3)
    with k1:
        st.info("📍 Byrjaðu á **Staðan núna** til að sjá lifandi gögn.")
    with k2:
        st.info("🏘️ Farðu í **Staðir og bæir** fyrir landafræði.")
    with k3:
        st.info("🎯 Notaðu **Landafræðiáskorun** fyrir hópverkefni.")

    st.markdown("### Fljótleg kennsluleið")
    st.write("1. Opnaðu **Íslandskort**.  \n2. Veldu gagnalög.  \n3. Farðu í **Staðir og bæir** eða **Byggðaþróun**.  \n4. Ljúktu með **Landafræðiáskorun** eða **Ferðaleiðangri**.")

elif selected_page in ["📍 Staðan núna", "🗺️ Íslandskort"]:
    render_map_and_status()

elif selected_page == "🛣️ Vegir og leiðir":
    render_roads(road_network, road_df, road_fallback, road_msg)

elif selected_page == "🧭 Ferðaráð Vallaskóla":
    render_travel_advisor(
        places=places,
        weather=weather,
        traffic=traffic,
        cameras=cameras,
        traffic_counters=traffic_counters,
        south_road_network=south_road_network,
        road_network=road_network,
    )

elif selected_page in ["🛣️ Suðurlandsvegir", "Suðurlandsvegir"]:
    render_south_roads(south_road_network, south_road_df, south_road_fallback, south_road_msg, traffic_counters)

elif selected_page == "🚦 Umferðartölur":
    render_traffic_numbers(traffic_counters, traffic_counters_fallback, traffic_counters_msg)

elif selected_page == "📈 Gagnaheilsa":
    st.subheader("📈 Gagnaheilsa / Realtime Engine")
    render_data_health(statuses)
    render_data_explorer(cameras, quakes, traffic, weather, alerts)

elif selected_page == "🎒 Verkefnaleiðangur":
    render_mission_mode(cameras, quakes, traffic, alerts)

elif selected_page in ["👥 Lið og stig", "🏆 Stigalisti"]:
    render_leaderboard()

elif selected_page == "📋 Verkefni":
    st.subheader("📋 Verkefni")
    st.info("Verkefni eru vistuð og stýrð í Kennarastjórnborði.")
    render_teacher_center()

elif selected_page == "👨‍🏫 Kennarastjórnborð":
    render_teacher_center()

elif selected_page == "🤖 Verkefnasmiður":
    render_ai_task_maker(cameras, quakes, traffic, alerts)

elif selected_page == "📦 Útflutningur í Classroom":
    render_classroom_export(cameras, quakes, traffic, alerts)

elif selected_page == "🧭 Gagnaskoðari":
    render_data_explorer(cameras, quakes, traffic, weather, alerts)

elif selected_page == "🌋 Jarðskjálftabrú":
    render_full_data_activation(statuses, cameras, quakes, traffic, weather, alerts, weather_texts=weather_texts)

elif selected_page == "🏘️ Staðir og bæir":
    render_geography(places)

elif selected_page == "🧭 Ferðaleiðangur":
    render_route_mission(places, weather=weather, traffic=traffic, cameras=cameras)

elif selected_page == "🎯 Landafræðiáskorun":
    render_geography_challenge(places, weather=weather, traffic=traffic, cameras=cameras)

elif selected_page == "👨‍🏫 Verkefnabanki kennara":
    render_teacher_mission_builder()

elif selected_page == "📊 Hagstofugögn":
    render_hagstofa_explorer(places, hagstofa_population, hagstofa_fallback, hagstofa_msg)

elif selected_page == "📈 Byggðaþróun":
    render_settlement_trends(places, place_trends, trends_fallback, trends_msg)

elif selected_page == "💧 Vatnafar og ár":
    render_hydrology(hydro_live, rivers, hydro_fallback, hydro_msg, river_lines)

elif selected_page == "🧪 Skjálftaprófun":
    render_quake_debug()

elif selected_page == "📄 Skýrslur":
    render_reports(cameras, quakes, traffic, alerts)

elif selected_page == "⚙️ Stillingar":
    st.subheader("⚙️ Stillingar")
    st.write("Hér koma stillingar fyrir sjálfgefinn bekk, landshluta, kortalög og útlit.")
    if st.button("Hreinsa cache / endurhlaða gögn", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache hreinsað. Endurhlaðið síðuna.")

st.divider()

st.subheader("🏫 Verkefnahugmyndir fyrir kennslu")
st.write("""
**Live Lab v4.3.2** er grunnurinn að stærra kerfi. Nú er búið að aðskilja gögn, kort og viðmót svo auðvelt sé að bæta við næstu einingum.

Næst getum við bætt við:
1. Mission Mode fyrir nemendur.
2. AI verkefnasmið sem býr til verkefni úr gögnum dagsins.
3. Sérstöku Vallaskóla dashboardi.
4. Nemendastigum og hópaleik.
5. Betri færðarlögum og veðurviðvörunum eftir landshlutum.
""")

st.markdown(
    f'<div class="small-note">Síðasta keyrsla: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}. '
    'Þessi vefur er kennsluverkefni og kemur ekki í stað opinberra öryggisupplýsinga.</div>',
    unsafe_allow_html=True,
)
