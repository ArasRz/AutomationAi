# Repetitionsquiz L1–L4 — Svar
## Lektion 8: Sammanfattning Del 1

---

## Frågor om testpyramid och automationsmognad (L1)

### Fråga 1 (G) — Testpyramiden

Testpyramiden består av tre nivåer med rekommenderad fördelning 70/20/10:

| Nivå | Andel | Verktyg | Egenskaper |
|------|-------|---------|------------|
| **Enhetstester** (botten) | 70 % | pytest, JUnit, Jest | Snabba, billiga, många |
| **API/Integrationstester** (mitten) | 20 % | Postman, requests | Medelsnabba |
| **E2E/GUI-tester** (toppen) | 10 % | Selenium, Playwright | Långsamma, dyra, få |

**Varför börja nedifrån?**
Enhetstester hittar buggar på källkodsnivå — billigast att fixa. GUI-tester är bräckliga: en
layoutändring bryter tio tester. Vanligt misstag är att börja med GUI-testautomation;
det ger snabb synlig demo men skapar en dyr, instabil testsuite.

I Taxi Stockholm-appen innebär det att man automatiserar prisberäkningslogiken
(enhet) och boknings-API:et (integration) *innan* man automatiserar hela
bokningsflödet i webbläsaren (GUI).

---

### Fråga 2 (G) — De fem mognadsnivåerna

| Nivå | Namn | Kännetecken |
|------|------|-------------|
| 1 | Initial/Ad hoc | Inga processer, sporadiska skript, allt manuellt |
| 2 | Managed/Pilot | Grundläggande planering, ett pilotprojekt startat |
| 3 | Defined/Standard | Strategi, CI/CD, dedikerade QA-roller, pyramidfördelning |
| 4 | Measured/Data | Metrics styr beslut, dashboards, pass rate >95% |
| 5 | Optimized/AI | Självläkande tester, AI-prioritering, kontinuerlig förbättring |

---

### Fråga 3 (VG) — Mognadsbedömning och plan till nivå 3

**Situationsbeskrivning:**
Två testare, allt manuellt, Selenium-licenser inköpta men oanvända.

**Bedömning:** Nivå 1–2 (Initial/Ad hoc → Managed). Verktyget är köpt men inte
implementerat — det räcker inte för nivå 2 utan praktisk användning.

**TAMA-analys:**
- **Kultur:** Nivå 1 — ingen automation-mindset, inget stöd för DevOps
- **Styrning:** Nivå 1 — ingen teststrategi
- **Organisation:** Nivå 2 — dedikerade testare finns
- **Resultat:** Nivå 1 — inga metrics, inga dashboards
- **Process:** Nivå 1 — inga CI/CD-steg

**Plan till nivå 3 (6 månader):**

| Fas | Tid | Åtgärd |
|-----|-----|--------|
| **Bedöm & Pilot** | Mån 1 | Välj 5–10 stabila regressionstester som pilot. Utbilda testarna i pytest + Selenium |
| **Visa värde** | Mån 2–3 | Kör piloten i CI (GitHub Actions). Mät tid sparad vs manuell körning. Visa för ledningen |
| **Skala upp** | Mån 4–6 | Bygg CI/CD-pipeline, lägg till API-tester, sätt pass rate >90% som mål, skapa dashboard |

Nyckel: Börja LITET och MÄTBART. "Vi sparar 4h/vecka" säljer bättre än "vi kör Selenium".

---

### Fråga 4 (G) — Shift-Left och Continuous Testing

**Shift-Left Testing** innebär att testare involveras redan i kravfasen, inte först när
koden är klar. Buggar hittas och fixas 10–100× billigare tidigt i cykeln. På Taxi Stockholm
skulle testaren sitta med i sprint planning och granska user stories innan development startar.

**Continuous Testing** innebär att tester körs automatiskt genom hela leveranskedjan —
vid varje commit, vid merge och vid deploy. Det är den tekniska implementation av shift-left
i ett CI/CD-system.

**Kopplingen till mognad:** Shift-Left är en kulturförändring (nivå 2→3),
Continuous Testing är den tekniska realiseringen (nivå 3→4).

