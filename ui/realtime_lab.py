
from __future__ import annotations

import streamlit as st


def render_realtime_lab(air_quality, weather_texts=None):
    st.subheader("🌐 Meira af rauntímagögnum")
    st.caption("Aukagögn sem hægt er að nota í náttúrufræði, samfélagsfræði, upplýsingatækni og verkefnavinnu.")

    tab_air, tab_texts = st.tabs(["🌫️ Loftgæði", "📝 Textaspár"])

    with tab_air:
        if air_quality is None or air_quality.empty:
            st.warning("Loftgæðagögn náðust ekki í þessari keyrslu.")
            st.caption("Kerfið reynir nú api.ust.is/aq.")
        else:
            st.dataframe(air_quality, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Sækja loftgæði sem CSV",
                data=air_quality.to_csv(index=False).encode("utf-8"),
                file_name="loftgaedi.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.info("Kennsluhugmynd: Láttu nemendur skoða loftgæði, finna mælistöðvar og ræða hvað getur haft áhrif á loftmengun.")

    with tab_texts:
        if weather_texts is None or weather_texts.empty:
            st.warning("Textaspár náðust ekki í þessari keyrslu.")
        else:
            for _, row in weather_texts.iterrows():
                with st.expander(row.get("title") or "Textaspá", expanded=False):
                    st.caption(f"{row.get('creation','')} | {row.get('valid_from','')} – {row.get('valid_to','')}")
                    st.write(row.get("content", ""))
            st.download_button(
                "⬇️ Sækja textaspár sem CSV",
                data=weather_texts.to_csv(index=False).encode("utf-8"),
                file_name="textaspar.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.info("Kennsluhugmynd: Láttu nemendur lesa textaspá, finna lykilorð um vind/úrkomu og breyta henni í einfalda veðurfrétt.")
