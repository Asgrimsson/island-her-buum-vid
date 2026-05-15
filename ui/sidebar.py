from __future__ import annotations

import streamlit as st


TASKS = [
    "Finndu þrjár vegamyndavélar á Suðurlandi. Hvað segir það okkur um færð og öryggi?",
    "Skoðaðu jarðskjálftana. Eru þeir dreifðir eða safnast þeir á ákveðin svæði?",
    "Veldu eina leið frá Selfossi til Reykjavíkur. Hvaða gögn myndir þú skoða áður en þú leggur af stað?",
    "Búðu til 5 spurningar fyrir yngri nemendur út frá kortinu.",
    "Berðu saman tvö svæði á Íslandi: hvar virðist mest virkni vera í dag?",
    "Hannaðu viðvörunarkerfi fyrir skólaferðalag: hvað þarf að birtast á skjánum?",
    "Veldu einn jarðskjálfta og skrifaðu stutta frétt um hann eins og veðurfréttamaður.",
    "Finndu Vallaskóla á kortinu og útskýrðu hvaða gögn skipta máli fyrir skólaferðalag.",
    "Reiknaðu hvaða svæði er næst Vallaskóla: Reykjanes, Katla eða Reykjavík.",
    "Búðu til kortaskýrslu: hvað er að gerast á Íslandi núna?"
]

QUIZ = [
    {
        "question": "Í hvaða landshluta er Vallaskóli?",
        "answer": "Suðurland",
        "options": ["Vesturland", "Suðurland", "Norðurland", "Austurland"],
    },
    {
        "question": "Hvaða gögn hjálpa mest við að meta akstur í vondum veðrum?",
        "answer": "Veður + færð + myndavélar",
        "options": ["Aðeins hitastig", "Veður + færð + myndavélar", "Aðeins kort", "Aðeins mannfjöldi"],
    },
    {
        "question": "Hvað sýnir jarðskjálftakort best?",
        "answer": "Staðsetningu og stærð skjálfta",
        "options": ["Aldur fjalla", "Staðsetningu og stærð skjálfta", "Fjölda bíla", "Vindátt á sjó"],
    },
]


def render_teacher_helper():
    st.subheader("🧠 Kennarahjálpari")
    if "task_index" not in st.session_state:
        st.session_state["task_index"] = 0

    if st.button("🎲 Búa til verkefni dagsins", use_container_width=True):
        st.session_state["task_index"] = (st.session_state["task_index"] + 1) % len(TASKS)

    st.info(TASKS[st.session_state["task_index"]])


def render_quiz():
    st.subheader("🎮 Landafræðileikur")
    if "q_index" not in st.session_state:
        st.session_state["q_index"] = 0
    if "score" not in st.session_state:
        st.session_state["score"] = 0

    q_index = st.session_state["q_index"] % len(QUIZ)
    current = QUIZ[q_index]
    st.write(f"**{current['question']}**")
    answer = st.radio("Veldu svar:", current["options"], key=f"quiz_{q_index}", label_visibility="collapsed")

    if st.button("Athuga svar", use_container_width=True):
        if answer == current["answer"]:
            st.session_state["score"] += 10
            st.session_state["q_index"] += 1
            st.success("Rétt! +10 Live Lab stig")
        else:
            st.error("Næstum — skoðaðu kortið og reyndu aftur.")

    st.metric("Live Lab stig", st.session_state["score"])