---

### Fråga 5 (VG) — Pilot → Visa värde → Skala upp

**Varför inte automatisera allt på en gång?**
- Hög initial risk — fel verktygsval kostar månader
- Svårt att mäta ROI utan avgränsat scope
- Teamet hinner inte lära sig tillräckligt snabbt
- Om piloten misslyckas är skadan begränsad

**ROI-beräkning (exempel):**
```
Scenario: 50 regressionstester, 3 min/test manuellt = 150 min/körning
Körfrkvens: 3 gånger/vecka = 450 min/vecka = 7,5 h/vecka

Automationskostnad (engång): 40 h × 500 kr = 20 000 kr
Besparing per vecka:         7,5 h × 500 kr = 3 750 kr
Break-even:                  20 000 / 3 750 = ~5 veckor
ROI efter 1 år:              3 750 × 52 - 20 000 = 175 000 kr
```

**Pilot-strategin:**
1. Välj stabila, ofta körda tester med högt manuellt tidsvärde
2. Kör parallellt (manuellt + automatiserat) i 2 veckor för validering
3. Visa siffrorna för ledningen → godkänn utökning

---

## Frågor om Selenium, Playwright och POM (L2)

### Fråga 6 (G) — Selenium WebDriver-arkitektur

Selenium WebDriver kommunicerar via W3C WebDriver-protokollet (HTTP/JSON):

```
Testskript → WebDriver API → Browser Driver → Webbläsare → Webbapplikation
```

1. **Testskript** anropar WebDriver API (Python/Java/etc.)
2. **WebDriver API** skickar HTTP-requests till Browser Driver
3. **Browser Driver** (ChromeDriver, GeckoDriver) översätter till browserspecifika kommandon
4. **Webbläsaren** utför kommandon och returnerar svar

Sedan Selenium v4 är detta W3C-standardiserat — inga vendor-specific workarounds behövs.

---

### Fråga 7 (G) — Lokalisatorprioritet

**Prioritetsordning:**
1. **By.ID** — Snabbast, mest stabil. ID är unikt på sidan, direkt DOM-lookup.
2. **By.CSS_SELECTOR** — Flexibel och kraftfull (täcker ~90% av fallen). Kortare syntax än XPath.
3. **By.XPATH** — Mest flexibel men komplex och långsam (~10% av fallen).

**Varför ID > XPATH?**
- ID är unikt → ingen tvetydig matchning
- XPATH traverserar hela DOM-trädet → långsammare
- XPATH-uttryck som `//div[3]/table/tr[2]/td` brister vid minsta layoutändring

**När är XPATH nödvändigt?**
- Navigera uppåt i DOM (förälder-element): `//input[@id='email']/..`
- Textinnehållsmatchning: `//button[text()='Bekräfta bokning']`
- Komplexa relationer utan CSS-ekvivalent

---

### Fråga 8 (VG) — Selenium vs Playwright

| Egenskap | Selenium | Playwright |
|----------|----------|------------|
| Start | 2004 | 2020 |
| Skapare | ThoughtWorks/Community | Microsoft |
| Waits | Explicit krävs (WebDriverWait) | Auto-wait inbyggt |
| Browser setup | Extern ChromeDriver | Automatisk `playwright install` |
| Debugging | Standard | Traces + Video + Inspector |
| Arkitektur | HTTP/JSON W3C-protokoll | CDP/WebSocket (direktkommunikation) |
| Community | Störst | Snabbast växande |
| Mobiltestning | Appium-integration | `is_mobile`, viewport-emulering |

**När välja Selenium?**
- Befintlig kodbas i Selenium (migrationskostnad)
- Enterprise-miljö med legacy-system
- Kräver Appium-integration
- Teamet kan Java/C# bättre än Python

**När välja Playwright?**
- Nytt projekt utan legacy-beroenden
- Behöver responsiv testning (mobil-emulering)
- Vill ha traces och video out-of-the-box
- JavaScript/TypeScript frontend-team

---

### Fråga 9 (G) — Page Object Model (POM)

