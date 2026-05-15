# Ísland hér búum við — Deploy á Render, skref fyrir skref

## 0. Markmiðið

Við ætlum að setja vefinn í loftið sem stöðugt kennslutól:

- Kóðinn verður geymdur í GitHub.
- Render keyrir vefinn sem Python Web Service.
- Þegar þú uppfærir GitHub getur Render uppfært vefinn sjálfkrafa.

---

## 1. Afþjappa zip-skránni

1. Sæktu zip-skrána.
2. Hægri smelltu á hana.
3. Veldu **Extract All / Afþjappa**.
4. Settu möppuna t.d. á Desktop.
5. Mappan á að heita eitthvað á borð við:

```text
vallaskoli-live-lab-v43-deployment-ready-render
```

Þú mátt endurnefna hana í:

```text
island-her-buum-vid
```

---

## 2. Prófa vefinn fyrst í tölvunni

Opnaðu Command Prompt eða PowerShell inni í möppunni og keyrðu:

```bat
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

Opnaðu síðan:

```text
http://localhost:8501
```

Ef vefurinn opnast erum við góð.

---

## 3. Keyra healthcheck

Í sömu möppu:

```bat
py scripts/healthcheck.py
```

Þú vilt sjá:

```text
HEALTHCHECK OK — Ísland hér búum við er tilbúið til deploy.
```

---

## 4. Búa til GitHub repo

1. Farðu á GitHub.
2. Smelltu á **New repository**.
3. Nafn:

```text
island-her-buum-vid
```

4. Veldu **Private** eða **Public**.
   - Ég myndi velja **Private** fyrst.
5. Ekki haka við README ef þú ætlar að hlaða allri möppunni beint inn.
6. Smelltu á **Create repository**.

---

## 5A. Einföld leið: Upload files í GitHub

1. Opnaðu nýja repo-ið.
2. Smelltu á **uploading an existing file** eða **Add file → Upload files**.
3. Dragðu **allt innihald möppunnar** inn.
   - Ekki draga zip-skrána sjálfa.
   - Draga þarf `app.py`, `requirements.txt`, `services`, `ui`, `.streamlit`, `data` o.s.frv.
4. Skrifaðu commit skilaboð:

```text
Initial deploy ready version
```

5. Smelltu á **Commit changes**.

---

## 5B. Betri leið: Git Bash

Ef þú vilt nota Git Bash:

```bash
cd path/to/island-her-buum-vid
git init
git add .
git commit -m "Initial deploy ready version"
git branch -M main
git remote add origin https://github.com/NOTANDANAFN/island-her-buum-vid.git
git push -u origin main
```

Skiptu `NOTANDANAFN` út fyrir þitt GitHub notandanafn.

---

## 6. Búa til Web Service á Render

1. Farðu á Render.
2. Smelltu á **New +**.
3. Veldu **Web Service**.
4. Tengdu GitHub reikninginn ef Render biður um það.
5. Veldu repo-ið:

```text
island-her-buum-vid
```

6. Stilltu:

```text
Name:
island-her-buum-vid

Runtime:
Python

Build Command:
pip install -r requirements.txt

Start Command:
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

7. Settu Environment Variable:

```text
PYTHON_VERSION = 3.11.9
```

8. Veldu plan.
   - Free gengur fyrir prufu.
   - Paid plan er betra ef þetta á að vera stöðugt vinnutól sem sefur ekki.

9. Smelltu á **Create Web Service**.

---

## 7. Fylgjast með deploy

Render opnar logs. Bíddu þar til þú sérð að appið hafi ræst.

Leitaðu að villum eins og:

- `ModuleNotFoundError`
- `SyntaxError`
- `Port`
- `No module named ...`

Ef allt gengur færðu slóð, t.d.:

```text
https://island-her-buum-vid.onrender.com
```

---

## 8. Prófa vefinn á Render

Opnaðu Render-slóðina.

Prófaðu:

- Forsíða
- Íslandskort
- Gagnaheilsa
- Suðurlandsvegir
- Ferðaráð Vallaskóla
- Landafræðiáskorun
- Verkefnabanki kennara

---

## 9. Setja inn í Google Sites

Í Google Sites:

1. Opnaðu síðuna.
2. Veldu **Embed / Fella inn**.
3. Settu Render-slóðina inn.
4. Stilltu stærð rammans.
5. Birta síðuna.

---

## 10. Uppfærslur seinna

Þegar við gerum nýja útgáfu:

1. Afþjappa nýja zip.
2. Setja nýjar skrár yfir gömlu möppuna.
3. Commit/push í GitHub.
4. Render deployar sjálfkrafa.

Ef þú notar upload í GitHub:
1. Dragðu nýju skrárnar inn.
2. Commit changes.
3. Render sér breytinguna og deployar.

---

## Mikilvægt

Render Web Service þarf að hlusta á:

```text
0.0.0.0
```

og nota portið sem Render gefur í:

```text
$PORT
```

Þess vegna er start command:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```
