
from __future__ import annotations

import random
import pandas as pd
import streamlit as st
from services.teacher_missions import load_teacher_missions, mission_to_challenge


def _build_challenge(places, weather=None, traffic=None, cameras=None, prefer_teacher=False):
    teacher_missions = load_teacher_missions()
    if teacher_missions and (prefer_teacher or random.random() < 0.35):
        return mission_to_challenge(random.choice(teacher_missions))

    kinds = ["compare_population", "nearest_region", "route_plan", "safe_destination", "place_card", "coastal_inland", "data_detective", "settlement_story"]
    kind = random.choice(kinds)
    regions = sorted(places["region"].unique())

    if kind == "compare_population":
        a, b = places.sample(2).to_dict("records")
        return {
            "kind": kind,
            "title": "⚖️ Berðu saman tvo staði",
            "points": 30,
            "prompt": f"Berðu saman **{a['name']}** og **{b['name']}**. Hvor staðurinn er fjölmennari, hvor er nær Vallaskóla og hvað gæti skýrt muninn?",
            "data": [a, b],
            "checklist": ["Nefndu íbúafjölda beggja staða.", "Segðu hvor er nær Vallaskóla.", "Notaðu landshluta í rökstuðningi.", "Skrifaðu lokaályktun."],
            "teacher_hint": "Nemendur nota Landafræði-spjöld og Hagstofu gögn."
        }

    if kind == "nearest_region":
        region = random.choice(regions)
        return {
            "kind": kind,
            "title": "📍 Finndu stað í landshluta",
            "points": 20,
            "prompt": f"Finndu stað í landshlutanum **{region}**. Lýstu hvar hann er á Íslandi og berðu hann saman við Selfoss.",
            "data": [{"region": region}],
            "checklist": ["Veldu einn stað í réttum landshluta.", "Segðu hvort hann er við sjó, inni í landi eða nálægt fjöllum/firði.", "Berðu hann saman við Selfoss.", "Notaðu fjarlægð frá Vallaskóla."],
            "teacher_hint": "Gott verkefni fyrir kortalæsi og áttir."
        }

    if kind == "route_plan":
        route = places.sample(3).to_dict("records")
        route_names = " → ".join([r["name"] for r in route])
        return {
            "kind": kind,
            "title": "🧭 Búðu til ferðaleið",
            "points": 40,
            "prompt": f"Búðu til ferðaleið sem tengir þessa staði: **{route_names}**. Hvaða gögn þarf að skoða áður en lagt er af stað?",
            "data": route,
            "checklist": ["Settu staðina í skynsamlega röð.", "Segðu hvaða landshluta leiðin fer um.", "Skoðaðu veður eða færð.", "Útskýrðu muninn á loftlínu og akstursvegalengd."],
            "teacher_hint": "Nemendur geta notað Ferðaleiðangur til að prófa leiðina."
        }

    if kind == "safe_destination":
        place = places.sample(1).iloc[0].to_dict()
        return {
            "kind": kind,
            "title": "🚦 Öruggur áfangastaður?",
            "points": 35,
            "prompt": f"Þið eruð ferðaráð Vallaskóla. Metið hvort **{place['name']}** sé góður áfangastaður í dag. Notið að minnsta kosti tvö lifandi gögn.",
            "data": [place],
            "checklist": ["Skoðaðu veður.", "Skoðaðu færð eða myndavélar.", "Skoðaðu staðsetningu á korti.", "Gefðu grænt/gult/rautt ferðaljós og rökstuddu."],
            "teacher_hint": "Tengir saman landafræði og rauntímagögn."
        }

    if kind == "place_card":
        place = places.sample(1).iloc[0].to_dict()
        return {
            "kind": kind,
            "title": "🃏 Búðu til staðaspjald",
            "points": 25,
            "prompt": f"Búðu til stutt kynningarspjald um **{place['name']}**.",
            "data": [place],
            "checklist": ["Heiti staðar.", "Landshluti og sveitarfélag.", "Íbúafjöldi.", "Hvað er merkilegt þar?", "Ein góð spurning fyrir aðra nemendur."],
            "teacher_hint": "Nemendur geta notað Landafræði-spjöld."
        }

    if kind == "coastal_inland":
        return {
            "kind": kind,
            "title": "🌊 Strandbær eða innlandsstaður?",
            "points": 25,
            "prompt": "Veldu **tvo strandbæi** og **einn stað inni í landi**. Hvernig er staðsetningin ólík og hvaða áhrif getur hún haft á atvinnu, veður og samgöngur?",
            "data": [],
            "checklist": ["Veldu þrjá staði.", "Flokkaðu þá rétt.", "Ræddu áhrif staðsetningar.", "Notaðu kortið í rökstuðningi."],
            "teacher_hint": "Gott verkefni til að ræða byggðamynstur."
        }


    if kind == "settlement_story":
        place = places.sample(1).iloc[0].to_dict()
        return {
            "kind": kind,
            "title": "📈 Segðu byggðasögu staðar",
            "points": 35,
            "prompt": f"Skoðaðu byggðaþróun fyrir **{place['name']}**. Er staðurinn að stækka, minnka eða standa í stað? Hver gæti skýringin verið?",
            "data": [place],
            "checklist": ["Veldu staðinn í Byggðaþróun.", "Skoðaðu línurit.", "Segðu hvort hann stækkar eða minnkar.", "Nefndu tvær mögulegar ástæður."],
            "teacher_hint": "Nemendur nota nýja Byggðaþróun hlutann og tengja tölfræði við samfélagsfræði."
        }

    return {
        "kind": "data_detective",
        "title": "🕵️ Gagnaspæjari",
        "points": 30,
        "prompt": "Finndu einn stað þar sem þú getur tengt saman **mannfjölda**, **veður**, **færð** og **kortastaðsetningu**. Hvað segja gögnin þér?",
        "data": [],
        "checklist": ["Veldu stað.", "Notaðu mannfjöldagögn.", "Notaðu eitt lifandi gagnalag.", "Skrifaðu niðurstöðu með rökum."],
        "teacher_hint": "Hentar vel sem 20 mínútna hópverkefni."
    }


