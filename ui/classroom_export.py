
from __future__ import annotations

from datetime import datetime
import html
import streamlit as st

from services.teacher_tasks import load_tasks
from services.teams import load_teams


def _default_student_sheet() -> str:
    return """# Nemendablað — Vallaskóli Live Lab

**Nafn hóps:** ___________________________  
**Dagsetning:** __________________________  
**Mission / verkefni:** ___________________

## 1. Hvað eigið þið að rannsaka?
Skrifið með ykkar eigin orðum hvað verkefnið gengur út á.

__________________________________________________________________

__________________________________________________________________

## 2. Sönnunargögn úr kortinu
Finnið þrjú gögn úr Vallaskóli Live Lab.

| # | Gögn | Hvað segja gögnin okkur? |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

## 3. Ákvörðun hópsins
Við mælum með:

☐ Grænt ljós — allt lítur vel út  
☐ Gult ljós — þarf að skoða betur  
☐ Rautt ljós — ekki ráðlegt / þarf að bíða

## 4. Rökstuðningur
Af hverju komist þið að þessari niðurstöðu?

__________________________________________________________________

__________________________________________________________________

## 5. Útgangsmiði
Eitt sem við lærðum í dag:

__________________________________________________________________
"""


def _html_document(title: str, body_markdown: str) -> str:
    safe = html.escape(body_markdown)
    # Basic markdown-ish conversion for print
    safe = safe.replace("&lt;br&gt;", "<br>")
    lines = safe.splitlines()
    out = []
    for line in lines:
        if line.startswith("# "):
            out.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            out.append(f"<h3>{line[4:]}</h3>")
        elif line.strip() == "":
            out.append("<br>")
        elif line.startswith("|"):
            out.append(f"<pre>{line}</pre>")
        else:
            out.append(f"<p>{line}</p>")
    content = "\n".join(out)
    return f"""<!doctype html>
<html lang="is">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; color:#111827; line-height:1.45; }}
  h1 {{ font-size: 28px; margin-bottom: 10px; }}
  h2 {{ font-size: 20px; margin-top: 26px; border-bottom:1px solid #ddd; padding-bottom:6px; }}
  p {{ font-size: 15px; margin: 6px 0; }}
  pre {{ font-family: Arial, sans-serif; white-space: pre-wrap; background:#f8fafc; padding:8px; border-radius:8px; }}
  .brand {{ color:#0b78f0; font-weight:800; }}
  @media print {{ button {{ display:none; }} body {{ margin: 22mm; }} }}
</style>
</head>
<body>
<div class="brand">Vallaskóli Live Lab</div>
{content}
<script>window.onload = () => {{ /* user can press Ctrl+P */ }}</script>
</body>
</html>"""


def render_classroom_export(cameras, quakes, traffic, alerts):
    st.subheader("🖨️ Útflutningur í Classroom + Nemendablöð")
    st.caption("Búðu til prentvæn verkefnablöð og texta sem hægt er að afrita í Google Classroom.")

    tasks = load_tasks()
    teams = load_teams()

    tab_sheet, tab_classroom, tab_quick = st.tabs(["📝 Nemendablað", "📋 Classroom texti", "⚡ Hraðútgáfa"])

    with tab_sheet:
        if tasks:
            options = ["Tómt Live Lab blað"] + [t["title"] for t in tasks]
            selected = st.selectbox("Veldu verkefni", options, key="printable_task_select")
            if selected == "Tómt Live Lab blað":
                content = _default_student_sheet()
                title = "Nemendablað — Vallaskóli Live Lab"
            else:
                task = next(t for t in tasks if t["title"] == selected)
                title = f"Nemendablað — {task['title']}"
                content = f"""# Nemendablað — {task['title']}

**Námsgrein:** {task.get('subject','')}  
**Tímalengd:** {task.get('duration','')}  
**Hópur:** ___________________________  
**Dagsetning:** {datetime.now().strftime("%d.%m.%Y")}

## Verkefni
{task.get('body','')}

## Sönnunargögn
Finnið þrjú gögn úr Live Lab.

1. _______________________________________________________________

2. _______________________________________________________________

3. _______________________________________________________________

## Niðurstaða hóps
__________________________________________________________________

__________________________________________________________________

## Mat hópsins
☐ Við notuðum kortið  
☐ Við fundum þrjú gögn  
☐ Við rökstuddum niðurstöðu  
☐ Við gátum útskýrt verkefnið fyrir öðrum
"""
        else:
            title = "Nemendablað — Vallaskóli Live Lab"
            content = _default_student_sheet()

        edited = st.text_area("Nemendablað", value=content, height=430, key="student_sheet_editor")
        html_doc = _html_document(title, edited)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "⬇️ Sækja sem Markdown",
                data=edited,
                file_name="vallaskoli-live-lab-nemendablad.md",
                mime="text/markdown",
                use_container_width=True
            )
        with c2:
            st.download_button(
                "🖨️ Sækja sem prentvænt HTML",
                data=html_doc,
                file_name="vallaskoli-live-lab-nemendablad.html",
                mime="text/html",
                use_container_width=True
            )

        st.info("Til að prenta: opnaðu HTML skrána í vafra og ýttu á Ctrl+P.")

    with tab_classroom:
        team_list = ", ".join([t["name"] for t in teams]) if teams else "Allir hópar"
        classroom_text = f"""Vallaskóli Live Lab — verkefni dagsins

Nemendur vinna í hópum: {team_list}

1. Opnið Vallaskóli Live Lab.
2. Veljið Verkefnaleiðangur eða verkefni dagsins.
3. Finnið þrjú sönnunargögn úr kortinu.
4. Skrifið stutta niðurstöðu.
5. Skilið rökstuðningi með gögnum.

Gögn í kerfinu núna:
- Myndavélar: {len(cameras)}
- Jarðskjálftar: {len(quakes)}
- Færðarpunktar: {len(traffic)}
- Viðvaranir: {len(alerts)}

Skil:
- Hópanafn
- 3 sönnunargögn
- lokaákvörðun
- rökstuðningur
"""
        st.text_area("Texti fyrir Google Classroom", value=classroom_text, height=300, key="classroom_export_text")
        st.download_button(
            "⬇️ Sækja Classroom texta",
            data=classroom_text,
            file_name="classroom-live-lab-verkefni.txt",
            mime="text/plain",
            use_container_width=True
        )

    with tab_quick:
        st.markdown("### ⚡ Hraðútgáfa fyrir 20 mínútna tíma")
        quick = """# 20 mínútna Live Lab verkefni

## 0–3 mín
Kennari sýnir kortið og spyr: Hvað er að gerast á Íslandi núna?

## 3–12 mín
Hópar finna 3 gögn:
- eitt úr korti
- eitt úr stöðuspjaldi
- eitt úr viðvörun/færð/skjálfta

## 12–17 mín
Hópar skrifa niðurstöðu:
Við teljum að ______ vegna þess að ______.

## 17–20 mín
Hópar deila einni niðurstöðu.
"""
        st.code(quick, language="markdown")
        st.download_button(
            "⬇️ Sækja 20 mín verkefni",
            data=quick,
            file_name="20-min-live-lab-verkefni.md",
            mime="text/markdown",
            use_container_width=True
        )
