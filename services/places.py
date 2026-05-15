
from __future__ import annotations

import math
import pandas as pd
import streamlit as st


VALLASKOLI = (63.9346, -20.9966)

PLACES = [
    {"name": "Reykjavík", "region": "Höfuðborgarsvæði", "municipality": "Reykjavíkurborg", "lat": 64.1466, "lon": -21.9426, "type": "höfuðborg", "note": "Höfuðborg Íslands og stærsti þéttbýliskjarni landsins."},
    {"name": "Kópavogur", "region": "Höfuðborgarsvæði", "municipality": "Kópavogsbær", "lat": 64.1114, "lon": -21.9080, "type": "bær", "note": "Næstfjölmennasta sveitarfélag landsins."},
    {"name": "Hafnarfjörður", "region": "Höfuðborgarsvæði", "municipality": "Hafnarfjarðarbær", "lat": 64.0671, "lon": -21.9377, "type": "hafnarbær", "note": "Bær við hraun og höfn sunnan Reykjavíkur."},
    {"name": "Garðabær", "region": "Höfuðborgarsvæði", "municipality": "Garðabær", "lat": 64.0887, "lon": -21.9220, "type": "bær", "note": "Bær á höfuðborgarsvæðinu, milli Kópavogs og Hafnarfjarðar."},
    {"name": "Mosfellsbær", "region": "Höfuðborgarsvæði", "municipality": "Mosfellsbær", "lat": 64.1667, "lon": -21.7000, "type": "bær", "note": "Bær við rætur Esju og Úlfarsfells."},
    {"name": "Seltjarnarnes", "region": "Höfuðborgarsvæði", "municipality": "Seltjarnarnesbær", "lat": 64.1531, "lon": -22.0002, "type": "bær", "note": "Vestasti hluti höfuðborgarsvæðisins."},

    {"name": "Selfoss", "region": "Suðurland", "municipality": "Árborg", "lat": 63.9331, "lon": -20.9971, "type": "bær", "note": "Stærsti þéttbýliskjarni Suðurlands og heimabær Vallaskóla."},
    {"name": "Hveragerði", "region": "Suðurland", "municipality": "Hveragerðisbær", "lat": 64.0004, "lon": -21.1860, "type": "jarðhitabær", "note": "Þekktur fyrir jarðhita, gróðurhús og Reykjadal."},
    {"name": "Þorlákshöfn", "region": "Suðurland", "municipality": "Ölfus", "lat": 63.8557, "lon": -21.3781, "type": "hafnarbær", "note": "Höfn við suðurströndina og ferjusamband til Vestmannaeyja."},
    {"name": "Eyrarbakki", "region": "Suðurland", "municipality": "Árborg", "lat": 63.8637, "lon": -21.1486, "type": "þorp", "note": "Gamalt sjávarþorp með merkri sögu."},
    {"name": "Stokkseyri", "region": "Suðurland", "municipality": "Árborg", "lat": 63.8371, "lon": -21.0592, "type": "þorp", "note": "Sjávarþorp á Suðurlandi."},
    {"name": "Hella", "region": "Suðurland", "municipality": "Rangárþing ytra", "lat": 63.8345, "lon": -20.4000, "type": "bær", "note": "Þjónustubær á Suðurlandsvegi."},
    {"name": "Hvolsvöllur", "region": "Suðurland", "municipality": "Rangárþing eystra", "lat": 63.7533, "lon": -20.2243, "type": "bær", "note": "Nálægt Njáluslóðum og leiðinni að Þórsmörk."},
    {"name": "Vík í Mýrdal", "region": "Suðurland", "municipality": "Mýrdalshreppur", "lat": 63.4186, "lon": -19.0060, "type": "þorp", "note": "Syðsta þorp Íslands, nálægt Reynisfjöru og Mýrdalsjökli."},
    {"name": "Kirkjubæjarklaustur", "region": "Suðurland", "municipality": "Skaftárhreppur", "lat": 63.7896, "lon": -18.0580, "type": "þorp", "note": "Áningarstaður milli Víkur og Skaftafells."},
    {"name": "Vestmannaeyjar", "region": "Suðurland", "municipality": "Vestmannaeyjabær", "lat": 63.4427, "lon": -20.2734, "type": "eyjabær", "note": "Eyjabær þekktur fyrir eldgosið 1973 og lundabyggð."},

    {"name": "Akranes", "region": "Vesturland", "municipality": "Akraneskaupstaður", "lat": 64.3218, "lon": -22.0749, "type": "bær", "note": "Bær á Skipaskaga, norðan Hvalfjarðar."},
    {"name": "Borgarnes", "region": "Vesturland", "municipality": "Borgarbyggð", "lat": 64.5383, "lon": -21.9206, "type": "bær", "note": "Þjónustumiðstöð Vesturlands við Borgarfjörð."},
    {"name": "Stykkishólmur", "region": "Vesturland", "municipality": "Stykkishólmsbær", "lat": 65.0757, "lon": -22.7297, "type": "hafnarbær", "note": "Bær á Snæfellsnesi með ferju yfir Breiðafjörð."},
    {"name": "Grundarfjörður", "region": "Vesturland", "municipality": "Grundarfjarðarbær", "lat": 64.9243, "lon": -23.2631, "type": "bær", "note": "Bær við Kirkjufell á norðanverðu Snæfellsnesi."},
    {"name": "Ólafsvík", "region": "Vesturland", "municipality": "Snæfellsbær", "lat": 64.8945, "lon": -23.7092, "type": "þorp", "note": "Þorp á Snæfellsnesi nálægt Snæfellsjökli."},

    {"name": "Ísafjörður", "region": "Vestfirðir", "municipality": "Ísafjarðarbær", "lat": 66.0748, "lon": -23.1340, "type": "bær", "note": "Stærsti bær Vestfjarða."},
    {"name": "Bolungarvík", "region": "Vestfirðir", "municipality": "Bolungarvíkurkaupstaður", "lat": 66.1590, "lon": -23.2500, "type": "bær", "note": "Sjávarbær norðan við Ísafjörð."},
    {"name": "Patreksfjörður", "region": "Vestfirðir", "municipality": "Vesturbyggð", "lat": 65.5965, "lon": -23.9958, "type": "þorp", "note": "Þorp á sunnanverðum Vestfjörðum."},

    {"name": "Blönduós", "region": "Norðurland vestra", "municipality": "Húnabyggð", "lat": 65.6602, "lon": -20.2809, "type": "bær", "note": "Bær við ós Blöndu."},
    {"name": "Sauðárkrókur", "region": "Norðurland vestra", "municipality": "Skagafjörður", "lat": 65.7461, "lon": -19.6394, "type": "bær", "note": "Stærsti bær Skagafjarðar."},
    {"name": "Hvammstangi", "region": "Norðurland vestra", "municipality": "Húnaþing vestra", "lat": 65.3970, "lon": -20.9436, "type": "þorp", "note": "Þorp við Miðfjörð."},

    {"name": "Akureyri", "region": "Norðurland eystra", "municipality": "Akureyrarbær", "lat": 65.6885, "lon": -18.1262, "type": "bær", "note": "Stærsti bær utan höfuðborgarsvæðisins."},
    {"name": "Húsavík", "region": "Norðurland eystra", "municipality": "Norðurþing", "lat": 66.0449, "lon": -17.3389, "type": "bær", "note": "Þekkt fyrir hvalaskoðun."},
    {"name": "Dalvík", "region": "Norðurland eystra", "municipality": "Dalvíkurbyggð", "lat": 65.9702, "lon": -18.5286, "type": "bær", "note": "Bær við Eyjafjörð."},
    {"name": "Siglufjörður", "region": "Norðurland eystra", "municipality": "Fjallabyggð", "lat": 66.1511, "lon": -18.9081, "type": "bær", "note": "Sögufrægur síldarbær."},
    {"name": "Ólafsfjörður", "region": "Norðurland eystra", "municipality": "Fjallabyggð", "lat": 66.0670, "lon": -18.6467, "type": "bær", "note": "Bær á Tröllaskaga."},

    {"name": "Egilsstaðir", "region": "Austurland", "municipality": "Múlaþing", "lat": 65.2669, "lon": -14.3948, "type": "bær", "note": "Miðstöð Austurlands við Lagarfljót."},
    {"name": "Seyðisfjörður", "region": "Austurland", "municipality": "Múlaþing", "lat": 65.2606, "lon": -14.0098, "type": "bær", "note": "Fjarðarbær með ferjusamband til Evrópu."},
    {"name": "Neskaupstaður", "region": "Austurland", "municipality": "Fjarðabyggð", "lat": 65.1480, "lon": -13.6833, "type": "bær", "note": "Bær í Norðfirði."},
    {"name": "Reyðarfjörður", "region": "Austurland", "municipality": "Fjarðabyggð", "lat": 65.0316, "lon": -14.2183, "type": "bær", "note": "Bær við Reyðarfjörð."},
    {"name": "Eskifjörður", "region": "Austurland", "municipality": "Fjarðabyggð", "lat": 65.0731, "lon": -14.0153, "type": "bær", "note": "Fjarðarbær á Austurlandi."},
    {"name": "Höfn", "region": "Suðausturland", "municipality": "Sveitarfélagið Hornafjörður", "lat": 64.2539, "lon": -15.2082, "type": "bær", "note": "Bær við Vatnajökul og humarhöfn."},
    {"name": "Djúpivogur", "region": "Austurland", "municipality": "Múlaþing", "lat": 64.6570, "lon": -14.2850, "type": "þorp", "note": "Sjávarþorp á Austfjörðum."},

    {"name": "Keflavík", "region": "Suðurnes", "municipality": "Reykjanesbær", "lat": 64.0049, "lon": -22.5624, "type": "bær", "note": "Hluti Reykjanesbæjar, nálægt Keflavíkurflugvelli."},
    {"name": "Njarðvík", "region": "Suðurnes", "municipality": "Reykjanesbær", "lat": 63.9800, "lon": -22.5300, "type": "bær", "note": "Hluti Reykjanesbæjar."},
    {"name": "Grindavík", "region": "Suðurnes", "municipality": "Grindavíkurbær", "lat": 63.8424, "lon": -22.4338, "type": "bær", "note": "Bær á Reykjanesskaga nálægt nýlegri eldvirkni."},
    {"name": "Sandgerði", "region": "Suðurnes", "municipality": "Suðurnesjabær", "lat": 64.0376, "lon": -22.7077, "type": "bær", "note": "Bær á norðanverðum Reykjanesskaga."},
    {"name": "Garður", "region": "Suðurnes", "municipality": "Suðurnesjabær", "lat": 64.0656, "lon": -22.6466, "type": "bær", "note": "Þekktur fyrir vita og fuglalíf."},
]


