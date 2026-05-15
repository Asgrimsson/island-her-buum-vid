
from __future__ import annotations

import streamlit as st

from services.teacher_tasks import add_task, load_tasks, update_task_status, delete_task, tasks_df
from services.teams import load_teams


SUBJECTS = ["Landafræði", "Náttúrufræði", "Upplýsingatækni", "Stærðfræði", "Íslenska", "Samþætt verkefni"]
DURATIONS = ["10 mín", "20 mín", "40 mín", "80 mín", "Heil kennslustund"]


def _classroom_copy(task: dict) -> str:
    return f"""# {task['title']}

**Viðfangsefni:** {task.get('subject','')}
**Tímalengd:** {task.get('duration','')}
**Hópur:** {task.get('target','Allir hópar')}

## Verkefni
{task.get('body','')}

## Skil
Skilið stuttri niðurstöðu með:
- 3 sönnunargögnum úr Vallaskóli Live Lab
- rökstuðningi
- lokaákvörðun hópsins

## Mat
- Kort/gögn notuð rétt
- Rökstuðningur skýr
- Hópur vinnur vel saman
"""


def render_teacher_center():
    st.subheader("👨‍🏫 Teacher Control Center")
    st.caption("Stjórnborð fyrir kennara: vista verkefni, velja verkefni dagsins, úthluta á lið og afrita í Classroom.")

    tab_create, tab_tasks, tab_lesson = st.tabs(["➕ Búa til verkefni", "📚 Verkefnabanki", "⏱️ Lesson Mode"])

    with tab_create:
        teams = load_teams()
        team_options = ["Allir hópar"] + [t["name"] for t in teams]

        c1, c2, c3 = st.columns(3)
        with c1:
            title = st.text_input("Titill verkefnis", placeholder="t.d. Stormferð Vallaskóla", key="teacher_task_title")
        with c2:
            subject = st.selectbox("Námsgrein", SUBJECTS, key="teacher_subject")
        with c3:
            duration = st.selectbox("Tímalengd", DURATIONS, key="teacher_duration")

        target = st.selectbox("Úthluta á", team_options, key="teacher_target")

        default_body = st.session_state.get("generated_live_lab_task", "")
        body = st.text_area(
            "Verkefnalýsing",
            value=default_body,
            height=260,
            placeholder="Skrifaðu verkefni eða farðu fyrst í AI Verkefnasmið og búðu til verkefni.",
            key="teacher_task_body"
        )

        c1, c2 = st.columns([0.3, 0.7])
        with c1:
            if st.button("💾 Vista verkefni", use_container_width=True):
                ok, msg = add_task(title, subject, duration, body, target)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)
        with c2:
            st.info("Ábending: Ef þú býrð til verkefni í AI Verkefnasmið birtist það sjálfkrafa hér.")

    with tab_tasks:
        tasks = load_tasks()
        if not tasks:
            st.info("Engin verkefni vistuð enn.")
        else:
            df = tasks_df()
            st.dataframe(
                df[["title", "subject", "duration", "target", "status", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Veldu verkefni")
            selected_title = st.selectbox("Verkefni", [t["title"] for t in tasks], key="teacher_task_select")
            task = next(t for t in tasks if t["title"] == selected_title)

            st.markdown(f"## {task['title']}")
            st.write(f"**Námsgrein:** {task.get('subject')} | **Tími:** {task.get('duration')} | **Hópur:** {task.get('target')}")
            st.info(task.get("body", ""))

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("⭐ Gera að verkefni dagsins", use_container_width=True):
                    update_task_status(task["id"], "Verkefni dagsins")
                    st.success("Verkefni merkt sem verkefni dagsins.")
                    st.rerun()
            with c2:
                if st.button("✅ Merkja lokið", use_container_width=True):
                    update_task_status(task["id"], "Lokið")
                    st.rerun()
            with c3:
                if st.button("🗑️ Eyða", use_container_width=True):
                    delete_task(task["id"])
                    st.rerun()

            with st.expander("📋 Afrita í Google Classroom"):
                st.code(_classroom_copy(task), language="markdown")

    with tab_lesson:
        st.markdown("### ⏱️ Lesson Mode")
        st.write("Veldu tímaform og notaðu þetta sem kennsluflæði á skjávarpa.")

        mode = st.radio(
            "Kennsluflæði",
            ["20 mín hraðverkefni", "40 mín hópavinna", "80 mín rannsóknarvinna"],
            horizontal=True,
            key="lesson_mode_radio"
        )

        if mode == "20 mín hraðverkefni":
            steps = [
                ("0–3 mín", "Kveikja: Kennari sýnir kortið og spyr hvað sé að gerast."),
                ("3–12 mín", "Hópar finna 3 gögn úr kortinu."),
                ("12–17 mín", "Hópar skrifa niðurstöðu."),
                ("17–20 mín", "2–3 hópar deila niðurstöðu.")
            ]
        elif mode == "40 mín hópavinna":
            steps = [
                ("0–5 mín", "Kveikja og hlutverk útskýrð."),
                ("5–20 mín", "Hópar vinna Verkefnaleiðangur."),
                ("20–30 mín", "Skýrsla og rökstuðningur."),
                ("30–40 mín", "Kynning, stig og umræða.")
            ]
        else:
            steps = [
                ("0–10 mín", "Innlögn um gögn, kort og áreiðanleika."),
                ("10–35 mín", "Rannsókn í hópum."),
                ("35–55 mín", "Skýrsla, kortaskýring eða frétt."),
                ("55–75 mín", "Kynningar."),
                ("75–80 mín", "Útgangsmiði: hvað lærðum við?")
            ]

        for time, step in steps:
            st.write(f"**{time}:** {step}")

        with st.expander("📋 Afrita kennsluflæði"):
            st.code("\n".join([f"{time}: {step}" for time, step in steps]), language="text")
