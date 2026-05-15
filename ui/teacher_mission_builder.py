
from __future__ import annotations

import json
import streamlit as st

from services.teacher_missions import (
    add_teacher_mission,
    create_teacher_mission,
    delete_teacher_mission,
    export_missions_json,
    import_missions_json,
    load_teacher_missions,
)


def _mission_card(mission: dict):
    st.markdown(
        f"""
<div style="background:#ffffff;border:1px solid #dfe8f4;border-radius:22px;padding:18px;margin-bottom:12px;box-shadow:0 10px 28px rgba(15,23,42,.06);">
  <div style="font-size:1.25rem;font-weight:950;color:#0f172a;">👨‍🏫 {mission.get('title','Áskorun')}</div>
  <div style="color:#64748b;margin-top:3px;">{mission.get('subject','')} · {mission.get('level','')} · {mission.get('points',0)} stig</div>
  <div style="margin-top:12px;color:#1e293b;line-height:1.45;">{mission.get('prompt','')}</div>
  <div style="margin-top:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:10px;">
    <b>Áhersla:</b> {mission.get('focus','')}<br>
    <b>Kennaraábending:</b> {mission.get('teacher_hint','')}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_teacher_mission_builder():
    st.subheader("👨‍🏫 Verkefnabanki kennara")
    st.caption("Búðu til sérsniðnar landafræðiáskoranir og vistaðu þær í verkefnabanka.")

    tab_create, tab_bank, tab_export, tab_templates = st.tabs([
        "➕ Búa til áskorun",
        "📚 Verkefnabanki",
        "⬇️ Flytja út / inn",
        "⚡ Sniðmát"
    ])

    with tab_create:
        c1, c2 = st.columns([0.55, 0.45])
        with c1:
            title = st.text_input("Titill áskorunar", placeholder="t.d. Ferðaráð Vallaskóla", key="mission_title")
            prompt = st.text_area(
                "Verkefnalýsing",
                height=160,
                placeholder="Skrifaðu hvað nemendur eiga að gera...",
                key="mission_prompt"
            )
            checklist = st.text_area(
                "Gátlisti, ein lína fyrir hvert atriði",
                height=160,
                value="- Skoðið kortið\n- Notið að minnsta kosti tvö gagnalög\n- Rökstyðjið niðurstöðu\n- Skilið stuttu svari",
                key="mission_checklist"
            )
            teacher_hint = st.text_area(
                "Kennaraábending",
                height=100,
                placeholder="Hvernig er best að nota verkefnið í kennslu?",
                key="mission_teacher_hint"
            )

        with c2:
            subject = st.selectbox("Námsgrein", ["Landafræði", "Samfélagsfræði", "Náttúrufræði", "Stærðfræði", "Upplýsingatækni", "Þverfaglegt"], key="mission_subject")
            level = st.selectbox("Tímalengd / hamur", ["10 mín hraðáskorun", "20 mín hópverkefni", "40 mín rannsókn", "Heimaverkefni", "Kennari velur"], key="mission_level")
            points = st.slider("Stig", 5, 100, 30, 5, key="mission_points")
            focus = st.text_input("Áhersla", value="Staðir + lifandi gögn", key="mission_focus")

            st.markdown("### Forskoðun")
            preview = {
                "title": title or "Ný áskorun",
                "subject": subject,
                "level": level,
                "points": points,
                "prompt": prompt or "Verkefnalýsing birtist hér.",
                "focus": focus,
                "teacher_hint": teacher_hint or "Kennaraábending birtist hér.",
            }
            _mission_card(preview)

        if st.button("💾 Vista áskorun í verkefnabanka", use_container_width=True):
            if len(prompt.strip()) < 10:
                st.warning("Verkefnalýsing þarf að vera aðeins lengri.")
            else:
                mission = create_teacher_mission(title, subject, level, points, focus, prompt, checklist, teacher_hint)
                add_teacher_mission(mission)
                st.success("Áskorun vistuð í verkefnabanka.")
                st.rerun()

    with tab_bank:
        missions = load_teacher_missions()
        st.metric("Fjöldi áskorana", len(missions))

        q = st.text_input("Leita í verkefnabanka", placeholder="t.d. ferð, mannfjöldi, Suðurland...", key="mission_bank_search")
        filtered = missions
        if q:
            qlow = q.lower()
            filtered = [
                m for m in missions
                if qlow in str(m.get("title","")).lower()
                or qlow in str(m.get("prompt","")).lower()
                or qlow in str(m.get("focus","")).lower()
                or qlow in str(m.get("subject","")).lower()
            ]

        for mission in filtered:
            with st.expander(f"👨‍🏫 {mission.get('title')} · {mission.get('points',0)} stig", expanded=False):
                _mission_card(mission)
                st.markdown("**Gátlisti**")
                for item in mission.get("checklist", []):
                    st.write(f"- {item}")

                classroom = f"""Teacher Mission — Vallaskóli Live Lab

Titill: {mission.get('title')}
Námsgrein: {mission.get('subject')}
Tími: {mission.get('level')}
Stig: {mission.get('points')}

Verkefni:
{mission.get('prompt')}

Gátlisti:
""" + "\n".join([f"- {x}" for x in mission.get("checklist", [])]) + f"""

Kennaraábending:
{mission.get('teacher_hint','')}
"""
                st.code(classroom, language="markdown")

                if not str(mission.get("id", "")).startswith("default-"):
                    if st.button("🗑️ Eyða þessari áskorun", key=f"delete_mission_{mission.get('id')}", use_container_width=True):
                        if delete_teacher_mission(mission.get("id")):
                            st.success("Áskorun eydd.")
                            st.rerun()
                        else:
                            st.warning("Ekki tókst að eyða áskorun.")

    with tab_export:
        st.markdown("### Flytja út")
        data = export_missions_json()
        st.download_button(
            "⬇️ Sækja verkefnabanka sem JSON",
            data=data,
            file_name="vallaskoli-live-lab-teacher-missions.json",
            mime="application/json",
            use_container_width=True
        )
        st.code(data[:3000] + ("\n..." if len(data) > 3000 else ""), language="json")

        st.markdown("### Flytja inn")
        imported = st.text_area("Límdu JSON verkefnabanka hér", height=180, key="mission_import_json")
        if st.button("📥 Flytja inn verkefnabanka", use_container_width=True):
            ok, msg = import_missions_json(imported)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab_templates:
        st.markdown("""
### Hugmyndir að sérsniðnum áskorunum

**1. Skólaferðalag í dag**  
Nemendur velja áfangastað, skoða veður, færð og fjarlægð og gefa ferðaljós.

**2. Byggðamynstur Íslands**  
Nemendur bera saman þrjá staði í ólíkum landshlutum og skoða mannfjölda.

**3. Vatnafar og byggð**  
Nemendur velja bæ nálægt á eða farvegi og útskýra hvernig vatnafar gæti haft áhrif á byggð.

**4. Jarðhræringar og staðsetning**  
Nemendur velja stað nálægt skjálftasvæði og skoða hvaða gögn þyrfti að fylgjast með.

**5. Ferðaleið með rökum**  
Nemendur setja upp leið í Ferðaleiðangur og rökstyðja stoppin.
""")