def _distance_km(lat1, lon1, lat2, lon2):
    r = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@st.cache_data(ttl=3600, show_spinner=False)
def get_places() -> pd.DataFrame:
    df = pd.DataFrame(PLACES)
    df["distance_from_vallaskoli_km"] = df.apply(
        lambda r: round(_distance_km(VALLASKOLI[0], VALLASKOLI[1], r["lat"], r["lon"]), 1),
        axis=1,
    )

    highlights = {
        "Reykjavík": "Höfuðborg Íslands og miðstöð stjórnsýslu, menningar og þjónustu.",
        "Selfoss": "Heimabær Vallaskóla og mikilvægur þjónustukjarni á Suðurlandi.",
        "Akureyri": "Stærsti bær utan höfuðborgarsvæðisins og mikilvæg miðstöð Norðurlands.",
        "Vík í Mýrdal": "Syðsta þorp landsins, nálægt Reynisfjöru, Dyrhólaey og Mýrdalsjökli.",
        "Vestmannaeyjar": "Eyjasamfélag með einstaka gos- og sjávarútvegssögu.",
        "Grindavík": "Staður á Reykjanesskaga þar sem jarðhræringar og eldvirkni hafa haft mikil áhrif.",
        "Höfn": "Gátt að Vatnajökli og Suðausturlandi.",
        "Ísafjörður": "Miðstöð Vestfjarða, umkringd fjöllum og fjörðum.",
        "Húsavík": "Þekkt fyrir hvalaskoðun og staðsetningu við Skjálfanda.",
        "Egilsstaðir": "Miðstöð Austurlands við Lagarfljót.",
        "Keflavík": "Nálægt stærsta alþjóðaflugvelli Íslands.",
    }

    def _highlight(row):
        if row["name"] in highlights:
            return highlights[row["name"]]
        if "hafnar" in str(row.get("type", "")).lower():
            return f"{row['name']} tengist sjó, samgöngum, fiskveiðum eða verslun."
        if "þorp" in str(row.get("type", "")).lower():
            return f"{row['name']} er gott dæmi um minni þéttbýlisstað í {row['region']}."
        return row.get("note", "")

    population_estimates = {
        "Reykjavík": "≈ 140.000",
        "Kópavogur": "≈ 40.000",
        "Hafnarfjörður": "≈ 31.000",
        "Garðabær": "≈ 19.000",
        "Mosfellsbær": "≈ 14.000",
        "Seltjarnarnes": "≈ 4.600",
        "Selfoss": "≈ 10.000",
        "Hveragerði": "≈ 3.400",
        "Þorlákshöfn": "≈ 1.700",
        "Eyrarbakki": "≈ 600",
        "Stokkseyri": "≈ 500",
        "Hella": "≈ 1.000",
        "Hvolsvöllur": "≈ 1.000",
        "Vík í Mýrdal": "≈ 350",
        "Kirkjubæjarklaustur": "≈ 200",
        "Vestmannaeyjar": "≈ 4.500",
        "Akranes": "≈ 8.000",
        "Borgarnes": "≈ 2.000",
        "Stykkishólmur": "≈ 1.300",
        "Grundarfjörður": "≈ 850",
        "Ólafsvík": "≈ 1.000",
        "Ísafjörður": "≈ 2.700",
        "Bolungarvík": "≈ 1.000",
        "Patreksfjörður": "≈ 700",
        "Blönduós": "≈ 900",
        "Sauðárkrókur": "≈ 2.600",
        "Hvammstangi": "≈ 600",
        "Akureyri": "≈ 20.000",
        "Húsavík": "≈ 2.300",
        "Dalvík": "≈ 1.400",
        "Siglufjörður": "≈ 1.200",
        "Ólafsfjörður": "≈ 800",
        "Egilsstaðir": "≈ 2.700",
        "Seyðisfjörður": "≈ 700",
        "Neskaupstaður": "≈ 1.400",
        "Reyðarfjörður": "≈ 1.300",
        "Eskifjörður": "≈ 1.000",
        "Höfn": "≈ 2.500",
        "Djúpivogur": "≈ 400",
        "Keflavík": "≈ 16.000",
        "Njarðvík": "≈ 5.000",
        "Grindavík": "≈ 3.600",
        "Sandgerði": "≈ 1.900",
        "Garður": "≈ 1.700",
    }

    # NOTE: distance_from_vallaskoli_km is straight-line distance ("loftlína"), not road distance.
    # Estimated road distance is only a classroom approximation.
    def _road_factor(row):
        region = row.get("region", "")
        if region in ["Höfuðborgarsvæði", "Suðurnes", "Suðurland"]:
            return 1.18
        if region in ["Vestfirðir", "Austurland"]:
            return 1.45
        return 1.32

    df["straight_line_from_vallaskoli_km"] = df["distance_from_vallaskoli_km"]
    df["estimated_road_from_vallaskoli_km"] = df.apply(
        lambda r: round(r["straight_line_from_vallaskoli_km"] * _road_factor(r), 1),
        axis=1,
    )

    df["population"] = df["name"].map(population_estimates).fillna("Bætum við síðar")
    df["highlight"] = df.apply(_highlight, axis=1)
    df["student_question"] = df.apply(
        lambda r: f"Hvernig myndir þú lýsa staðsetningu {r['name']} fyrir nemanda sem hefur aldrei komið þangað? Notaðu landshluta, áttir og loftlínu frá Vallaskóla ({r['straight_line_from_vallaskoli_km']} km) og áætlaða akstursleið ({r['estimated_road_from_vallaskoli_km']} km).",
        axis=1,
    )
    return df.sort_values(["region", "name"]).reset_index(drop=True)
