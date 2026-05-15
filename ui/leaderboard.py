
from __future__ import annotations

import streamlit as st

from services.teams import add_team, award_points, teams_df, load_teams, reset_all


def render_team_selector(key: str = "active_team") -> str | None:
    teams = load_teams()
    names = [t["name"] for t in teams]
    if not names:
        st.info("Búðu fyrst til lið í Leaderboard flipanum.")
        return None
    return st.selectbox("Veldu lið", names, key=key)


def render_leaderboard():
    st.subheader("🏆 Live Leaderboard")

    df = teams_df()
    if df.empty:
        st.info("Engin lið komin enn. Búðu til fyrsta liðið hér fyrir neðan.")
    else:
        top = df.head(10).copy()
        top["Sæti"] = range(1, len(top) + 1)
        top["Lið"] = top["name"]
        top["Bekkur/hópur"] = top["class_name"]
        top["Stig"] = top["points"]
        top["Mission"] = top["missions"]
        top["Merki"] = top["badges"].apply(lambda x: ", ".join(x) if isinstance(x, list) and x else "—")
        st.dataframe(
            top[["Sæti", "Lið", "Bekkur/hópur", "Stig", "Mission", "Merki"]],
            use_container_width=True,
            hide_index=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Fjöldi liða", len(df))
        c2.metric("Samtals stig", int(df["points"].sum()))
        c3.metric("Flest stig", int(df["points"].max()))

    st.markdown("### ➕ Búa til lið")
    col1, col2, col3 = st.columns([0.45, 0.35, 0.2])
    with col1:
        name = st.text_input("Nafn liðs", placeholder="t.d. Eldfjallateymið")
    with col2:
        class_name = st.text_input("Bekkur/hópur", placeholder="t.d. 5. bekkur")
    with col3:
        st.write("")
        st.write("")
        if st.button("Búa til", use_container_width=True):
            ok, msg = add_team(name, class_name)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)

    with st.expander("🎁 Gefa aukastig / kennarastjórn"):
        teams = load_teams()
        if teams:
            team = st.selectbox("Veldu lið", [t["name"] for t in teams], key="award_team")
            pts = st.number_input("Stig", min_value=1, max_value=100, value=10, step=5)
            reason = st.text_input("Ástæða", value="Kennarastig")
            if st.button("Gefa stig"):
                ok, msg = award_points(team, int(pts), reason)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.caption("Engin lið til.")

    with st.expander("⚠️ Núllstilla öll lið"):
        st.warning("Þetta eyðir öllum liðum og stigum í þessari staðbundnu útgáfu.")
        if st.button("Núllstilla leaderboard"):
            reset_all()
            st.rerun()