def _init_state():
    st.session_state.setdefault("geo_challenge_score", 0)
    st.session_state.setdefault("geo_challenge_completed", 0)
    st.session_state.setdefault("geo_current_challenge", None)


def render_geography_challenge(places, weather=None, traffic=None, cameras=None):
    _init_state()

    st.subheader("🎯 Landafræðiáskorun")
    st.caption("Gagnvirkur landafræðileikur sem tengir saman staði, mannfjölda, kort, leiðir og lifandi gögn.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Stig", st.session_state["geo_challenge_score"])
    c2.metric("Loknar áskoranir", st.session_state["geo_challenge_completed"])
    c3.metric("Staðir í gagnagrunni", len(places))

    mode = st.radio(
        "Veldu leikham",
        ["10 mín hraðáskorun", "20 mín hópverkefni", "40 mín rannsókn", "Kennari velur sjálfur"],
        horizontal=True,
        key="geo_challenge_mode"
    )

    b1, b2, b3 = st.columns([0.34, 0.33, 0.33])
    with b1:
        if st.button("🎲 Ný áskorun", use_container_width=True):
            st.session_state["geo_current_challenge"] = _build_challenge(places, weather, traffic, cameras)
            st.session_state["geo_answer"] = ""
            st.rerun()
    with b2:
        if st.button("🔄 Núllstilla stig", use_container_width=True):
            st.session_state["geo_challenge_score"] = 0
            st.session_state["geo_challenge_completed"] = 0
            st.rerun()
    with b3:
        teacher_points = st.number_input("Stig frá kennara", min_value=5, max_value=100, value=25, step=5, key="teacher_geo_points")

    if st.button("👨‍🏫 Draga kennaraáskorun úr verkefnabanka", use_container_width=True):
        st.session_state["geo_current_challenge"] = _build_challenge(places, weather, traffic, cameras, prefer_teacher=True)
        st.session_state["geo_answer"] = ""
        st.rerun()

    if st.session_state["geo_current_challenge"] is None:
        st.session_state["geo_current_challenge"] = _build_challenge(places, weather, traffic, cameras)

    ch = st.session_state["geo_current_challenge"]

    st.markdown(
        f"""
<div style="background:linear-gradient(135deg,#eef2ff,#f8fafc);border:1px solid #c7d2fe;border-radius:24px;padding:22px;box-shadow:0 14px 32px rgba(15,23,42,.08);margin:12px 0 18px 0;">
  <div style="font-size:1.75rem;font-weight:950;color:#0f172a;">{ch['title']}</div>
  <div style="margin-top:8px;color:#334155;font-size:1.05rem;">{ch['prompt']}</div>
  <div style="margin-top:12px;display:inline-block;background:white;border:1px solid #ddd6fe;border-radius:999px;padding:6px 12px;font-weight:800;color:#5b21b6;">{ch['points']} stig</div>
</div>
""",
        unsafe_allow_html=True
    )

    left, right = st.columns([0.58, 0.42], gap="large")

    with left:
        st.markdown("### ✅ Gátlisti")
        checked = []
        for i, item in enumerate(ch["checklist"]):
            checked.append(st.checkbox(item, key=f"geo_challenge_check_{ch['kind']}_{i}"))

        st.markdown("### ✍️ Svar / rökstuðningur")
        answer = st.text_area(
            "Skrifaðu svar hópsins hér",
            key="geo_answer",
            height=180,
            placeholder="Við völdum ... vegna þess að gögnin sýna ..."
        )

        enough = len(answer.strip()) >= 40 and sum(checked) >= max(2, len(ch["checklist"]) // 2)

        x1, x2 = st.columns(2)
        with x1:
            if st.button("✅ Merkja áskorun lokið", use_container_width=True, disabled=not enough):
                points = ch["points"] + (10 if all(checked) else 0)
                st.session_state["geo_challenge_score"] += points
                st.session_state["geo_challenge_completed"] += 1
                st.session_state["geo_current_challenge"] = _build_challenge(places, weather, traffic, cameras)
                st.session_state["geo_answer"] = ""
                st.success(f"Frábært! +{points} stig.")
                st.rerun()

        with x2:
            if st.button("⭐ Kennari gefur stig", use_container_width=True):
                st.session_state["geo_challenge_score"] += int(teacher_points)
                st.session_state["geo_challenge_completed"] += 1
                st.success(f"Kennarastig: +{teacher_points}")
                st.rerun()

        if not enough:
            st.caption("Til að ljúka þarf svar með rökstuðningi og að haka við nokkur atriði í gátlistanum.")

    with right:
        st.markdown("### 🔎 Gögn sem tengjast áskorun")
        if ch.get("data"):
            df = pd.DataFrame(ch["data"])
            show_cols = [c for c in ["name", "region", "municipality", "population", "straight_line_from_vallaskoli_km", "estimated_road_from_vallaskoli_km", "note"] if c in df.columns]
            if show_cols:
                st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
            else:
                st.json(ch["data"])
        else:
            st.info("Veldu gögn úr kortinu, Staðir og bæir, Ferðaleiðangur eða Hagstofu síðunni.")

        st.markdown("### 👨‍🏫 Kennaraábending")
        st.info(ch["teacher_hint"])

        with st.expander("📋 Afrita í Google Classroom"):
            classroom = f"""Landafræðiáskorun

Leikhamur: {mode}
Áskorun: {ch['title']}

Verkefni:
{ch['prompt']}

Gátlisti:
""" + "\n".join([f"- {x}" for x in ch["checklist"]]) + """

Skil:
- Svar hóps
- Rökstuðningur með gögnum
- Niðurstaða
"""
            st.code(classroom, language="markdown")

    st.divider()
    st.info("Kennsluhugmynd: Láttu hópa draga nýja áskorun, vinna í 10–20 mínútur og kynna niðurstöðu með að minnsta kosti tveimur gagnalögum úr Live Lab.")
