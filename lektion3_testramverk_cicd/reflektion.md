# Lektion 3: CI/CD och Testramverk – Reflektion

## Praktisk övning: CI/CD-pipeline
Workflow-filen finns i: `.github/workflows/tester.yml`

Den kör automatiskt vid varje push till main och innehåller:
- Selenium-tester (lektion2_selenium_playwright/test_selenium_login.py)
- Playwright-tester (lektion2_selenium_playwright/test_playwright_login.py)
- Matrix-strategi som kör de två sviterna parallellt
- Automatisk rapportgenerering med --junit-xml

---

## Reflektionsfrågor

### Hur skulle du organisera testautomation i ett team med fem utvecklare och en testare?

I ett team med fem utvecklare och en testare är tydlig ansvarsfördelning avgörande.
Testaren bör äga teststrategin och se till att rätt saker testas på rätt nivå enligt
testpyramiden: många enhetstester, färre integrationstester och ett fåtal E2E-tester.
Utvecklarna bör skriva enhetstester för sin egen kod, medan testaren fokuserar på
integrations- och E2E-tester.

Koden bör organiseras lektion för lektion eller modul för modul med en gemensam
pages/-mapp för Page Objects som hela teamet delar. Varje ny sida i applikationen
får en egen page object-klass. På så sätt kan flera personer jobba i samma kodbas
utan att trampa varandra på tårna.

### Vilka designmönster skulle du välja och varför?

Page Object Model (POM) är det självklara valet. Det separerar lokalisatorer och
actions från testlogiken, vilket gör att om en knapp byter id behöver bara en fil
uppdateras. BasePage-mönstret ovanpå POM gör att gemensamma metoder som click()
och send_keys() skrivs en gång och ärvs av alla page objects.

För fixtures och setup används conftest.py så att driver-hanteringen är centraliserad
och inte upprepas i varje testfil. Det minskar duplicering och gör det enklare att
byta webbläsare eller lägga till headless-läge på ett ställe.

### Hur skulle du mäta testautomationens framgång?

Framgång mäts inte bara i antal tester utan i värde. Relevanta mätvärden är:

- Kodtäckning: hur stor del av applikationen täcks av tester
- Felupptäcktsgrad: hur många buggar hittas av automatiserade tester innan release
- Exekveringstid: hur lång tid tar testsviterna, och minskar den med parallellisering
- Stabilitet: hur många tester är "flaky" (misslyckas ibland utan anledning)
- Underhållskostnad: hur lång tid läggs på att uppdatera tester vid kodändringar

En pipeline som körs vid varje push och ger snabb feedback är i sig ett mått på
framgång — om ingen tittar på resultaten har automatiseringen inget värde oavsett
hur många tester som finns.