**POM-mönstret** separerar *sidelogik* (lokalisatorer + metoder) från *testlogik* (assertions).
Varje webbsida representeras av en klass.

```
pages/
  login_page.py     ← Lokalisatorer + login(), get_error()
  dashboard_page.py ← Lokalisatorer + get_title()
tests/
  test_login.py     ← Använder LoginPage, gör assertions
```

**Tre fördelar:**
1. **Underhållbarhet** — Byt lokalisator på ETT ställe, inte i varje test
2. **Läsbarhet** — `login_page.login("admin", "123")` läses som naturligt språk
3. **Återanvändbarhet** — Samma sidklass används i hundra tester

**Utan POM:** Om `#login-btn` döps om till `#submit-btn` → 47 tester bröts.
**Med POM:** Ändra på ett ställe i `LoginPage.LOGIN_BUTTON`.

---

## Frågor om ramverk och CI/CD (L3)

### Fråga 10 (G) — pytest vs Robot Framework vs Cypress

| | pytest | Robot Framework | Cypress |
|--|--------|-----------------|---------|
| Språk | Python | RF-syntax (keyword-driven) | JavaScript |
| Stil | Kodbaserad | Keyword-driven, BDD-liknande | Kodbaserad |
| Målgrupp | Tekniska Python-team | Blandade team (testare utan kod) | Frontend JS-team |
| Rapporter | Via plugins (pytest-html) | Inbyggd HTML-rapport | Inbyggd video |
| Styrka | Flexibilitet, ekosystem | Lättläst syntax, ingen kodkunskap | Snabb setup i JS-projekt |

**Välj pytest** för Python-backend + tekniskt QA-team (som i kursen).
**Välj Robot Framework** om icke-tekniska testare ska skriva tester.
**Välj Cypress** om frontendutvecklare ansvarar för E2E-tester i ett React/Angular-projekt.

---

### Fråga 11 (G) — AAA-mönstret

**Arrange-Act-Assert:**
- **Arrange** — Förbered testdata, starta webbläsare, logga in
- **Act** — Utför den *enda* handling som testet verifierar
- **Assert** — Verifiera att resultatet är det förväntade

```python
def test_successful_login(driver):
    # Arrange
    login_page = LoginPage(driver)
    driver.get("https://example.com/login")

    # Act
    login_page.login("admin", "secret123")

    # Assert
    assert "Dashboard" in driver.title
```

**Varför viktigt?** AAA tvingar fram tester med ett enda ansvar — lättare att förstå
varför ett test misslyckas. Utan AAA blandas setup och assertions, vilket gör felsökning svår.

---

### Fråga 12 (VG) — Komplett CI/CD-pipeline

**Steg i ordning (fail-fast-principen — snabbaste tester körs först):**

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    steps:
      1. Checkout kod
      2. Sätt upp Python-miljö
      3. Installera dependencies (pip install -r requirements.txt)
      4. Enhetstester (pytest tests/unit/ -v)            # ~2 min
      5. API-tester (pytest tests/api/ -v)               # ~5 min
      6. Linting/kodkvalitet (flake8, mypy)
      7. GUI-tester headless (pytest tests/gui/ -v)      # ~20 min
      8. Generera HTML-rapport (pytest-html)
      9. Deploy till staging (om alla tester passerar)
```

**Testmetrics att följa:**
| Metric | Målvärde |
|--------|----------|
| Kodtäckning | >70% |
| Pass rate | >95% |
| Flaky rate | <5% |
| Total körtid | <30 min |
| Antal tester per kategori | 70/20/10 |

---

## Frågor om API-testning (L4)

### Fråga 13 (G) — HTTP-metoder och statuskoder

| Metod | Syfte | Lyckad statuskod |
|-------|-------|-----------------|
| GET | Hämta resurs | 200 OK |
| POST | Skapa resurs | 201 Created |
| PUT | Uppdatera hel resurs | 200 OK |
| DELETE | Radera resurs | 200 OK (eller 204 No Content) |

**Felkoder att känna:**
- 400 Bad Request — felaktig request-payload
- 401 Unauthorized — saknar auth-token
- 403 Forbidden — har token men saknar rättigheter
- 404 Not Found — resursen finns inte
- 500 Internal Server Error — serverfel

---

### Fråga 14 (G) — Datadriven testning med JSON

```python
# testdata/bokningar.json
[
  {"pickup": "Arlanda", "destination": "Stockholm C", "expected_status": 200},
  {"pickup": "",        "destination": "Stockholm C", "expected_status": 400},
  {"pickup": "Arlanda", "destination": "",            "expected_status": 400}
]
```

```python
# test_api_bokning.py
import json
import pytest
import requests

