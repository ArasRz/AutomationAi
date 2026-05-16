# Reflektion – Lektion 7
## Mobiltest, Felsökning & Testobservabilitet

---

## Övning 1 – Responsiva tester med Playwright

### Vad testar vi och varför?

Vi testar fyra skärmbredder: `iPhone SE` (375px), `iPhone 15 Pro` (430px),
`iPad` (768px) och `Desktop` (1920px). Anledningen är att en feature kan fungera
perfekt på desktop men vara helt oanvändbar på mobil — t.ex. en knapp som
hamnar bakom ett menyöverlapp eller en text som blir för liten att trycka på.

I Taxi Stockholm-appen är det kritiskt att `#book-taxi`-knappen alltid
är klickbar oavsett enhet. Om chauffören eller passageraren sitter med en
äldre iPhone och knappen inte visas korrekt missar man en bokning.

### `is_mobile` och `viewport` — vad händer bakom kulisserna?

```python
context = browser.new_context(
    viewport={"width": 375, "height": 667},
    is_mobile=True,
)
```

`viewport` styr CSS-mediaquerys — webbplatsen "ser" en 375px bred skärm.
`is_mobile=True` sätter dessutom `navigator.userAgent` till en mobil
UA-sträng och aktiverar touch-events istället för muskick. Utan `is_mobile`
kan sajter som identifierar enhetstyp via User-Agent visa desktoplayout
trots smal viewport.

### WCAG 2.5.5 – Touch Target Size

Standarden kräver minst 44×44px för alla interaktiva element på pekskärm.
Anledningen är fysiologisk: ett genomsnittligt fingeravtryck täcker ~57px.
Mindre knappar leder till felmissningar — extra allvarligt i en bokningsapp
där ett feltryck kan avboka fel taxi eller skicka föraren till fel adress.

```python
# Soft assertion-mönster: samla ALLA fel innan assert
violations = []
for btn in buttons:
    box = btn.bounding_box()
    if box["width"] < 44 or box["height"] < 44:
        violations.append(f"{btn} är {box['width']}×{box['height']}px")
assert not violations, "\n".join(violations)
```

Utan soft assertions stannar testet vid första felet och vi missar resten —
problematiskt när man vill se hela bilden på en release.

---

## Övning 2 – Failure-kategorisering och Root Cause Analysis

### De fyra kategorierna (T/D/I/B)

| Kategori | Beskrivning | Vanligt mönster |
|----------|-------------|-----------------|
| **T** – Timing | Element inte redo, AJAX ej klar | Många failures i samma CI-körning |
| **D** – Testdata | Föråldrad data, ändrad profil | Sporadic failures efter DB-migreringar |
| **I** – Infrastruktur | DB nere, certifikat, disk full | Alla tester i ett scope failar |
| **B** – Riktig bugg | Regression i appkoden | Reproducerbart lokalt OCH i CI |

### Varför är infrastrukturproblem viktigast att lösa först?

