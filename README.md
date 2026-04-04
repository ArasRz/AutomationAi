# Testautomation och AI inom IT-test

**Kurs:** Testautomation och AI inom IT-test | 30 YHP
**Skola:** Frans Schartaus Handelsinstitut
**Kursledare:** Kays Ismail
**Kurskod:** 8050
**Tentamen:** 27 maj 2026

## Om kursen

Kursen täcker två huvudspår:

**Testautomation Track**
- Automation grunder & testpyramiden
- Testverktyg & frameworks (Selenium, Playwright, Cypress, Appium)
- CI/CD integration

**AI & Innovation Track**
- AI/ML fundamentals
- LLM-assisterade tester & prompt engineering
- Hållbar testautomation

## Schema

| # | Lektion | Datum |
|---|---------|-------|
| 1 | Automationsmognad & organisationskultur | 25 mars |
| 2 | Selenium WebDriver och Playwright | 1 april |
| 3 | Testramverk, CI/CD, Continuous Testing | 8 april |
| 4 | API-testing, datadriven testning | 15 april |
| 5 | AI-driven testautomation, promptteknik | 22 april |
| 6 | Prestanda, OWASP, WCAG | 29 april |
| 7 | Mobiltest, felsökning, testobservabilitet | 6 maj |
| 8 | Sammanfattning och repetition | 13 maj |
| 9 | Sammanfattning och repetition | 20 maj |
| 10 | **Tentamen** | 27 maj |

## Repo-struktur

```
/
├── lektion1_automationsmognad/
├── lektion2_selenium_playwright/
├── lektion3_testramverk_cicd/
├── lektion4_api_datadriven/
├── lektion5_ai_testautomation/
├── lektion6_prestanda_owasp_wcag/
├── lektion7_mobiltest_felsokning/
├── lektion8_repetition/
├── lektion9_repetition/
└── lektion10_tentamen/
```

## Verktyg & Setup

- **Python** 3.13+
- **pytest** – testramverk
- **Selenium WebDriver** – webbautomation
- **Playwright** – modern webbautomation

### Installera beroenden

```bash
pip install pytest
pip install selenium
pip install playwright
```

## Testpyramiden

```
        /\
       /E2E\        ← UI/browser-tester (Selenium, Playwright)
      /------\
     / Integr \     ← API, service & databaskommunikation
    /----------\
   /  Enhetstest \  ← Snabba, isolerade funktionstester (pytest)
  /______________\
```

## Mognadsnivåer

| Nivå | Namn | Kännetecken |
|------|------|-------------|
| 1 | Ad Hoc | Manuella tester, ingen process |
| 2 | Repeterbar | Några automatiserade tester, basic tools |
| 3 | Definierad | Omfattande automation, CI/CD delvis |
| 4 | Optimerad | Full automation, AI-assisterade tester |

## Mål

Automatisera regressionstester för appar och hemsida, med fokus på repetitiva flöden som idag görs manuellt.