with open("testdata/bokningar.json") as f:
    TESTDATA = json.load(f)

@pytest.mark.parametrize("fall", TESTDATA)
def test_skapa_bokning(fall):
    response = requests.post(
        "https://api.taxistockholm.se/bookings",
        json={"pickup": fall["pickup"], "destination": fall["destination"]}
    )
    assert response.status_code == fall["expected_status"]
```

**Fördelar:** Testlogiken ändras ALDRIG — bara JSON-filen. Testare utan Python-kunskap
kan lägga till nya testfall.

---

### Fråga 15 (VG) — API vs GUI-testning: kostnadseffektivitet

**API-tester är billigare av tre skäl:**
1. **Hastighet** — API-test tar 10–200ms, GUI-test tar 5–30 sekunder = 100× snabbare
2. **Stabilitet** — Inga `StaleElementReferenceError`, inga timing-problem med AJAX
3. **Underhåll** — API ändras sällan; frontend-layouten ändras hela tiden

**Prioriteringsstrategi för e-handelsplattform:**

```
Enhet (70%): prisberäkning, rabattlogik, valideringsregler, sessionhantering
API  (20%): produktkatalog CRUD, orderflöde, betalnings-API, autentisering
GUI  (10%): komplett köpflöde (E2E), inloggning, checkout-bekräftelsesida
```

Nyckeln: *Testa affärslogiken på lägsta möjliga nivå.*
Rabattprocenten testas som en Python-funktion (0,5s), inte som ett GUI-flöde (30s).

---

## Ytterligare frågor om testdesigntekniker och DevOps (L1–L4)

### Fråga 16 (G) — Ekvivalenspartitionering

Ekvivalenspartitionering delar indata i klasser där alla värden förväntas bete sig identiskt.
Det räcker att testa ett värde per klass — de övriga ger inget nytt informationsvärde.

**Exempel: ålder 18–65:**

| Klass | Område | Testvärde | Förväntat |
|-------|--------|-----------|-----------|
| Ogiltig (för ung) | < 18 | 15 | Felmeddelande |
| Giltig | 18–65 | 35 | Godkänd |
| Ogiltig (för gammal) | > 65 | 70 | Felmeddelande |
| Ogiltig (negativ) | < 0 | -5 | Felmeddelande |

Vanligt misstag: glömma ogiltiga klasser — det är där buggar ofta gömmer sig.

---

### Fråga 17 (G) — Gränsvärdesanalys

Gränsvärdesanalys kompletterar ekvivalenspartitionering genom att testa *exakt vid gränserna*
där beteendet förändras — mest buggar uppstår där.

**Värden 1–100:**

| Värde | Typ | Varför testa? |
|-------|-----|---------------|
| 0 | Precis under nedre gräns | Off-by-one: accepteras 0 av misstag? |
| 1 | Precis på nedre gräns | Lägsta giltiga värde |
| 2 | Precis över nedre gräns | Normalt giltigt värde |
| 99 | Precis under övre gräns | Normalt giltigt värde |
| 100 | Precis på övre gräns | Högsta giltiga värde |
| 101 | Precis över övre gräns | Off-by-one: accepteras 101 av misstag? |

---

### Fråga 18 (G) — pytest fixtures och scope

**Fixtures** ersätter `setUp/tearDown` med dependency injection. pytest hittar dem via
namn i testfunktionens parametrar — ingen import behövs om de är i `conftest.py`.

| Scope | Livslängd | Typiskt användningsfall |
|-------|-----------|------------------------|
| `function` (default) | Varje testfunktion | Webbläsarinstans, isolerad testdata |
| `class` | Varje testklass | Delat state inom en klass |
| `module` | Varje .py-fil | Databasanslutning per testfil |
| `session` | Hela körningen | Autentiserings-token (en inloggning för alla tester) |

**Session-scope-exempel:**
```python
@pytest.fixture(scope="session")
def auth_token():
    response = requests.post("/auth/login", json={"user": "admin", "pass": "123"})
    return response.json()["token"]  # Loggar in EN gång, återanvänds i alla API-tester
