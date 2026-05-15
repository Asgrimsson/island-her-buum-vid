
from __future__ import annotations

from datetime import datetime
import random
import streamlit as st


LEVELS = ["3.–4. bekkur", "5. bekkur", "6.–7. bekkur", "8.–10. bekkur"]
TOPICS = ["Veður", "Jarðskjálftar", "Færð og umferð", "Kort og landafræði", "Skólaferðalag", "Náttúruvá"]
DURATIONS = ["10 mínútur", "20 mínútur", "40 mínútur", "80 mínútur"]


def _data_sentence(topic: str, cameras, quakes, traffic, alerts) -> str:
    parts = [
        f"{len(cameras)} vegamyndavélar eru í gagnasafninu.",
        f"{len(quakes)} skjálftar eru sýndir í skjálftalaginu.",
        f"{len(traffic)} færðarpunktar eru á kortinu.",
        f"{len(alerts)} viðvörunarfærslur eru í kerfinu.",
    ]
    if topic == "Jarðskjálftar" and len(quakes):
        try:
            biggest = quakes.sort_values("size", ascending=False).iloc[0]
            parts.append(f"Stærsti skjálftinn í gögnunum er {biggest.get('size')} við {biggest.get('place')}.")
        except Exception:
            pass
    if topic == "Færð og umferð" and len(traffic):
        try:
            first = traffic.iloc[0]
            parts.append(f"Dæmi um færðarpunkt: {first.get('name')} — {first.get('status')}.")
        except Exception:
            pass
    return " ".join(parts)


def build_task(prompt: str, level: str, topic: str, duration: str, cameras, quakes, traffic, alerts) -> str:
    data_context = _data_sentence(topic, cameras, quakes, traffic, alerts)
    verbs = ["skoða", "bera saman", "rökstyðja", "útskýra", "merkja á kort", "skrifa stutta niðurstöðu"]
    product = random.choice(["stutt skýrsla", "munnleg kynning", "kortaskýring", "fréttatilkynning", "ferðaráætlun"])

    return f"""# Live Lab verkefni dagsins

**Bekkur:** {level}  
**Viðfangsefni:** {topic}  
**Tímalengd:** {duration}  
**Dagsetning:** {datetime.now().strftime("%d.%m.%Y")}

## Kennaramarkmið
Nemendur nota lifandi gögn úr Vallaskóli Live Lab til að {random.choice(verbs)} og taka rökstudda ákvörðun.

## Gagnastaða núna
{data_context}

## Kveikja
{prompt.strip() or f"Skoðið {topic.lower()} á Íslandskortinu og finnið hvað er áhugaverðast í gögnunum í dag."}

## Verkefni nemenda
1. Opnið kortið og kveikið á þeim lögum sem tengjast verkefninu.
2. Finnið **þrjú sönnunargögn** úr kortinu.
3. Ræðið í hóp: Hvað segja gögnin okkur?
4. Skilið niðurstöðu sem **{product}**.
5. Útskýrið hvaða gögn hjálpuðu ykkur mest og af hverju.

## Spurningar
1. Hvaða staður eða svæði vekur mesta athygli?
2. Hvaða gögn styðja niðurstöðuna ykkar?
3. Hvað gæti breyst ef veður, færð eða skjálftar breytast?
4. Hvaða upplýsingar vantar til að taka enn betri ákvörðun?
5. Hvernig mynduð þið útskýra þetta fyrir yngri nemendum?

## Stigagjöf
- 10 stig: Hópur notar kortið rétt.
- 20 stig: Hópur finnur þrjú góð sönnunargögn.
- 20 stig: Hópur rökstyður niðurstöðu.
- 10 stig: Hópur setur niðurstöðuna skýrt fram.
- 10 aukastig: Hópur tengir verkefnið við raunverulegt öryggi eða skólaferðalag.

## Google Classroom texti
Notið Vallaskóli Live Lab. Veljið gögn úr kortinu, vinnið í hóp og skilið stuttri niðurstöðu með þremur sönnunargögnum. Verkefnið tengist: **{topic}**.
"""


def render_ai_task_maker(cameras, quakes, traffic, alerts):
    st.subheader("🤖 AI Verkefnasmiður")
    st.caption("Fyrsta útgáfa er örugg, staðbundin og notar gögnin sem eru þegar í Live Lab. Seinna getum við tengt OpenAI eða Gemini með API lykli.")

    c1, c2, c3 = st.columns(3)
    with c1:
        level = st.selectbox("Bekkur", LEVELS, index=1)
    with c2:
        topic = st.selectbox("Viðfangsefni", TOPICS)
    with c3:
        duration = st.selectbox("Tímalengd", DURATIONS, index=1)

    prompt = st.text_area(
        "Hvað viltu að verkefnið fjalli um?",
        placeholder="Dæmi: Búðu til 20 mínútna verkefni um jarðskjálfta fyrir 5. bekk þar sem nemendur nota kortið.",
        height=110
    )

    if st.button("✨ Búa til verkefni", use_container_width=True):
        st.session_state["generated_live_lab_task"] = build_task(prompt, level, topic, duration, cameras, quakes, traffic, alerts)

    task = st.session_state.get("generated_live_lab_task")
    if task:
        st.markdown(task)
        with st.expander("📋 Afrita sem hreinan texta"):
            st.code(task, language="markdown")
