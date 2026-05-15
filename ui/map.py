from __future__ import annotations

import folium
import pandas as pd
from services.road_network import road_style


VALLASKOLI = {"name": "Vallaskóli", "lat": 63.9362, "lon": -20.9975}


def _safe(v, default=""):
    return default if pd.isna(v) else v




MAIN_ROADS = [
    {
        "name": "Hringvegur 1 — Suðurströnd og Austurland",
        "road": "1",
        "coords": [
            [64.15, -21.94], [64.03, -21.36], [63.94, -20.99], [63.84, -20.40],
            [63.75, -20.22], [63.42, -19.01], [63.79, -18.06], [64.02, -16.98],
            [64.25, -15.21], [64.66, -14.29], [65.03, -14.22], [65.27, -14.39],
        ],
    },
    {
        "name": "Hringvegur 1 — Norðurleið",
        "road": "1",
        "coords": [
            [65.27, -14.39], [65.65, -14.28], [66.04, -17.34], [65.69, -18.13],
            [65.75, -19.64], [65.66, -20.28], [65.40, -20.94], [64.54, -21.92],
            [64.32, -22.07], [64.15, -21.94],
        ],
    },
    {
        "name": "Suðurlandsvegur 1",
        "road": "1",
        "coords": [[64.15, -21.94], [64.03, -21.36], [63.94, -20.99], [63.84, -20.40], [63.75, -20.22], [63.42, -19.01]],
    },
    {
        "name": "Vesturlandsvegur 1",
        "road": "1",
        "coords": [[64.15, -21.94], [64.32, -22.07], [64.54, -21.92], [64.90, -22.90]],
    },
    {
        "name": "Norðurlandsvegur 1",
        "road": "1",
        "coords": [[64.54, -21.92], [65.40, -20.94], [65.66, -20.28], [65.75, -19.64], [65.69, -18.13], [65.60, -17.00], [66.04, -17.34]],
    },
    {
        "name": "Austurlandsvegur 1",
        "road": "1",
        "coords": [[65.27, -14.39], [65.03, -14.22], [64.66, -14.29], [64.25, -15.21]],
    },
    {
        "name": "Reykjanesbraut",
        "road": "41",
        "coords": [[64.15, -21.94], [64.07, -22.05], [64.04, -22.20], [64.00, -22.56], [63.99, -22.65]],
    },
    {
        "name": "Grindavíkurvegur",
        "road": "43",
        "coords": [[63.99, -22.56], [63.90, -22.43], [63.84, -22.43]],
    },
    {
        "name": "Krýsuvíkurvegur / Suðurstrandarvegur",
        "road": "42/427",
        "coords": [[63.84, -22.43], [63.88, -22.05], [63.94, -21.97], [63.86, -21.38], [63.84, -21.15]],
    },
    {
        "name": "Gullni hringurinn — Þingvellir / Laugarvatn / Geysir",
        "road": "36/37/35",
        "coords": [[64.15, -21.94], [64.26, -21.13], [64.21, -20.73], [64.13, -20.31], [64.31, -20.12], [64.33, -20.30], [63.94, -20.99]],
    },
    {
        "name": "Þrengslavegur",
        "road": "39",
        "coords": [[64.03, -21.36], [63.97, -21.45], [63.86, -21.38]],
    },
    {
        "name": "Þorlákshafnarvegur",
        "road": "38",
        "coords": [[63.94, -20.99], [63.89, -21.18], [63.86, -21.38]],
    },
    {
        "name": "Landeyjahafnarvegur",
        "road": "254",
        "coords": [[63.75, -20.22], [63.63, -20.13], [63.53, -20.12]],
    },
    {
        "name": "Snæfellsnesvegur",
        "road": "54",
        "coords": [[64.54, -21.92], [64.77, -22.72], [64.85, -23.25], [64.92, -23.26], [64.89, -23.71], [64.75, -23.65]],
    },
    {
        "name": "Dalaleið / Vestfirðir",
        "road": "60",
        "coords": [[64.54, -21.92], [65.12, -21.80], [65.40, -21.95], [65.60, -23.99], [65.75, -23.47], [66.07, -23.13]],
    },
    {
        "name": "Djúpvegur Vestfirðir",
        "road": "61",
        "coords": [[66.07, -23.13], [66.16, -23.25], [66.11, -22.70], [65.95, -21.55], [65.66, -21.45]],
    },
    {
        "name": "Strandavegur",
        "road": "68",
        "coords": [[65.40, -20.94], [65.70, -21.50], [65.95, -21.55]],
    },
    {
        "name": "Siglufjarðarvegur / Tröllaskagi",
        "road": "76/82",
        "coords": [[65.69, -18.13], [65.97, -18.53], [66.07, -18.65], [66.15, -18.91], [65.88, -19.42], [65.75, -19.64]],
    },
    {
        "name": "Húsavíkurvegur",
        "road": "85",
        "coords": [[65.69, -18.13], [65.80, -17.75], [66.04, -17.34], [66.18, -17.10], [66.36, -15.34]],
    },
    {
        "name": "Mývatns- og Dettifossleið",
        "road": "87/862",
        "coords": [[65.69, -18.13], [65.60, -17.00], [65.65, -16.91], [65.82, -16.38], [66.04, -16.50]],
    },
    {
        "name": "Öxi / Berufjörður",
        "road": "939",
        "coords": [[65.03, -14.22], [64.80, -14.50], [64.66, -14.29]],
    },
    {
        "name": "Austfjarðaleið — Fjarðabyggð",
        "road": "92/96",
        "coords": [[65.27, -14.39], [65.26, -14.01], [65.15, -13.68], [65.07, -14.02], [65.03, -14.22]],
    },
    {
        "name": "Kjalvegur",
        "road": "35",
        "coords": [[64.31, -20.12], [64.72, -19.95], [64.90, -19.50], [65.25, -19.40], [65.45, -19.35]],
    },
    {
        "name": "Sprengisandsleið",
        "road": "26/F26",
        "coords": [[63.99, -19.70], [64.25, -19.25], [64.70, -18.80], [65.10, -18.10], [65.60, -17.00]],
    },
    {
        "name": "Kaldidalur",
        "road": "550",
        "coords": [[64.26, -21.13], [64.50, -20.70], [64.70, -20.50], [64.75, -20.90], [64.54, -21.92]],
    },
]

