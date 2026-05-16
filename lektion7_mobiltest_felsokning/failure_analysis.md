# Övning 2 – Failure-kategorisering och Root Cause Analysis
Lektion 7: Mobiltest, Felsökning & Testobservabilitet

---

## Del A: Failure-kategorisering (15 min)

TechRetail AB:s nattliga körning visade 47 misslyckade tester av 800 (5,9%
failure rate — normalt 1,5%). Nedan kategoriseras 10 representativa failures.

**Kategorier:**
- **T** = Timing (race condition, animation, lazy loading, AJAX ej klar)
- **D** = Testdata (föråldrad data, saknad testanvändare, ändrat pris)
- **I** = Infrastruktur (databas nere, nätverksfel, certifikat, disk full)
- **B** = Riktig bugg (regression i applikationskoden)

| # | Test | Felmeddelande | Kategori | Motivering |
|---|------|--------------|----------|------------|
| 1 | test_login_success | TimeoutError: waiting for #dashboard (30s) | **T** | Elementet finns men API svarar långsamt — sannolikt p.g.a. rate limiting i ny deploy |
| 2 | test_product_price | AssertionError: expected 499 got 599 | **B** | Priset ändrades i applikationen — trolig regression i prissättningslogiken |
| 3 | test_search_results | ElementNotVisibleError: .search-result | **T** | AJAX-laddning inte klar när testet söker elementet — behöver explicit wait |
| 4 | test_add_to_cart | StaleElementReferenceError | **T** | Sidan uppdaterades under pågående interaktion — elementreferens är gammal |
| 5 | test_checkout_address | AssertionError: "Stockholm" not in page | **D** | Adressen i testdata matchar inte — testanvändarens profil uppdaterades |
| 6 | test_order_history | ConnectionRefusedError: port 5432 | **I** | PostgreSQL-databasen är nere (port 5432 = Postgres) |
| 7 | test_product_image | AssertionError: image width 0px | **T/B** | Bilden laddades inte — kan vara timing (lazy load) eller trasig bild-URL |
| 8 | test_filter_category | TimeoutError: waiting for .product-list | **T** | Relaterat till #1 och #6 — databas nere gör API:t långsamt |
| 9 | test_user_profile | AssertionError: expected "Premium" got "Basic" | **D** | Testkontots prenumerationsstatus ändrades i testdatabasen |
| 10 | test_newsletter_signup | ElementClickInterceptedError: overlay | **T** | Cookie-banner/overlay blockerar knappen — behöver stängas före klick |

### Sammanräkning

| Kategori | Antal | Andel |
|----------|-------|-------|
| Timing (T) | 5–6 | ~55–60% |
| Testdata (D) | 2 | 20% |
| Infrastruktur (I) | 1 | 10% |
| Riktig bugg (B) | 1–2 | 10–15% |

### Prioriteringsordning

1. **Infrastruktur (#6) — åtgärda FÖRST**
   Databasen nere (port 5432) är troligtvis grundorsaken till timing-problemen
   i #1, #8 och delvis #3. Fixar du #6 försvinner sannolikt 4–5 andra failures.

2. **Riktig bugg (#2, #7) — eskalera till dev-teamet**
   Dessa representerar faktiska defekter i applikationskoden och ska rapporteras
   som buggar. Håll dem öppna tills de är fixade.

3. **Testdata (#5, #9) — snabb fix**
   Uppdatera testdata eller lägg till setup-logik som garanterar korrekt state.

4. **Timing (#3, #4, #10) — stabilisera med explicit wait**
   Åtgärda med `wait_for_element()` och overlay-hantering. Normalt enkla att fixa.

### Mönsteranalys

Failures #1, #3, #4, #8 och #10 är alla timing-relaterade OCH uppstod i
samma körning. Infrastrukturproblemet (#6 — databas nere) gör API:t långsamt,
vilket orsakar sekundära TimeoutError i #1 och #8. **En gemensam rotorsak
kan förklara 6 av 10 failures** — leta alltid efter sådana mönster innan du
felsöker varje test individuellt.

---

## Del B: Root Cause Analysis – 5 Varför-metoden (15 min)

### Testkandiat: `test_login_success` (failure #1)

**Symptom:** TimeoutError — `#dashboard`-elementet visades inte inom 30 sekunder.

**Bakgrundsinformation tillgänglig:**
- Testet passerade igår kväll (kl 02:00)
- CI-körning startade kl 02:00 som vanligt
- En deployment gjordes kl 01:45 (15 minuter före teststart)
- Deployen innehöll: *"Add rate limiting to login endpoint"*
- Tre andra tester med TimeoutError misslyckades också (alla med API-laddning)

---

**Varför 1:** Varför misslyckades testet?
→ Elementet `#dashboard` visades inte inom 30 sekunder efter login-klick.

**Varför 2:** Varför visades inte `#dashboard`?
→ Login-API:et svarade inte i tid — HTTP 429 (Too Many Requests) returnerades.

**Varför 3:** Varför returnerade API:et 429?
→ Den nya rate-limiting-regeln begränsar login-anrop till 5 per minut per IP.

**Varför 4:** Varför triggades rate limiten av testerna?
→ CI-servern kör alla tester parallellt från samma IP-adress och gör
  50+ login-anrop per minut — långt över gränsen på 5/minut.

**Varför 5:** Varför saknades undantag för CI-serverns IP?
→ **ROOT CAUSE:** Rate limiting-regeln implementerades utan att ta hänsyn
  till CI/CD-infrastrukturens IP-adress. Ingen testmiljö-whitelist skapades.

**Fix:** Lägg till CI-serverns IP i rate-limit-undantaget för testmiljön.
Alternativt: Återanvänd autentiserat session-token mellan tester istället för
att logga in för varje test (sparar både tid och API-anrop).

**Lärdomar:**
- Alla deployments till testmiljön ska ha ett "CI/CD-impact"-avsnitt i PR-beskrivningen
- Rate limiting ska alltid ha en explicit whitelist för testinfrastruktur
- Timing-problem som uppstår i CI men inte lokalt = miljöskillnad att undersöka

---

## Del C: Stabiliseringsverktyg

Se de skapade filerna för praktisk implementation:

| Fil | Innehåll |
|-----|----------|
| [`wait_utils.py`](wait_utils.py) | `wait_for_element()`, `wait_for_navigation()`, `wait_for_text()` |
| [`retry_fixture.py`](retry_fixture.py) | `retry_on_failure()` + `@with_retry` dekorator |

### Varför explicit wait istället för sleep?

```python
# FEL — väntar alltid 2 sekunder, oavsett när elementet är klart
import time
time.sleep(2)
page.click("#confirm")

# RÄTT — väntar tills elementet faktiskt är klickbart (snabbt + stabilt)
from wait_utils import wait_for_element
wait_for_element(page, "#confirm")
page.click("#confirm")
```

### Varför retry ska användas sparsamt

Retry-logik är ett **skyddsnät**, inte en lösning. Logga alltid retries:

```python
# Om detta test "passerar med retry 2" varje natt:
# → Det finns ett underliggande timing-problem
# → Loggen avslöjar mönstret
# → Åtgärda grundorsaken, ta bort retry
```
