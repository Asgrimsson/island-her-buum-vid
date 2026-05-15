
from __future__ import annotations

import folium
import streamlit as st
from streamlit_folium import st_folium


def _place_card(row):
    population = row.get("population") or "Bætum við síðar"
    st.markdown(
        f"""
<div style="background:linear-gradient(180deg,#ffffff,#f8fbff);border:1px solid #dfe8f4;border-radius:26px;padding:24px;box-shadow:0 16px 42px rgba(15,23,42,.08);margin-bottom:18px;">
  <div style="font-size:2.1rem;font-weight:950;color:#0f172a;letter-spacing:-0.04em;">🏘️ {row['name']}</div>
  <div style="color:#475569;font-size:1.05rem;margin-top:4px;">{row['region']} · {row['municipality']} · {row['type']}</div>
  <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:18px;">
    <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:18px;padding:14px;"><b>Landshluti</b><br>{row['region']}</div>
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:18px;padding:14px;"><b>Frá Vallaskóla</b><br>{row.get('straight_line_from_vallaskoli_km', row.get('straight_line_from_vallaskoli_km', row['distance_from_vallaskoli_km']))} km loftlína</div>
    <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:18px;padding:14px;"><b>Íbúafjöldi</b><br>{population}<br><span style="font-size:.82rem;color:#64748b;">{row.get("population_source","")} {row.get("population_year","")}</span></div>
  </div>
  <div style="margin-top:18px;font-size:1rem;line-height:1.55;color:#1e293b;"><b>Stutt lýsing:</b><br>{row['note']}</div>
  <div style="margin-top:16px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:18px;padding:16px;color:#0f172a;">
    <b>✨ Hvað er merkilegt hér?</b><br>{row.get('highlight','')}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_geography(places):
    st.subheader("🏘️ Staðir og bæir Íslands")
    st.caption("Landafræðiæfingar með helstu stöðum, landshlutum, fjarlægð frá Vallaskóla og staðaspjöldum.")

    tab_cards, tab_map, tab_table, tab_tasks = st.tabs(["🃏 Landafræði-spjöld", "🗺️ Kort", "📋 Tafla", "🎒 Verkefni"])

    with tab_cards:
        c1, c2, c3 = st.columns([0.35, 0.35, 0.30])
        with c1:
            regions = ["Allir landshlutar"] + sorted(places["region"].unique())
            region = st.selectbox("Landshluti", regions, key="place_card_region")
        with c2:
            types = ["Allar tegundir"] + sorted(places["type"].unique())
            ptype = st.selectbox("Tegund", types, key="place_card_type")
        with c3:
            sort_by = st.selectbox("Raða eftir", ["Nafni", "Fjarlægð frá Vallaskóla"], key="place_card_sort")

        df = places.copy()
        if region != "Allir landshlutar":
            df = df[df["region"] == region]
        if ptype != "Allar tegundir":
            df = df[df["type"] == ptype]

        df = df.sort_values("straight_line_from_vallaskoli_km" if sort_by == "Fjarlægð frá Vallaskóla" else "name")
        selected = st.selectbox("Veldu stað", df["name"].tolist(), key="selected_place_card")
        row = df[df["name"] == selected].iloc[0]

        left, right = st.columns([0.58, 0.42], gap="large")
        with left:
            _place_card(row)
            st.markdown("### 🎒 Spurning fyrir nemendur")
            st.info(row.get("student_question", ""))
            st.markdown("### 🧭 Mini-verkefni")
            st.write(
                f"""
1. Finndu {row['name']} á kortinu.  
2. Segðu í hvaða landshluta staðurinn er.  
3. Finndu einn annan stað nálægt honum.  
4. Útskýrðu hvort staðurinn er við sjó, inni í landi, nálægt fjalli, á eða jökli.  
5. Berðu staðinn saman við Selfoss.
"""
            )

        with right:
            m = folium.Map(location=[row["lat"], row["lon"]], zoom_start=9, tiles="CartoDB positron")
            folium.Marker(
                location=[row["lat"], row["lon"]],
                tooltip=row["name"],
                popup=f"<b>{row['name']}</b><br>{row['region']}<br>{row['note']}",
                icon=folium.Icon(color="purple", icon="info-sign"),
            ).add_to(m)
            folium.Circle(location=[row["lat"], row["lon"]], radius=20000, color="#7c3aed", fill=True, fill_opacity=0.06).add_to(m)
            st_folium(m, width=None, height=430, returned_objects=[])
            st.markdown("### 📍 Hnit")
            st.code(f"{row['lat']}, {row['lon']}")

    with tab_map:
        regions = sorted(places["region"].unique())
        selected_regions = st.multiselect("Veldu landshluta", regions, default=regions, key="geo_regions")
        df = places[places["region"].isin(selected_regions)]

        m = folium.Map(location=[64.9, -18.8], zoom_start=6, tiles="CartoDB positron")
        for _, row in df.iterrows():
            popup = f"""
<b>🏘️ {row['name']}</b><br>
<b>Landshluti:</b> {row['region']}<br>
<b>Sveitarfélag:</b> {row['municipality']}<br>
<b>Tegund:</b> {row['type']}<br>
<b>Íbúafjöldi:</b> {row.get('population') or 'Bætum við síðar'}<br>
<b>Frá Vallaskóla:</b> {row.get('straight_line_from_vallaskoli_km', row.get('straight_line_from_vallaskoli_km', row['distance_from_vallaskoli_km']))} km loftlína<br>
<br><b>Hvað er merkilegt hér?</b><br>{row.get('highlight','')}<br>
<br>{row['note']}
"""
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=7,
                tooltip=row["name"],
                popup=popup,
                color="#7c3aed",
                fill=True,
                fill_opacity=0.82,
            ).add_to(m)
        st_folium(m, width=None, height=640, returned_objects=[])

    with tab_table:
        q = st.text_input("Leita að stað/bæ", placeholder="t.d. Selfoss, Akureyri, Suðurland...", key="geo_search")
        df = places.copy()
        if q:
            qlow = q.lower()
            mask = (
                df["name"].str.lower().str.contains(qlow, na=False)
                | df["region"].str.lower().str.contains(qlow, na=False)
                | df["municipality"].str.lower().str.contains(qlow, na=False)
                | df["type"].str.lower().str.contains(qlow, na=False)
                | df["note"].str.lower().str.contains(qlow, na=False)
            )
            df = df[mask]

        cols = ["name", "region", "municipality", "type", "population", "straight_line_from_vallaskoli_km", "note", "highlight"]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Sækja staði sem CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="stadir-og-baeir-islands.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with tab_tasks:
        st.markdown("""
### Verkefnahugmyndir

**1. Næst Vallaskóla**  
Finndu 5 staði sem eru næst Vallaskóla. Hvað eiga þeir sameiginlegt?

**2. Landshlutar**  
Veldu einn landshluta og finndu 5 bæi þar. Hvernig liggja þeir miðað við fjöll, firði, ár eða strönd?

**3. Ferðaleið**  
Búðu til ferðaleið frá Selfossi til Akureyrar með 3 stoppum á leiðinni.

**4. Strandbæir og innlandsbæir**  
Flokkaðu 10 staði í strandbæi og staði inni í landi.

**5. Tengdu við lifandi gögn**  
Veldu bæ og skoðaðu veður, vegamyndavélar, færð, ár/farvegi og skjálfta í nágrenninu.

**6. Bæjarspjald**  
Veldu einn stað og búðu til stutt kynningarspjald:
- Hvar er staðurinn?
- Hvað er merkilegt þar?
- Hvernig kemst maður þangað frá Selfossi?
- Hvaða lifandi gögn skipta máli í dag?
""")