def _add_main_road_overlay(m):
    layer = folium.FeatureGroup(name="🛣️ Helstu vegir", show=True)
    for road in MAIN_ROADS:
        folium.PolyLine(
            road["coords"],
            color="#1f2937",
            weight=4,
            opacity=0.78,
            tooltip=f"🛣️ {road['name']}",
        ).add_to(layer)

        # Road number label roughly at middle coordinate.
        mid = road["coords"][len(road["coords"]) // 2]
        folium.Marker(
            location=mid,
            icon=folium.DivIcon(html=f"""
            <div style="
                background:#ffffff;
                border:2px solid #334155;
                border-radius:8px;
                padding:2px 7px;
                font-size:12px;
                font-weight:950;
                color:#0f172a;
                box-shadow:0 3px 10px rgba(15,23,42,.18);
                white-space:nowrap;">
                🛣️ {road['road']}
            </div>
            """)
        ).add_to(layer)
    layer.add_to(m)





def _traffic_fmt(value):
    try:
        if value is None or value == "":
            return "—"
        return f"{int(float(value)):,}".replace(",", ".")
    except Exception:
        return str(value)


def _traffic_popup_html(row):
    def g(key, default=""):
        try:
            value = row.get(key, default)
            if value is None or str(value).lower() == "nan":
                return default
            return value
        except Exception:
            return default

    daily_rows = ""
    for i in range(1, 8):
        val = g(f"umf_dagur{i}", "")
        date = g(f"dags_dagur{i}", "")
        if val not in ["", None]:
            label = "í gær" if i == 1 else f"fyrir {i} dögum"
            daily_rows += f"<tr><td>{label}</td><td><b>{_traffic_fmt(val)}</b></td><td>{date}</td></tr>"

    if not daily_rows:
        daily_rows = "<tr><td colspan='3'>Engin 7 daga sundurliðun í þessu svari.</td></tr>"

    speed = g("medalhradi_15min", "")
    speed_text = f"{_traffic_fmt(speed)} km/klst" if speed not in ["", None] else "—"

    return f"""
    <div style="font-family:system-ui;min-width:280px;max-width:380px;">
      <h3 style="margin:0 0 8px 0;">🚦 {g('name','Umferðarteljari')}</h3>
      <div><b>Vegur:</b> {g('road','')}</div>
      <div style="font-size:12px;color:#64748b;">Punkturinn sýnir teljara á/við þennan veg. Smelltu á veglínu til að sjá vegkafla.</div>
      <div><b>Svæði:</b> {g('region','')}</div>
      <div><b>Stefna:</b> {g('direction','')}</div>
      <div><b>Tegund:</b> {g('station_type','')}</div>
      <hr>
      <div style="font-size:15px;"><b>Kortatalan:</b> {g('traffic_label','—')}</div>
      <div><b>Tímabil kortatölu:</b> {g('traffic_period','óþekkt')}</div>
      <div><b>Síðasta uppfærsla:</b> {g('latest_time','')}</div>
      <hr>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <tr><td>Síðustu 15 mín.</td><td><b>{_traffic_fmt(g('umf_15min',''))}</b></td></tr>
        <tr><td>Frá miðnætti</td><td><b>{_traffic_fmt(g('umf_i_dag',''))}</b></td></tr>
        <tr><td>Meðalhraði sl. 15 mín.</td><td><b>{speed_text}</b></td></tr>
      </table>
      <hr>
      <div style="font-weight:800;margin-bottom:4px;">Síðustu 7 sólarhringar</div>
      <table style="width:100%;border-collapse:collapse;font-size:12px;">
        <tr><th style="text-align:left;">Dagur</th><th style="text-align:left;">Ökutæki</th><th style="text-align:left;">Dagsetning</th></tr>
        {daily_rows}
      </table>
      <p style="font-size:11px;color:#64748b;margin-top:8px;">
        Ath. teljarar geta verið stefnugreindir. Ef sami staður birtist tvisvar getur það verið sitthvor akstursstefnan.
      </p>
    </div>
    """




def _limit_geojson_features(geojson, limit=420):
    try:
        if not geojson or not geojson.get("features"):
            return geojson
        features = geojson.get("features", [])
        if len(features) <= limit:
            return geojson
        return {"type": "FeatureCollection", "features": features[:limit]}
    except Exception:
        return geojson


def build_live_map(
    cameras: pd.DataFrame,
    quakes: pd.DataFrame,
    traffic: pd.DataFrame,
    weather: pd.DataFrame,
    traffic_counters: pd.DataFrame | None = None,
    places: pd.DataFrame | None = None,
    river_lines: pd.DataFrame | None = None,
    road_network: dict | None = None,
    show_cameras=True,
    show_quakes=True,
    show_traffic=True,
    show_traffic_counters=False,
    show_weather=False,
    show_places=False,
    show_rivers=False,
    show_exact_roads=False,
    show_school=True,
):
    # Vegir þurfa að sjást vel í umferðarham. OpenStreetMap er því sjálfgefið grunnkort.
    m = folium.Map(location=[64.95, -18.9], zoom_start=6, tiles=None)

    folium.TileLayer("OpenStreetMap", name="Vegakort / OpenStreetMap", show=True).add_to(m)
    folium.TileLayer("CartoDB positron", name="Ljóst kort", show=False).add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="Dökkt kort", show=False).add_to(m)

    if show_school:
        folium.Marker(
            [VALLASKOLI["lat"], VALLASKOLI["lon"]],
            tooltip="Vallaskóli",
            popup="<b>🏫 Vallaskóli</b><br>Live Lab miðstöðin okkar",
            icon=folium.Icon(color="green", icon="home", prefix="fa"),
        ).add_to(m)

    if show_cameras and not cameras.empty:
        layer = folium.FeatureGroup(name="📷 Myndavélar", show=True)
        for _, row in cameras.head(220).iterrows():
            popup = f"<b>📷 {_safe(row.get('name'))}</b><br>{_safe(row.get('road'))}"
            image = _safe(row.get("image"))
            if image:
                popup += f"<br><img src='{image}' width='240'>"
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=5,
                popup=folium.Popup(popup, max_width=280),
                tooltip=str(_safe(row.get("name"), "Vefmyndavél")),
                color="#38d5ff",
                fill=True,
                fill_opacity=0.85,
            ).add_to(layer)
        layer.add_to(m)

    if show_quakes and not quakes.empty:
        layer = folium.FeatureGroup(name="🌋 Jarðskjálftar", show=True)
        for _, row in quakes.head(220).iterrows():
            size = float(row.get("size") or 0)
            radius = max(4, min(22, size * 4))
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=radius,
                popup=f"<b>🌋 {_safe(row.get('place'))}</b><br>Stærð: {size}<br>{_safe(row.get('time'))}",
                tooltip=f"{_safe(row.get('place'))} | {size}",
                color="#fb7185",
                fill=True,
                fill_opacity=0.55,
            ).add_to(layer)
        layer.add_to(m)

    if show_traffic and not traffic.empty:
        layer = folium.FeatureGroup(name="🚗 Færð / umferð", show=True)
        color_map = {"green": "#4ade80", "yellow": "#facc15", "red": "#fb7185"}
        for _, row in traffic.head(220).iterrows():
            color = color_map.get(row.get("severity"), "#facc15")
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=7,
                popup=f"<b>🚗 {_safe(row.get('name'))}</b><br>{_safe(row.get('status'))}",
                tooltip=f"{_safe(row.get('name'))} | {_safe(row.get('status'))}",
                color=color,
                fill=True,
                fill_opacity=0.8,
            ).add_to(layer)
        layer.add_to(m)

    if show_weather and not weather.empty:
        layer = folium.FeatureGroup(name="🌦️ Veðurstöðvar", show=False)
        for _, row in weather.iterrows():
            try:
                lat, lon = float(row["lat"]), float(row["lon"])
            except Exception:
                continue
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                popup=f"<b>🌦️ {_safe(row.get('station'))}</b><br>Hiti: {_safe(row.get('temp'))}<br>Vindur: {_safe(row.get('wind'))}",
                tooltip=str(_safe(row.get("station"), "Veðurstöð")),
                color="#a78bfa",
                fill=True,
                fill_opacity=0.75,
            ).add_to(layer)
        layer.add_to(m)




    if show_traffic_counters and traffic_counters is not None and not traffic_counters.empty:
        layer = folium.FeatureGroup(name="🚦 Umferðartölur", show=True)
        df = traffic_counters.dropna(subset=["lat", "lon"]) if {"lat", "lon"}.issubset(traffic_counters.columns) else traffic_counters
        max_val = 1
        try:
            max_val = max(float(pd.to_numeric(df["traffic_value"], errors="coerce").fillna(0).max()), 1)
        except Exception:
            max_val = 1

        for _, row in df.iterrows():
            try:
                lat = float(row.get("lat"))
                lon = float(row.get("lon"))
            except Exception:
                continue

            try:
                val = float(row.get("traffic_value") or 0)
            except Exception:
                val = 0

            label = row.get("traffic_label", "")
            if label in [None, "", "—"]:
                label = f"{val:g}" if val else "teljari"

            radius = 6 + min(16, (val / max_val) * 16) if max_val else 8
            is_fallback = str(row.get("source", "")).lower() == "fallback"

            popup = _traffic_popup_html(row)

            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                color="#f97316",
                fill=True,
                fill_opacity=0.78,
                tooltip=f"{row.get('name','Umferðarteljari')} — {label}",
                popup=popup,
            ).add_to(layer)

            # Always show a visible number/label on map.
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=f"""
                <div style="
                    transform: translate(10px,-18px);
                    background: rgba(255,255,255,.96);
                    border: 2px solid rgba(249,115,22,.55);
                    border-radius: 11px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: 950;
                    color: #7c2d12;
                    box-shadow: 0 5px 14px rgba(15,23,42,.22);
                    white-space: nowrap;">
                    🚦 {label}
                </div>
                """)
            ).add_to(layer)
        layer.add_to(m)


    if show_places and places is not None and not places.empty:
        layer = folium.FeatureGroup(name="🏘️ Staðir og bæir", show=True)
        for _, row in places.iterrows():
            try:
                lat = float(row.get("lat"))
                lon = float(row.get("lon"))
            except Exception:
                continue
            popup = f"""
            <b>🏘️ {row.get('name','Staður')}</b><br>
            <b>Landshluti:</b> {row.get('region','')}<br>
            <b>Sveitarfélag:</b> {row.get('municipality','')}<br>
            <b>Tegund:</b> {row.get('type','')}<br>
            <b>Íbúafjöldi:</b> {row.get('population') or 'Bætum við síðar'}<br>
            <b>Frá Vallaskóla:</b> {row.get('straight_line_from_vallaskoli_km', row.get('distance_from_vallaskoli_km',''))} km loftlína<br><b>Áætlaður akstur:</b> {row.get('estimated_road_from_vallaskoli_km','')} km<br>
            <br><b>✨ Hvað er merkilegt hér?</b><br>{row.get('highlight','')}<br>
            <br>{row.get('note','')}
            """
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                popup=popup,
                tooltip=str(row.get("name", "Staður")),
                color="#7c3aed",
                fill=True,
                fill_opacity=0.82,
            ).add_to(layer)
        layer.add_to(m)

    if show_rivers and river_lines is not None and not river_lines.empty:
        layer = folium.FeatureGroup(name="💧 Ár / farvegir", show=True)
        for _, row in river_lines.iterrows():
            coords = row.get("coords")
            if not coords:
                continue
            folium.PolyLine(
                locations=coords,
                color="#0ea5e9",
                weight=4,
                opacity=0.85,
                tooltip=str(row.get("river", "Á")),
                popup=f"<b>💧 {row.get('river','Á')}</b><br>{row.get('area','')}<br>{row.get('type','')}<br>{row.get('note','')}",
            ).add_to(layer)
        layer.add_to(m)


    folium.LayerControl(collapsed=False).add_to(m)
    return m
