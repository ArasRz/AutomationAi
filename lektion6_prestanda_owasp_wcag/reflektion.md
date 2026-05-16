# Lektion 6: Prestanda, Säkerhet & Tillgänglighetstest – Reflektion

Koduppgifterna finns i:
- `lektion6_prestanda_owasp_wcag/load_test_techretail.js` (Övning 1 – k6)
- `lektion6_prestanda_owasp_wcag/security_test_techretail.py` (Övning 2 – OWASP ZAP)
- `lektion6_prestanda_owasp_wcag/accessibility_test_techretail.py` (Övning 3 – axe-core)
- `lektion6_prestanda_owasp_wcag/test_broken_suite.py` (Självstudien)

---

## Reflektionsfrågor

### Fråga 1: Prestandatestning vs säkerhetstestning — skillnader och likheter

Prestandatestning och säkerhetstestning mäter var sitt icke-funktionellt
kvalitetsattribut, men de delar en viktig gemensam princip: beteendet under
onormal belastning avslöjar svagheter som inte syns vid normal användning.

En prestandatest simular tusentals parallella användare för att hitta flaskhalsar.
En säkerhetstest skickar medvetet felaktig input — SQL-strängar, XSS-vektorer —
för att hitta ingångspunkter som applikationen inte hanterar korrekt.

Skillnaden är syftet: prestandatestning söker efter kapacitetsgränser (när
kraschar systemet?), säkerhetstestning söker efter säkerhetsgränser (kan en
angripare ta sig in?). I praktiken hänger de samman — en Denial of Service-attack
är en prestandafråga orsakad av ett säkerhetsproblem.

Taxi Stockholm-koppling: om bokningssystemet inte klarar 500 simultana användare
under nyårsafton är det ett prestandaproblem. Om en angripare kan skicka
10 000 falska bokningsanrop och kraschla servern är det ett säkerhetsproblem
som manifesterar sig som prestandasvaghet (DoS via API-missbruk).

---

### Fråga 2: Manuell vs automatiserad tillgänglighetstestning

Automatiserade verktyg som axe-core täcker ungefär 30–40% av alla WCAG-kriterier.
De är utmärkta på tekniska kontroller: saknar en bild alt-text, är kontrasten
tillräcklig, har formulärfältet en label? Dessa kontroller görs konsekvent,
utan trötthet, och kan köras i varje CI/CD-pipeline.

Det som inte kan automatiseras är bedömningen av kontextuell rimlighet.
En bild kan ha alt-texten "bild 1" — tekniskt godkänd men oanvändbar.
En knapp kan ha aria-label="Klicka här" — tekniskt godkänd men inte
självförklarande. En tangentbordsnavigering kan följa rätt HTML-ordning
men ändå vara förvirrande för en skärmläsaranvändare om sidans logik
är svår att förstå.

Slutsats: automatiserade tester är ett nödvändigt golv, inte ett tak.
Axe-core och liknande verktyg fångar det uppenbara och snabba. Testning med
riktiga användare med funktionsnedsättningar är det enda sättet att verifiera
att systemet faktiskt är användbart — inte bara tekniskt kompatibelt.

---

### Fråga 3: Hur prioriterar du säkerhetsfynd?

OWASP ZAP returnerar fynd på fyra risknivåer: High, Medium, Low, Informational.
Prioriteringsordningen följer naturligt av risknivån, men det finns nuanser.

**High** åtgärdas alltid omedelbart. SQL Injection och Remote Code Execution
kan leda till fullständig kompromettering av systemet. Dessa blockerar release.

**Medium** bedöms i kontext. En saknad Secure-flagga på session-cookies är
Medium risk i allmänhet, men i ett betalningssystem för Taxi Stockholm höjer
det prioriteten — läckt session-token kan leda till bedrägliga bokningar.
Generellt åtgärdas Medium-issues inom nästa sprint.

**Low och Informational** samlas ihop och behandlas som teknisk skuld.
De är sällan akuta men bör hanteras systematiskt för att inte ansamlas.

Grundregeln: prioritera alltid det som ger en angripare störst tillgång med
minst ansträngning. SQL Injection i ett autentiserat formulär är mer allvarligt
än SQL Injection i ett offentligt sökfält utan känslig data.

---

### Fråga 4: Teknisk skuld inom tillgänglighet

Teknisk skuld i kod (otestad logik, hackiga workarounds) är välkänd.
Tillgänglighets-skuld är samma fenomen: ju fler WCAG-violations som
accepteras och skjuts upp, desto dyrare att åtgärda senare.

I en nybyggd applikation kostar det lite att lägga till alt-text på varje
bild, aria-label på varje knapp, och korrekt label på varje formulärfält.
Om dessa krav ignoreras under hela projektet och axe-core körs för första
gången tre veckor innan release, kan det finnas hundratals violations
spridda över hela kodbasen — en gigantisk refaktorering under tidspress.

Taxistockholm-lärdomen: integrera axe-core i CI/CD-pipelinen från dag ett.
Sätt ett tröskelgränsvärde (t.ex. noll critical-violations). Varje ny
komponent måste klara skanningen innan den mergas. Det är billigare att
fixa ett tillgänglighetsproblem direkt i pull requesten än sex månader senare
när UI-strukturen har förändrats.

Juridisk aspekt: EU:s tillgänglighetsdirektiv (WCAG 2.1 AA) är lag för
offentliga aktörer och delar av privat sektor. Att medvetet ackumulera
tillgänglighetsskuld kan innebära rättslig exponering, inte bara dålig UX.

---

### Fråga 5: AI och felsökning av icke-funktionella tester

AI-assistenter kan förkorta felsökningscykeln på tre sätt.

**Tolkning av felmeddelanden:** k6 returnerar statistik-tabeller med p50/p95/p99
och thresholds. En erfaren testare vet direkt vad det betyder. En junior
testare kan klistra in tabellen i ett AI-verktyg och få en förklaring:
"p95 = 847ms medan tröskeln är p95 < 500ms — 5% av dina anrop är långsammare
än 847ms, troligtvis databas-timeouts under hög last."

**Root cause-analys:** Om ett prestandatest fallerar kan AI hjälpa till att
koppla ihop symtom (hög latens på checkout-endpointen) med troliga orsaker
(N+1-frågor i ORM, saknat index, synkron extern API-anrop). AI kan föreslå
var i koden man bör börja titta.

**Generering av testfall:** Prompten "Generera ytterligare k6-testscenarier för
ett bookningsflöde med 1000 användare under Black Friday" ger ett startläge
som en testare kan anpassa — snabbare än att skriva från grunden.

Begränsning: AI förstår inte applikationens faktiska arkitektur, databas-schema
eller infrastruktur-konfiguration. Den kan ge riktningen — inte den exakta lösningen.
Det mänskliga omdömet om vad som faktiskt orsakar problemet i det specifika
systemet kan inte ersättas.
