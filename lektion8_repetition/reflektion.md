# Reflektion – Lektion 8
## Sammanfattning Del 1: Testautomationens Grundpelare (L1–L4)

---

## Repetitionsuppgifter (Självstudie)

### Uppgift 1 — Testpyramid för Taxi Stockholms app

**Applikation:** Taxi Stockholm bokningsapp (webb + mobil)

**Pyramid med 100 tester totalt:**

| Nivå | Antal | Exempel-testfall |
|------|-------|-----------------|
| **Enhet (70)** | 70 | `test_prisberakning_grundpris()`, `test_rabatt_vid_foretag()`, `test_validera_telefonnummer()`, `test_berakna_zon()` |
| **API/Integration (20)** | 20 | `test_POST_bokning_returnerar_201()`, `test_GET_forare_lista()`, `test_betalning_api_svarar_200()` |
| **E2E/GUI (10)** | 10 | `test_komplett_bokningsflode()`, `test_login_och_bokning()`, `test_avboka_bokning()` |

**Motivering:** Prisberäkning och validering är ren Python-logik — testar 10× snabbare som
enhetsfunktioner. API-testerna verifierar att backend-kontrakten håller. GUI-testerna
täcker de absolut viktigaste affärskritiska flödena.

---

### Uppgift 2 — Verktygsval för webbaserad bokhandel

**GUI-testverktyg:** Playwright

Motivering: Nytt projekt utan Selenium-legacy. Playwright har inbyggt auto-wait
(eliminerar `time.sleep`), stöd för responsiv testning med `is_mobile` och viewport,
och traces/video för felsökning. Dessutom enklare setup — `playwright install`
laddar ned webbläsare automatiskt.

**Testramverk:** pytest

Motivering: Bokhandeln är ett Python-projekt → pytest är det naturliga valet.
Fixtures hanterar setup/teardown, `@pytest.mark.parametrize` ger datadrivna tester
för produktkategorier och prisklasser. Ekosystemet (pytest-html, pytest-cov) ger
rapportering och täckningsmätning utan extra konfiguration.

**API-testverktyg:** requests + pytest

Motivering: Bokhandeln har ett REST API (produktkatalog, beställningar, betalning).
requests-biblioteket är enkelt och kraftfullt. Newman (Postman CLI) används för
explorativ testning under development.

---

### Uppgift 3 — CI/CD-pipeline för bokhandeln

```
Commit till feature-branch
  ↓
1. Enhetstester      (pytest tests/unit/ -v)           ~1 min
   → FAIL? Stoppa direkt (fail-fast)
  ↓
2. Linting           (flake8, mypy --strict)            ~30 s
  ↓
3. API-tester        (pytest tests/api/ -v)            ~3 min
  ↓
4. Deploy → staging (automatiskt om ovan passerar)
  ↓
5. GUI smoke-tester  (pytest tests/gui/ -m smoke)      ~5 min
  ↓
Merge-request: Godkänd för review

Nattlig cron (02:00):
  → Fullständig regression inkl. GUI (pytest tests/ -v)
  → pytest-html rapport
  → Metrics → dashboard
```

**Målvärden:**
| Metric | Mål |
|--------|-----|
| Pass rate | >95% |
| Kodtäckning | >75% |
| Flaky rate | <5% |
| Commit-feedback | <10 min |
| Full regression | <30 min |

---

### Uppgift 4 — 5 API-testfall för bokhandeln

| # | HTTP-metod | Endpoint | Förväntad kod | Verifierar |
|---|-----------|----------|---------------|-----------|
| 1 | GET | `/api/books?category=fiction` | 200 | Returnerar lista med böcker, `"category": "fiction"` i varje |
| 2 | POST | `/api/orders` (giltig payload) | 201 | Beställning skapas, response innehåller `order_id` |
| 3 | GET | `/api/books/99999` (finns ej) | 404 | Felmeddelande, inte servercrash |
| 4 | POST | `/api/orders` (utan auth-token) | 401 | Åtkomst nekad utan inloggning |
| 5 | POST | `/api/orders` (negativt antal) | 400 | Valideringsfel — antal < 1 är ogiltigt |

Test #3 och #5 är negativa testfall — de hittar edge cases som positiva tester missar.

---

## Reflektionsfrågor

### 1. Vad är jag mest säker på? Vad behöver jag repetera?

**Mest säker på:** API-testning (L4). HTTP-metoder, statuskoder och requests-biblioteket
sitter bra efter att ha skrivit faktiska API-tester i lektion 4. Kopplingen till
testpyramiden — "API-tester är billigast per bug" — är tydlig.

**Behöver repetera mest:** Selenium explicit wait vs implicit wait-kombinationer och
hur de interagerar. Det är lätt att glömma att man aldrig ska blanda dem, och
`WebDriverWait + expected_conditions`-syntaxen kräver övning för att sitta automatiskt.