```

Varning: Använd aldrig session-scope för testdata som förändras — det skapar beroenden
mellan tester och leder till flaky tests.

---

### Fråga 19 (VG) — Kontraktstestning

**Kontraktstestning** verifierar att ett API-kontrakt (strukturen på request/response)
uppfylls — utan att köra hela systemet. Vanligaste verktyg: Pact.

**Skillnad mot integrationstestning:**
| | Integrationstestning | Kontraktstestning |
|--|---------------------|------------------|
| Kräver | Båda systemen igång | Bara ett system + mock |
| Testar | Hela flödet | Kontraktet (schema) |
| Hastighet | Sekunder–minuter | Millisekunder |
| Isolering | Låg | Hög |

**Scenario:**
Taxi Stockholm har en Pricing Service som anropas av Booking Service. Pricing Service
byter fältnamnet `price` till `amount` i sitt JSON-svar. Utan kontraktstestning
deployas ändringen → Booking Service kraschar i produktion → kunder kan inte boka.
Med kontraktstestning (Pact) hade konsumenten (Booking Service) definierat att den
förväntar sig fältet `price` → testet failar direkt vid deploy av Pricing Service.

**Nackdelar:** Kräver att båda teamen underhåller kontraktet. Mer overhead än enkel
schemavalidering. Mest värde i microservice-arkitekturer med många tjänster.

---

### Fråga 20 (G) — DevOps

**DevOps** är en kultur och metodologi som bryter silos mellan Development (Dev) och
Operations (Ops). Centrala principer: collaboration, continuous integration, continuous
delivery, infrastructure as code, monitoring.

**Koppling till testautomation:**
- CI: automatiserade tester körs vid varje commit → omedelbar feedback
- CD: deploy sker bara om alla tester passerar → trygg leverans
- Monitoring (Shift-Right): tester körs även i produktion (synthetic monitoring)

**I en DevOps-pipeline:**
```
Commit → Build → Enhetstester → API-tester → GUI-tester → Deploy → Monitor
```

---

### Fråga 21 (VG) — Optimera CI/CD-pipeline (2 min + 15 min + 45 min)

**Problem:** 62 minuter total körtid — blockerar snabba releaser.

**Strategi:**

1. **Dela upp i steg (fail-fast):**
   ```
   Push-trigger:  Enhetstester (2 min) → API-tester (15 min) → Deploy staging
   Nattlig cron:  GUI-tester (45 min) + fullständig regression
   Merge-request: Enhet + API + urval GUI (smoke tests, ~5 min)
   ```

2. **Parallellisering:**
   ```yaml
   jobs:
     unit-tests:
     api-tests:
     gui-tests:
       strategy:
         matrix: [Chrome, Firefox]  # Parallella browserkörningar
   ```

3. **Testprioritering:**
   - Smoke tests (20 viktigaste tester) på varje commit
   - Fullständig regression vid merge till main

4. **Testpyramids princip:** 45 minuter GUI = systemet har för många GUI-tester.
   Kandidater för nedflyttning: affärslogiktester som råkar vara GUI-tester.

**Mål:** Commit-feedback på <10 min. Full regression nattligen.

---

## Fördjupningsfrågor (L1–L4)

### Fråga 22 (G) — TechRetail AB: 50 GUI + 5 enhet + 0 API

**Nuvarande fördelning:**
- GUI: 50/55 = **91%** ← Alldeles för högt
- Enhet: 5/55 = **9%** ← Alldeles för lågt
- API: 0/55 = **0%** ← Saknas helt

**Problem:** "Iskägel" (inverted pyramid) — mest bräckliga, långsammaste tester dominerar.

**Tre konsekvenser:**
1. **Lång körtid** — 50 GUI-tester × 30s = 25 min vs 50 enhetstester × 0,5s = 25s
2. **Instabilitet** — GUI-tester failar p.g.a. timing, AJAX, layoutändringar
3. **Sen feedback** — Buggar hittas sent när de är dyra att fixa

**Organisationskulturens roll:** Teamet prioriterade "synbara demo-tester" — typiskt
när testare och utvecklare inte kommunicerar och ledningen mäter antal automatiserade tester
snarare än kvalitet. Fixas med Shift-Left och gemensam definition of done.

---

### Fråga 23 (VG) — Flaky tests: blandat implicit + explicit wait

**Vad händer när de blandas?**
Selenium *staplar* timeouts: om implicit wait = 10s och explicit wait = 5s kan
den faktiska väntetiden bli 10–15s (oförutsägbart). Och ett element som hittades
"implicit" kanske inte är interagierbart ännu → `ElementNotInteractableException`.

**Rekommendation för TechRetail:**
1. **Ta bort ALL `driver.implicitly_wait()`** — sätt den till 0
2. Ersätt med explicit wait för varje interaktion:
   ```python
   # Bort:
   driver.implicitly_wait(10)
   driver.find_element(By.ID, "confirm").click()

   # In:
   WebDriverWait(driver, 10).until(
       EC.element_to_be_clickable((By.ID, "confirm"))
   ).click()
   ```
3. Flytta `WebDriverWait`-skapandet till `BasePage.__init__` för att undvika duplicering
4. `time.sleep()` är aldrig acceptabelt — det maskerar timing-problem utan att lösa dem

---

### Fråga 24 (G) — pytest markers och parametrize

**Markers:**
```python
@pytest.mark.smoke         # Kör med: pytest -m smoke
@pytest.mark.skip(reason="Kräver VPN")
@pytest.mark.xfail         # Förväntas faila (känd bugg)
```

**`@pytest.mark.parametrize`:**
```python
@pytest.mark.parametrize("inköpspris,rabatt,förväntat", [
    (100, 0.10, 90),    # 10% rabatt
    (200, 0.20, 160),   # 20% rabatt
    (0,   0.50, 0),     # Nollpris
    (100, 1.00, 0),     # 100% rabatt
    (100, 1.10, None),  # Ogiltig rabatt >100%
])
def test_rabattberakning(inköpspris, rabatt, förväntat):
    if förväntat is None:
        with pytest.raises(ValueError):
            berakna_rabatt(inköpspris, rabatt)
    else:
        assert berakna_rabatt(inköpspris, rabatt) == förväntat
