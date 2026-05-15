
from __future__ import annotations

from datetime import datetime
import random
import streamlit as st
from services.teams import load_teams, award_points


MISSIONS = [
    {
        "title": "Stormferð Vallaskóla",
        "role": "Þið eruð ferðaráð Vallaskóla.",
        "scenario": "Skóli vill fara í dagsferð frá Selfossi. Þið þurfið að velja öruggasta kostinn út frá lifandi gögnum.",
        "choices": ["Reykjavík", "Vík í Mýrdal", "Þingvellir"],
        "tasks": [
            "Skoðið myndavélar og færðarpunkta á leiðinni.",
            "Athugið hvort skjálftar eða viðvaranir skipta máli.",
            "Veljið áfangastað og rökstyðjið með minnst þremur gögnum.",
        ],
        "teacher_tip": "Gott fyrir landafræði, náttúrufræði og rökhugsun."
    },
    {
        "title": "Jarðskjálftavaktin",
        "role": "Þið eruð jarðvísindateymi.",
        "scenario": "Skjálftar hafa mælst á Íslandi. Þið þurfið að útskýra hvar virknin er mest og hvað fólk ætti að fylgjast með.",
        "choices": ["Reykjanes", "Katla", "Vatnajökull"],
        "tasks": [
            "Finnið stærsta skjálftann á kortinu.",
            "Skráið staðsetningu, stærð og mynstur.",
            "Búið til stutta frétt eða viðvörun fyrir nemendur.",
        ],
        "teacher_tip": "Gott fyrir hugtök eins og skjálftahrina, flekaskil og náttúruvá."
    },
    {
        "title": "Öruggasta leiðin",
        "role": "Þið eruð leiðsögumenn.",
        "scenario": "Nemendahópur þarf að ferðast um Suðurland. Þið eigið að velja leið og meta áhættu.",
        "choices": ["Selfoss → Reykjavík", "Selfoss → Vík", "Selfoss → Gullfoss"],
        "tasks": [
            "Skoðið færð, veður og vegamyndavélar.",
            "Finnið einn stað þar sem þarf að sýna sérstaka varúð.",
            "Gefið ferðinni grænt, gult eða rautt ljós og útskýrið af hverju.",
        ],
        "teacher_tip": "Frábært sem hópavinna í 20–30 mínútur."
    },
    {
        "title": "Fréttastofa Íslands",
        "role": "Þið eruð fréttateymi.",
        "scenario": "Þið eigið að búa til 60 sekúndna frétt um stöðuna á Íslandi í dag.",
        "choices": ["Veðurfrétt", "Skjálftafrétt", "Umferðarfrétt"],
        "tasks": [
            "Veljið þrjú lifandi gögn úr kortinu.",
            "Skrifið stutta frétt með inngangi, meginmáli og lokasetningu.",
            "Notið kortið sem sönnunargagn.",
        ],
        "teacher_tip": "Tengir upplýsingalæsi, íslensku og náttúrufræði."
    }
]


def _mission_points(report: str, evidence: str, decision: str) -> int:
    points = 0
    if len(report.strip()) >= 80:
        points += 20
    if len(evidence.strip()) >= 50:
        points += 20
    if decision:
        points += 10
    keywords = ["veður", "færð", "skjálfti", "myndavél", "viðvörun", "kort", "gögn"]
    points += min(30, sum(5 for k in keywords if k.lower() in (report + " " + evidence).lower()))
    return points


def render_mission_mode(cameras, quakes, traffic, alerts):
    st.subheader("🎒 Verkefnaleiðangur")

    if "mission_index" not in st.session_state:
        st.session_state["mission_index"] = 0
    if "mission_points" not in st.session_state:
        st.session_state["mission_points"] = 0
    if "team_name" not in st.session_state:
        st.session_state["team_name"] = ""

    teams = load_teams()
    team_names = [t["name"] for t in teams]

    top1, top2 = st.columns([0.7, 0.3])
    with top1:
        if team_names:
            selected_team = st.selectbox("Veldu lið", team_names, key="mission_team")
            st.session_state["team_name"] = selected_team
        else:
            st.session_state["team_name"] = st.text_input("Nafn hóps", value=st.session_state["team_name"], placeholder="t.d. Eldfjallateymið")
            st.caption("Ábending: Búðu til föst lið í 🏆 Leaderboard flipanum.")
    with top2:
        if st.button("🎲 Nýtt mission", use_container_width=True):
            st.session_state["mission_index"] = random.randrange(len(MISSIONS))

    mission = MISSIONS[st.session_state["mission_index"]]

    st.markdown(f"### 🚀 {mission['title']}")
    st.info(f"**Hlutverk:** {mission['role']}\n\n{mission['scenario']}")

    st.markdown("#### Verkefni")
    for i, task in enumerate(mission["tasks"], start=1):
        st.write(f"{i}. {task}")

    decision = st.radio("Veljið niðurstöðu / leið:", mission["choices"], horizontal=False)

    st.markdown("#### Sönnunargögn úr Live Lab")
    evidence = st.text_area(
        "Skrifið hvaða gögn þið notuðuð",
        placeholder="Dæmi: Við skoðuðum vegamyndavél á Hellisheiði, færðarlag og nýlegan skjálfta...",
        height=110,
        key="mission_evidence"
    )

    st.markdown("#### Skýrsla hóps")
    report = st.text_area(
        "Skrifið niðurstöðu og rökstuðning",
        placeholder="Við mælum með... vegna þess að...",
        height=150,
        key="mission_report"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Skila mission", use_container_width=True):
            earned = _mission_points(report, evidence, decision)
            st.session_state["mission_points"] += earned
            team_name = st.session_state.get("team_name", "")
            if team_names and team_name:
                award_points(team_name, earned, mission["title"])
                st.success(f"Mission skilað! {team_name} fékk {earned} stig.")
            else:
                st.success(f"Mission skilað! Þið fenguð {earned} stig.")
            st.balloons()
    with col2:
        st.metric("Mission stig", st.session_state["mission_points"])
    with col3:
        st.caption(f"Kennaraábending: {mission['teacher_tip']}")

    with st.expander("📋 Afrita mission fyrir Google Classroom / Classroom verkefni"):
        team = st.session_state["team_name"] or "Hópur"
        classroom_text = f"""
{mission['title']}

Hópur: {team}
Hlutverk: {mission['role']}

Lýsing:
{mission['scenario']}

Verkefni:
1. {mission['tasks'][0]}
2. {mission['tasks'][1]}
3. {mission['tasks'][2]}

Veljið einn kost:
{", ".join(mission['choices'])}

Skilið:
- Sönnunargögnum úr kortinu
- Stuttri niðurstöðu
- Rökstuðningi með lifandi gögnum

Dagsetning: {datetime.now().strftime("%d.%m.%Y")}
"""
        st.code(classroom_text, language="text")

    with st.expander("🧪 Lifandi gögn sem geta hjálpað hópnum"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Myndavélar", len(cameras))
        c2.metric("Skjálftar", len(quakes))
        c3.metric("Færðarpunktar", len(traffic))
        c4.metric("Viðvaranir", len(alerts))
