
from __future__ import annotations

import pandas as pd
import streamlit as st

from services.api_client import fetch_url


DEBUG_URLS = [
    "https://luk.vedur.is/arcgis/rest/services/skjalftar/skjalftar_isn93/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
    "https://luk.vedur.is/arcgis/rest/services/skjalftar/skjalftar_isn93/MapServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
    "https://luk.vedur.is/arcgis/rest/services/skjalftar/skjalftar_isn93/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&f=pjson",
    "https://luk.vedur.is/arcgis/rest/services/skjalftar/skjalftar_isn93/MapServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&f=pjson",
]


def render_quake_debug():
    st.subheader("🧪 Skjálfta Debug")
    st.caption("Þessi síða sýnir hrátt svar frá LUK/ArcGIS svo við getum fundið réttu dálkanöfnin og hnitin.")

    url = st.selectbox("Veldu skjálftaendapunkt", DEBUG_URLS, key="quake_debug_url")

    if st.button("Sækja hrá skjálftagögn", use_container_width=True):
        result = fetch_url(url, timeout=15, verify_ssl=True)
        st.session_state["quake_debug_result"] = result

    result = st.session_state.get("quake_debug_result")
    if not result:
        st.info("Smelltu á hnappinn til að sækja hrá skjálftagögn.")
        return

    if not result.ok:
        st.error(result.error)
        return

    st.success(f"Svar kom frá {result.url} ({result.kind}, {result.elapsed_ms} ms)")

    raw = result.data
    if isinstance(raw, dict):
        st.write("Top-level lyklar:", list(raw.keys()))

        if "fields" in raw:
            fields = raw.get("fields", [])
            if fields:
                fdf = pd.DataFrame(fields)
                st.markdown("### Fields")
                st.dataframe(fdf, use_container_width=True, hide_index=True)

        features = raw.get("features", [])
        st.markdown(f"### Features: {len(features)}")
        if features:
            sample = features[0]
            attrs = sample.get("attributes") or sample.get("properties") or {}
            geom = sample.get("geometry") or {}
            st.markdown("#### Fyrsta geometry")
            st.json(geom)
            st.markdown("#### Fyrstu attributes/properties")
            st.json(attrs)

            rows = []
            for f in features[:20]:
                attrs = f.get("attributes") or f.get("properties") or {}
                geom = f.get("geometry") or {}
                row = dict(attrs)
                if "x" in geom:
                    row["_x"] = geom.get("x")
                if "y" in geom:
                    row["_y"] = geom.get("y")
                rows.append(row)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.code(str(raw)[:5000])