```

5 testfall med EN funktion. Utan parametrize → 5 separata funktioner med identisk struktur.

---

### Fråga 25 (VG) — conftest.py-hierarki

**Vad är conftest.py?**
En speciell pytest-fil som automatiskt laddas. Fixtures definierade här är tillgängliga
för alla tester i samma mapp och undermappar — utan import.

**Hierarki för TechRetail (80 testfiler):**
```
tests/
  conftest.py           ← Fixtures tillgängliga ÖVERALLT
    db_session          (scope=session) — EN databasanslutning för hela körningen
    api_base_url        (scope=session) — Bas-URL från miljövariabel

  unit/
    conftest.py         ← Fixtures bara för enhetstester
      mock_price_calc   — Mockad prisberäkning

  api/
    conftest.py         ← Fixtures bara för API-tester
      auth_token        (scope=session) — Autentiserings-token
      api_client        — requests.Session med headers

  gui/
    conftest.py         ← Fixtures bara för GUI-tester
      driver            (scope=function) — En Chrome-instans per test
      login_page        — Förloggad LoginPage
```

**Regler:**
- `session`-scope i root-conftest (dyra setup)
- `function`-scope i gui/conftest (isolering)
- Aldrig allt i en enda conftest.py — det ger beroenden mellan testtyper
