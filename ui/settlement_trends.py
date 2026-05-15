
from __future__ import annotations

import pandas as pd
import streamlit as st

from services.hagstofa import summarize_place_trend


def _fmt(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n)


def render_settlement_trends(places: pd.DataFrame, place_trends: pd.DataFrame, trend_fallback: bool, trend_msg: str):
    st.subheader("📈 Byggðaþróun")
    st.caption("Skoðaðu hvort staðir eru að stækka, minnka eða standa í stað.")

    if trend_fallback:
        st.warning(trend_msg)
    else:
        st.success(trend_msg)

    if place_trends is None or place_trends.empty:
        st.error("Engin byggðaþróunargögn fundust.")
        return

    tab_story, tab_compare, tab_rankings, tab_tasks = st.tabs([
        "📖 Mannfjöldasaga",
        "⚖️ Samanburður",
        "🏆 Topplistar",
        "🎒 Verkefni"
    ])

    with tab_story:
        c1, c2 = st.columns([0.45, 0.55])
        with c1:
            names = sorted(place_trends["name"].unique())
            default = "Selfoss" if "Selfoss" in names else names[0]
            selected = st.selectbox("Veldu stað", names, index=names.index(default), key="trend_story_place")

            df = place_trends[place_trends["name"] == selected].sort_values("year")
            summary = summarize_place_trend(place_trends, selected)

            st.metric("Nýjasti íbúafjöldi", _fmt(summary.get("latest_population", "")), f"ár {summary.get('latest_year','')}")
            st.metric("Breyting frá fyrsta ári", _fmt(summary.get("total_change", "")), f"{summary.get('total_pct','')}%")

            if "change_5y" in summary:
                st.metric("Breyting síðustu 5 ár", _fmt(summary["change_5y"]), f"{summary['change_5y_pct']}%")
            if "change_10y" in summary:
                st.metric("Breyting síðustu 10 ár", _fmt(summary["change_10y"]), f"{summary['change_10y_pct']}%")

            st.info(summary.get("story", ""))

            source = summary.get("source", "")
            if source:
                st.caption(f"Uppruni gagna: {source}")

        with c2:
            chart = df[["year", "population_value"]].set_index("year")
            st.line_chart(chart)
            st.dataframe(df[["year", "population_value", "source", "hagstofa_name"]], use_container_width=True, hide_index=True)

        st.markdown("### ✍️ Söguspurning")
        st.write(
            f"Af hverju heldur þú að **{selected}** hafi breyst svona? "
            "Hugsaðu um atvinnu, samgöngur, nálægð við höfuðborgarsvæði, náttúru, þjónustu og skóla."
        )

    with tab_compare:
        names = sorted(place_trends["name"].unique())
        default_a = "Selfoss" if "Selfoss" in names else names[0]
        default_b = "Akureyri" if "Akureyri" in names else names[min(1, len(names)-1)]

        ca, cb = st.columns(2)
        with ca:
            a = st.selectbox("Staður A", names, index=names.index(default_a), key="trend_compare_a")
        with cb:
            b = st.selectbox("Staður B", names, index=names.index(default_b), key="trend_compare_b")

        df = place_trends[place_trends["name"].isin([a, b])].copy()
        pivot = df.pivot_table(index="year", columns="name", values="population_value", aggfunc="first")
        st.line_chart(pivot)

        sa = summarize_place_trend(place_trends, a)
        sb = summarize_place_trend(place_trends, b)

        c1, c2 = st.columns(2)
        with c1:
            st.metric(a, _fmt(sa.get("latest_population", "")), f"{sa.get('total_pct','')}% frá {sa.get('first_year','')}")
            st.write(sa.get("story", ""))
        with c2:
            st.metric(b, _fmt(sb.get("latest_population", "")), f"{sb.get('total_pct','')}% frá {sb.get('first_year','')}")
            st.write(sb.get("story", ""))

    with tab_rankings:
        latest_year = int(place_trends["year"].max())
        latest = place_trends[place_trends["year"] == latest_year].copy()

        first_by_place = place_trends.sort_values("year").groupby("name").first().reset_index()
        latest_by_place = place_trends.sort_values("year").groupby("name").last().reset_index()

        ranking = latest_by_place[["name", "region", "population_value", "year", "source"]].merge(
            first_by_place[["name", "population_value", "year"]],
            on="name",
            suffixes=("_latest", "_first")
        )
        ranking["change"] = ranking["population_value_latest"] - ranking["population_value_first"]
        ranking["change_pct"] = (ranking["change"] / ranking["population_value_first"] * 100).round(1)

        st.markdown(f"### Staðan árið {latest_year}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Fjölmennustu staðir")
            st.dataframe(
                ranking.sort_values("population_value_latest", ascending=False).head(10),
                use_container_width=True,
                hide_index=True
            )
        with c2:
            st.markdown("#### Mesta fjölgun")
            st.dataframe(
                ranking.sort_values("change", ascending=False).head(10),
                use_container_width=True,
                hide_index=True
            )

        st.download_button(
            "⬇️ Sækja byggðaþróun sem CSV",
            data=place_trends.to_csv(index=False).encode("utf-8"),
            file_name="byggdathroun-stadir.csv",
            mime="text/csv",
            use_container_width=True
        )

    with tab_tasks:
        st.markdown("""
### Verkefnahugmyndir

**1. Er staðurinn að stækka?**  
Veldu einn stað og skoðaðu línuritið. Skrifaðu hvort hann hafi stækkað, minnkað eða staðið í stað.

**2. Selfoss vs. annar staður**  
Berðu Selfoss saman við annan stað. Hvor hefur breyst meira?

**3. Af hverju breytist byggð?**  
Veldu stað sem hefur stækkað mikið. Nefndu þrjár mögulegar ástæður.

**4. Lítill en mikilvægur staður**  
Finndu fámennan stað sem er samt mikilvægur vegna staðsetningar, hafnar, ferðaþjónustu eða náttúru.

**5. Ferðaleiðangur + íbúafjöldi**  
Búðu til ferðaleið og skoðaðu hvort stopparnir eru á stækkandi eða minnkandi stöðum.
""")
