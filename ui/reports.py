
from __future__ import annotations

from datetime import datetime
import streamlit as st

from services.teams import teams_df, load_teams
from services.teacher_tasks import load_tasks


def _build_markdown_report(cameras, quakes, traffic, alerts) -> str:
    teams = load_teams()
    tasks = load_tasks()

    top_team = "Engin lið skráð"
    if teams:
        sorted_teams = sorted(teams, key=lambda x: int(x.get("points", 0)), reverse=True)
        top_team = f"{sorted_teams[0].get('name')} ({sorted_teams[0].get('points', 0)} stig)"

    active_tasks = [t for t in tasks if t.get("status") in ["Virkt", "Verkefni dagsins"]]

    return f"""# Vallaskóli Live Lab — kennsluskýrsla

**Dagsetning:** {datetime.now().strftime("%d.%m.%Y %H:%M")}  
**Kerfi:** Vallaskóli Live Lab v1.7

## Gagnastaða
- Myndavélar: {len(cameras)}
- Jarðskjálftar: {len(quakes)}
- Færðarpunktar: {len(traffic)}
- Viðvaranir: {len(alerts)}

## Lið og stig
- Fjöldi liða: {len(teams)}
- Efsta lið: {top_team}

## Verkefni
- Fjöldi vistaðra verkefna: {len(tasks)}
- Virk verkefni: {len(active_tasks)}

## Tillaga að umræðu
1. Hvaða gögn voru gagnlegust í dag?
2. Hvaða svæði á Íslandi vakti mesta athygli?
3. Hvernig geta lifandi gögn hjálpað okkur að taka betri ákvarðanir?
4. Hvað þyrfti að skoða nánar áður en farið er í skólaferðalag?

## Næstu skref
- Velja verkefni dagsins í Kennarastjórnborði.
- Láta nemendur vinna Verkefnaleiðangur í hópum.
- Nota Leaderboard til að safna stigum.
"""


def render_reports(cameras, quakes, traffic, alerts):
    st.subheader("📄 Skýrslur")
    st.caption("Búðu til einfalda kennsluskýrslu úr stöðu dagsins, verkefnum og liðum.")

    report = _build_markdown_report(cameras, quakes, traffic, alerts)
    st.markdown(report)

    st.download_button(
        "⬇️ Sækja skýrslu sem Markdown",
        data=report,
        file_name=f"vallaskoli-live-lab-skyrsla-{datetime.now().strftime('%Y%m%d-%H%M')}.md",
        mime="text/markdown",
        use_container_width=True
    )

    with st.expander("📋 Afrita skýrslu"):
        st.code(report, language="markdown")
