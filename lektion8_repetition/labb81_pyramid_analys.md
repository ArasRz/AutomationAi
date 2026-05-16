# Labb 8.1 – Testpyramid-analys för TechRetail AB
## Lektion 8: Sammanfattning Del 1

---

## Uppgift 1: Nuvarande fördelning

| Testnivå | Verktyg | Antal tester | Exekveringstid | Andel |
|----------|---------|--------------|----------------|-------|
| GUI-tester | Selenium | 120 | 45 min | **60 %** |
| API-tester | requests | 50 | 5 min | **25 %** |
| Enhetstester | pytest | 30 | 1 min | **15 %** |
| **Totalt** | – | **200** | **51 min** | **100 %** |

---

## Uppgift 2: Jämförelse med rekommenderad testpyramid

### Nuvarande vs Idealfördelning

```
NUVARANDE (TechRetail AB)        IDEAL (70/20/10)
─────────────────────────        ─────────────────
         ▲                              ▲
       ██████                         ██
    GUI  60%                       GUI  10%
   ██████████                      ██████
  API     25%                   API     20%
████████████████               █████████████████
Enhet       15%               Enhet         70%
```

**TechRetail AB har en INVERTERAD pyramid** — iskägel-mönstret.
Dyrast och långsammast dominerar; enhetstester (billigast, snabbast) är minst.

---

## Uppgift 3: Problem med inverterad pyramid

### Problem 1: Oacceptabelt lång körtid
51 minuter per körning × 10 körningar/dag = **510 minuter/dag = 8,5 h/dag** spenderas
på testning. Ledningens mål är <15 minuter — nuläget är 3,4× för långsamt.

Konsekvens: Teamet kör CI/CD mer sällan → färre commits valideras → större risker
vid varje release.

### Problem 2: Hög instabilitet (flaky tests)
GUI-tester med Selenium är känsliga för:
- AJAX-laddning som inte är klar → `TimeoutError`
- DOM-ändringar i frontend → `StaleElementReferenceError`
- Timingberoenden → tester failar sporadiskt utan riktig bugg

60% av testerna är GUI → 60% av testerna löper hög risk för instabilitet.
En instabil testsuite ignoreras → mister sitt QA-värde.

### Problem 3: Sen och dyr felsökning
Utan enhetstester hittas buggar i affärslogiken (prissättning, rabatter, validering)
FÖRST när GUI-testet kör hela flödet. Det tar 10–30 minuter att nå teststeget
→ buggen fixas sent → kostsam att reparera.

Forskning visar: buggar i production kostar 100× mer att fixa än i development.

---

## Uppgift 4: Migrationsplan med TAMA-modellen

**Nuvarande TAMA-nivå: 2 (Managed)**
- CI/CD finns (GitHub Actions)
- Automation pågår (200 tester)
- Men fördelning är fel → inte "Defined/Standard" (nivå 3)

### Fas 1 (Månad 1–2): Flytta affärslogik till enhetstester
Identifiera GUI-tester som testar affärslogik (inte visuell rendering):

| Kandidat för nedflyttning | Från | Till | Motivering |
|--------------------------|------|------|-----------|
| Prisberäkningar | GUI | Enhet | Ren Python-logik, inget UI behövs |
| Rabattvalidering | GUI | Enhet | Input/output-funktion |
| Kundvagnsberäkning | GUI | Enhet | Algebraisk logik |
| Formulärvalidering | GUI | API | Valideras i backend-endpoint |
| Produktsökning | GUI | API | REST-endpoint, ingen rendering |

**Mål fas 1:** 30 nya enhetstester, 10 nya API-tester, 20 GUI-tester borttagna.

### Fas 2 (Månad 3–4): Stabilisera kvarvarande GUI-tester
- Lägg till explicit wait på alla GUI-tester (eliminera `time.sleep`)
- Implementera Page Object Model (om det saknas)
- Identifiera och ta bort duplicerade GUI-tester

**Mål fas 2:** Flaky rate <5%, GUI-körtid <20 min.

### Fas 3 (Månad 5–6): Nå idealfördelning + metrics
- Fortsätt flytta ner tester
- Sätt upp testmetrics-dashboard
- Automatisera pipeline-rapportering

**Målfördelning:**

| Nivå | Nuläge | Mål |
|------|--------|-----|
| Enhet | 30 (15%) | 140 (70%) |
| API | 50 (25%) | 40 (20%) |
| GUI | 120 (60%) | 20 (10%) |

---

## Uppgift 5: Förväntad tidsvinst

**Beräkning med idealfördelning (200 tester totalt):**

| Nivå | Antal | Tid/test | Total tid |
|------|-------|---------|-----------|
| Enhetstester | 140 | 0,5 s | 70 s ≈ 1,2 min |
| API-tester | 40 | 3 s | 120 s = 2 min |
| GUI-tester | 20 | 30 s | 600 s = 10 min |
| **TOTALT** | **200** | – | **≈ 13,2 min** |

**Jämförelse:**

| | Nuläge | Idealläge | Förbättring |
|--|--------|-----------|-------------|
| Körtid | 51 min | 13 min | **−75%** |
| Mål (<15 min) | Ej uppnått | ✓ Uppnått | |
| Kostnad/dag (10 körn.) | 8,5 h | 2,2 h | −6,3 h/dag |

**Kostnadsbesparingar per år:**
```
Sparad tid/dag: 6,3 h × 500 kr/h = 3 150 kr/dag
Sparad tid/år:  3 150 × 220 arbetsdagar = 693 000 kr/år
```

### Vad kan inte konverteras?
- Tester som verifierar visuell rendering (bilder, layouter, animationer)
- Tester som kräver faktisk webbläsarinteraktion (autofyll, drag-and-drop)
- Komplett köpflöde E2E (ett sådant bör finnas — men bara ett)

Dessa 20 GUI-tester ska vara de *viktigaste* affärskritiska flödena: login, sökning,
lägg i kundvagn, checkout — och inget annat.
