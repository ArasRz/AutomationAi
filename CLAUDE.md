# CLAUDE.md

## Om användaren

- Manuell testare på Taxi Stockholm
- Mål: Automatisera regressionstester för företagets appar och hemsida
- Går kursen "Testautomation och AI inom IT-test" (30 YHP) på Frans Schartaus Handelsinstitut
- Ny inom testautomation och programmering – förklara koncept tydligt med praktiska exempel

## Språk

Kommunicera på svenska om inget annat anges.

## Hur du hjälper

- Koppla alltid kodexempel till verkliga testscenarier (t.ex. bokning av taxi, inloggning, kartflöden)
- Förklara varför, inte bara hur
- Håll koden enkel och läsbar – prioritera tydlighet över elegans
- Påminn om testpyramiden när det är relevant: enhet → integration → E2E

## Projektstruktur

Koden är organiserad lektion för lektion:

```
lektion1_automationsmognad/
lektion2_selenium_playwright/
lektion3_testramverk_cicd/
lektion4_api_datadriven/
lektion5_ai_testautomation/
lektion6_prestanda_owasp_wcag/
lektion7_mobiltest_felsokning/
lektion8_repetition/
lektion9_repetition/
lektion10_tentamen/
```

## Verktyg som används i kursen

- **pytest** – testramverk (Python)
- **Selenium WebDriver** – webbautomation (Lektion 2)
- **Playwright** – modern webbautomation (Lektion 2)
- **Postman / requests** – API-testning (Lektion 4)
- **Appium** – mobiltestning (Lektion 7)
- **JMeter** – prestandatestning (Lektion 6)

## Köra tester

```bash
# Kör alla tester i en lektion
pytest lektion1_automationsmognad/ -v

# Kör specifik fil
pytest lektion1_automationsmognad/test_hello.py -v
```
