# Lektion 5: AI-driven Testautomation – Reflektion

Koduppgiften finns i: `lektion5_ai_testautomation/test_security_basics.py`

---

## Reflektionsfrågor

### Fråga 1: AI och prestandatestning

Hur kan AI och maskininlärning förbättra prestandatestning jämfört med traditionella metoder?

Traditionell prestandatestning innebär att en testare manuellt definierar lastscenarier
och tolkar resultat i efterhand. AI kan förbättra detta på flera sätt. En ML-modell
tränad på historisk trafik kan automatiskt generera realistiska lastprofiler istället
för statiska Thread Groups i JMeter. Intelligent analys av prestandadata kan identifiera
flaskhalsar som är svåra att se för ögat — till exempel att svarstiden för ett specifikt
API-anrop ökar med 5 ms vid varje ny deploy, ett mönster som ingen testar för manuellt
men som ackumuleras till ett prestandaproblem.

Ett konkret exempel: en ML-modell kan jämföra 10 000 tidigare testresultat och flagga
att databasens svarstid börjar avvika från baseline redan när CPU-belastningen når 60%,
inte 90% som rullar uppgiften sätts för. Det ger tid att agera innan systemet kraschar.

---

### Fråga 2: Etik och säkerhetstestning

Under Lektion 5 diskuterades etik kring AI-testning och GDPR. Hur relaterar dessa
principer till säkerhetstestning?

Etik och säkerhetstestning hänger tätt ihop. Den grundläggande principen är att
säkerhetstestning — inklusive penetrationstestning — bara är laglig och etisk om
man har explicit tillstånd från ägaren av systemet. Att skanna en produktionsserver
utan tillstånd är olagligt oavsett syftet.

Gränsen för vad en testare bör göra vid penetrationstestning dras vid det som är
överenskommet i ett testmandat: vilka system, vilka metoder, under vilken tidsperiod.
Utanför det mandatet ska man aldrig agera, även om man hittar en uppenbar sårbarhet.

GDPR-perspektivet: testdata ska aldrig innehålla verkliga personnummer, e-postadresser
eller betalkortsdata. Taxi Stockholms testmiljö bör använda anonymiserad eller
syntetisk kunddata. Om ett dataläckage sker i testmiljön och den datan kan kopplas
till riktiga kunder är det ett GDPR-brott, oavsett att det var "bara ett test".

---

### Fråga 3: AI och tillgänglighetstestning

Kan AI-verktyg identifiera tillgänglighetsproblem som regelbaserade verktyg missar?

Ja, delvis. Regelbaserade verktyg som axe DevTools är utmärkta på att kontrollera
konkreta tekniska krav — saknar bilden en alt-text, har knappen tillräcklig kontrast,
är formulärfältet kopplat till en label? Dessa saker kan kontrolleras automatiskt.

Vad regelbaserade verktyg missar är kontext och semantik. En bild kan ha alt-texten
"bild" — tekniskt godkänt men helt oanvändbart för en skärmläsaranvändare. En AI
med förståelse för text kan bedöma om alt-texten faktiskt beskriver bildens innehåll.
På samma sätt kan AI utvärdera om ett navigeringsflöde är logiskt och förutsägbart
för en användare med kognitiv funktionsnedsättning, något som inga regler täcker.

Begränsningar: AI-baserade tillgänglighetstester kan inte ersätta testning med riktiga
användare med funktionsnedsättningar. En skärmläsaranvändare hittar problem som
varken axe DevTools eller AI förstår — till exempel att sidans logiska ordning är
bruten när man navigerar med Tab-tangenten.

---

### Fråga 4: Prompt engineering för icke-funktionell testning

Hur anpassas prompt-strategin för att generera icke-funktionella testfall?

Funktionella testfall testar vad systemet gör — loggar man in med rätt lösenord
kommer man till dashboarden. Icke-funktionella testfall testar hur — hur snabbt,
hur säkert, hur tillgängligt. Prompten måste specificera detta tydligt.

Exempel på en prompt för prestandatestscenarier för en e-handelsapplikation:

> "Du är en erfaren prestandatestare. Generera fem JMeter-testscenarier för
> en e-handelsapplikation under Black Friday-belastning. Applikationen
> hanterar produktsökning, produktsidor och kassaflöde. Inkludera:
> antal virtuella användare (ramp-up 100 → 1000 på 5 minuter), tänkbara
> flaskhalsar per scenario, och vilket SLA-gränsvärde (max svarstid i ms)
> som bör gälla för varje endpoint. Skriv allt på svenska."

Det som skiljer sig mot funktionella promptar är att man måste specificera
belastningsnivåer, mätvärden och acceptanskriterier — inte bara "vad ska hända".

---

### Fråga 5: Helhetsbilden

Lektion 5 visade att AI-driven testautomation handlar om att kombinera mänsklig
expertis med maskinens kapacitet. Hur gäller detta för de tre testområdena i Lektion 6?

Principen är densamma för alla tre: AI och automatiserade verktyg gör det repetitiva
och systematiska — mänsklig expertis avgör vad det betyder och vad som ska göras åt det.

**Prestandatestning:** JMeter kan automatiskt köra 1000 simultana användare och samla
statistik. Men en erfaren testare måste tolka om den uppmätta flaskhalsen sitter i
databasen, nätverket eller applikationskoden. Man bör alltid granska manuellt när
resultaten avviker oväntat från baseline.

**Säkerhetstestning:** OWASP ZAP kan automatiskt skanna efter kända sårbarheter, men
genererar många falska positiver. En testare måste verifiera varje fynd manuellt och
bedöma allvarlighetsgraden i sin specifika kontext. Automatiserade verktyg kan aldrig
ersätta en manuell kodgranskning av affärskritisk logik.

**Tillgänglighetstestning:** axe DevTools täcker de tekniska WCAG-kraven automatiskt,
men den mänskliga bedömningen — "är detta faktiskt användbart för en person med
funktionsnedsättning?" — kan aldrig automatiseras helt. Verktyg ger ett startläge,
men användartest med riktiga personer är det enda sättet att verifiera verklig
tillgänglighet.