---

### 2. Tre saker att göra först vid ny teststrategi

1. **Bedöm mognadsnivå** (TAMA-modellen) — Utan nulägesanalys väljs fel startpunkt.
   "Gör pilotprojekt" är fel råd till en organisation på nivå 4.

2. **Börja med enhetstester på befintlig affärslogik** — Direkt ROI, inga externa
   beroenden, enkelt att komma igång. Prisberäkning och validering i Taxi Stockholm-appen
   kan enhetstestas på en dag.

3. **Sätt upp CI/CD-pipeline** (om den saknas) — Utan automatisk körning vid varje
   commit minskar testernas värde dramatiskt. GitHub Actions gratis-tier räcker för start.

---

### 3. Hur har min syn på testautomation förändrats?

Innan kursen: Testautomation = klicka i webbläsaren med Selenium.

Nu: Testpyramiden är grundsynen. GUI-tester är *toppen* av pyramiden — dyra, bräckliga,
sista utvägen. Verklig testautomation börjar nedifrån med enhets- och API-tester.

Den viktigaste lärdomen: **Kultur > Verktyg.** En organisation kan köpa alla licenser
men ändå ha 0% automationsmognad om teamet inte har rätt mindset och ledarskapet
inte stödjer shift-left. L1 är viktigast, inte L2.

---

### 4. Realistisk mognadsnivå inom ett år för en typisk svensk IT-organisation

**Realistiskt: Nivå 2 → Nivå 3** (från Managed/Pilot till Defined/Standard).

Motivering: Nivå 3 kräver strategi, CI/CD-pipeline och dedikerade QA-roller — allt
detta är möjligt på ett år om ledningen engageras. Men nivå 4 (metrics-driven) och
nivå 5 (AI-prio) kräver flera år av disciplin och kulturförändring.

Förutsättningar för att nå nivå 3:
- Budget för 1–2 QA-ingenjörer
- Ledningens stöd (tid = pengar)
- Pilot med mätbar ROI för att motivera fortsatt investering
- GitHub Actions eller liknande CI/CD redan tillgängligt

---

## Fördjupade reflektionsfrågor

### 5. Hur övertyga skeptisk ledningsgrupp?

ROI är det starkaste argumentet: "Varje release tar testteamet 3 dagar manuellt.
Med automation tar det 20 minuter. Vid 2 releaser/månad sparar vi 70+ mantimmar
per månad — 35 000 kr vid 500 kr/h. Breakeven på automationsinvesteringen inom 6 månader."

Komplettera med riskargument: "En missad bugg i betalningsflödet kostade oss 150 000 kr
i förlorade transaktioner och kundkompensation i mars. Automation hade hittat den bugg
inom 20 minuter av deployment."

---

### 6. Vanligaste fallgroparna

1. **Automatisera GUI-tester först** — synligast för chefer men dyrast att underhålla.
2. **Underskatta underhållskostnaden** — 20% av automationstiden går till underhåll.
   Fel förväntningar → projektet avbryts när "testerna ständigt brister".
3. **Välja verktyg utan teamkompetens** — Cypress till ett Python-team = ödsla tid
   på att lära sig JavaScript.
4. **Inte involvera utvecklare** — Testautomation är teamansvar; QA ensamt klarar det inte.
5. **Hoppa över CI/CD-integrationen** — Tester som körs manuellt "ibland" ger inget
   kontinuerligt skyddsnät.

---

### 7. Ramverkval och teknisk stack

pytest passar Python-team (backend Flask/Django, skript, datavetenskap).
Cypress passar JavaScript-team (React, Vue, Angular frontend).
Robot Framework passar blandade team där testare utan programmeringsbakgrund
ska skriva tester — nyckelordsyntaxen är nästan naturligt språk.

Ramverkets ekosystem spelar stor roll: pytest-plugins (pytest-html, pytest-cov,
pytest-xdist för parallellkörning) ger omedelbar nytta. Cypress har inbyggd
skärminspelning — värdefullt för frontend-team som debuggar visuella buggar.

---

## Syntes: Den röda tråden L1–L4

```
L1 Organisationskultur    → Möjliggör allt. Utan rätt kultur fungerar inget.
       ↓
L2 Selenium & Playwright  → Verktygen för GUI-lagret (10% av pyramiden)
       ↓
L3 pytest & CI/CD         → Strukturen som gör tester körbara automatiskt
       ↓
L4 API-testning           → Det mest kostnadseffektiva lagret (20% av pyramiden)
       ↓
Enhetstester              → Grunden (70% av pyramiden) — L1–L4 förbereder för detta
```

**Röda tråden:** Mognad → Strategi → Verktyg → Pipeline → Kvalitet i produktion.