I TechRetail AB-exemplet (47 failures, 5.9%) var PostgreSQL nere (test #6).
Det orsakade sekundära TimeoutError i #1, #3, #8 — API:et var långsamt
p.g.a. databasbortfall, inte ett timing-problem i testerna.

Lektionen: **en enda root cause kan förklara 6 av 10 failures**.
Felsök alltid på mönster (vilket scope, vilken tid, vilka API-anrop) innan
du öppnar varje test individuellt.

### 5 Varför-metoden — lärdomar

Root cause för `test_login_success`-timeout:
> Rate limiting implementerades utan CI/CD IP-undantag.

De fem "varfören" tvingade oss från symptom (`#dashboard visas inte`)
till systemnivå (`CI-infrastruktur inte whitelistad i ny säkerhetsregel`).

**Konkret läxa för Taxi Stockholm:**
- Alla deployments ska ha ett "CI/CD-impact"-avsnitt i PR-beskrivningen
- Rate limiting, geoblocking och certifikatbyten ska alltid testas mot
  CI-miljöns IP innan de aktiveras i produktion

### Varför `wait_for_element()` istället för `time.sleep()`?

```python
# Dåligt: väntar alltid 3s, även om knappen dyker upp på 0.2s
time.sleep(3)
page.click("#book-taxi")

# Bra: väntar tills knappen faktiskt är klickbar
wait_for_element(page, "#book-taxi")
page.click("#book-taxi")
```

`sleep()` gör testet antingen för snabbt (instabilt) eller onödigt långsamt.
Explicit wait är deterministiskt: det passerar så snart villkoret är uppfyllt
och misslyckas med ett tydligt felmeddelande med URL och selector om det inte uppfylls.

### Retry — skyddsnät, inte lösning

```python
@with_retry(max_retries=2, backoff_base=0.5)
def bekrafta_bokning():
    page.click("#confirm-booking")
```

Exponentiell backoff (1s → 2s → 4s) ger systemet tid att återhämta sig
utan att bombardera det. Men om ett test **alltid** passerar på retry 2
finns ett underliggande timing-problem som ska åtgärdas — inte maskas.

---

## Övning 3 – Testobservabilitet

### De tre pelarna: Logs, Metrics, Traces

| Pelare | Vad det är | Verktyg i kursen |
|--------|-----------|------------------|
| **Logs** | Vad hände, när, vilket test | `TestLogger` → JSONL |
| **Metrics** | Aggregerade nyckeltal | `conftest.py` → `test_metrics.jsonl` |
| **Traces** | Anrop-spårning genom systemet | Playwright traces (network, screenshots) |

### Varför JSONL och inte vanlig textlog?

```bash
# Textlog — söker manuellt i tusentals rader
grep "FAILED" test.log

# JSONL — filtrerar exakt på fält, maskinläsbart
jq 'select(.status=="failed" and .suite_name=="bokningsflöde")' results.jsonl
```

JSONL är kompatibelt med Grafana Loki, Elasticsearch och Datadog.
För Taxi Stockholm innebär det att ops-teamet kan ställa in alerts direkt
på `pass_rate < 0.80` utan att skriva egna log-parsers.

### conftest.py-hooks — varför hookwrapper?

`@pytest.hookimpl(hookwrapper=True)` ger åtkomst till testresultatet
*efter* att pytest skapat det. Utan `hookwrapper` kan vi bara köra kod
*innan* testet — vi ser aldrig resultatet.

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield          # Pytest skapar rapporten
    report = outcome.get_result()   # Nu kan vi läsa den
    if report.failed:
        # Spara feltyp, duration etc.
```

Koden i testfilerna behöver inte ändras — hooks är transparenta.
Det är samma mekanism som pytest-html och pytest-cov använder.

### Dashboard — vad visar varje diagram?

| Diagram | Frågan det besvarar |
|---------|---------------------|
| **Pass Rate-trend** | Förbättras kvaliteten över tid? |
| **Körtid-trend** | Blir testerna långsammare (ny kod, mer fixtures)? |
| **Feltyper (doughnut)** | Dominerar TimeoutError? → timing-problem. AssertionError? → bugg. |
| **Långsammaste tester** | Vilka kandidater för optimering eller explicit wait? |

### Vad mäter vi inte — och varför spelar det roll?

Metrics-dashboarden visar *aggregerade* resultat. Den berättar inte
*varför* ett specifikt test är 8 sekunder långsamt eller vilket API-anrop
som är flaskhalsen. För det behövs Playwright traces:

```python
context = browser.new_context(record_video_dir="traces/")
# eller
page.tracing.start(screenshots=True, snapshots=True)
```

Kombinationen `metrics (vad) + traces (varför) + logs (när)` är
den kompletta observabilitetskedjan som används i produktion.

---

## Sammanfattning

| Lektion 7-koncept | Tillämpad i |
|-------------------|------------|
| Responsiv testning med 4 viewports | `test_responsive.py` |
| WCAG 2.5.5 touch targets | `test_responsive.py::test_touch_targets_mobile` |
| Explicit wait (deterministic) | `wait_utils.py` |
| Retry med exponentiell backoff | `retry_fixture.py` |
| Failure-kategorisering T/D/I/B | `failure_analysis.md` |
| 5 Varför-metoden | `failure_analysis.md` |
| Strukturerad JSONL-loggning | `test_logger.py` |
| Automatisk metrics-insamling | `conftest.py` |
| HTML-dashboard med Chart.js | `generate_dashboard.py` |
