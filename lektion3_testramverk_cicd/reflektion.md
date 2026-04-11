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

---

## Fördjupning: Testpyramiden i praktiken

### 1) Hur bör fördelningen mellan enhet-, integrations- och systemtester se ut?

I ett typiskt webbprojekt brukar en sund fördelning se ut ungefär så här:
70% enhetstester, 20% integrationstester och 10% E2E-tester (systemtester).

Enhetstester är snabba, billiga att skriva och köra, och ger omedelbar feedback.
De testar enskilda funktioner och klasser isolerat utan beroenden till databaser
eller webbläsare. I vårt projekt motsvaras de av test_unit.py som testar att
page object-klassernas konstanter och lokalisatorer är korrekt definierade.

Integrationstester verifierar att olika delar av systemet fungerar tillsammans,
till exempel att en inloggningsfunktion faktiskt kommunicerar rätt med servern.
Dessa är långsammare men fångar fel som enhetstester missar.

E2E-tester simulerar hela användarflöden i en riktig webbläsare, precis som
våra Selenium- och Playwright-tester gör. De är de mest värdefulla testerna ur
ett användarperspektiv men också de dyraste att skriva, underhålla och köra.
Därför ska de vara få men välvalda — fokus på de kritiska flödena som bokning,
betalning och inloggning.

### 2) Vilka risker uppstår vid en inverterad testpyramid?

En inverterad testpyramid innebär att teamet har fler E2E-tester än enhetstester.
Det är ett vanligt mönster i team som saknar en tydlig teststrategi, och det leder
till flera konkreta problem.

Det första problemet är hastighet. E2E-tester med webbläsare tar sekunder per test
medan enhetstester tar millisekunder. Med hundratals E2E-tester kan en pipeline ta
timmar, vilket gör att utvecklare slutar vänta på resultaten och pushar ändå.

Det andra problemet är instabilitet. E2E-tester är känsliga för nätverksproblem,
långsamma sidor och timing-problem. Dessa "flaky tests" misslyckas ibland utan
att något egentligen är fel, vilket skapar ett rop-som-vargar-syndrom där teamet
slutar lita på testerna.

Det tredje problemet är felsökning. När ett E2E-test misslyckas är det svårt att
veta exakt var felet uppstod — i frontend, backend, databas eller nätverk? Med
enhetstester isoleras felet omedelbart till en specifik funktion.

På Taxi Stockholm skulle en inverterad pyramid till exempel innebära att varje
ändring i bokningsflödet triggar tjugo webbläsartester i sekvens, medan ett
enkelt enhetstest hade kunnat fånga samma bugg på en sekund.

### 3) Hur kan kontraktstestning med Pact komplettera testpyramiden?

Kontraktstestning med Pact adresserar ett gap i den traditionella testpyramiden:
hur verifierar man att en frontend och en backend kommunicerar rätt med varandra
utan att köra ett fullständigt E2E-test?

Pact fungerar så att konsumenten (till exempel en mobilapp) definierar ett kontrakt
— exakt vilka API-anrop den gör och vilket format den förväntar sig tillbaka.
Producenten (backend-API:et) verifierar att den uppfyller kontraktet. Testerna körs
separat och snabbt, utan att båda systemen behöver vara uppe samtidigt.

Ett konkret exempel: om Taxi Stockholms app förväntar sig ett JSON-svar med fälten
"rideId", "driverId" och "estimatedTime", definieras det som ett kontrakt. Om
backend-teamet sedan byter namn på "estimatedTime" till "eta" fångas det direkt
i kontraktstestet — innan det når produktion och orsakar ett kraschande E2E-test
eller ännu värre, en kraschande app för riktiga kunder.

Pact placerar sig alltså mellan enhetstester och integrationstester i pyramiden
och minskar behovet av tunga E2E-tester för att verifiera API-kommunikation.
