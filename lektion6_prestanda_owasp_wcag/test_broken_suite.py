"""
L6 Självstudien – Felsökning av trasig testsuite
Lektion 6: Prestanda, Säkerhet & Tillgänglighetstest

Din uppgift: Hitta och fixa de 3 buggarna i den här filen.
Varje test innehåller exakt ett fel.

Kör för att se felen:
    pytest test_broken_suite.py -v

När alla tre tester är gröna är uppgiften klar.

Tips: Läs felmeddelandet noggrant — pytest berättar vad som väntades
och vad som faktiskt hände.
"""

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Simulerade prestandadata
# (Föreställ dig att dessa kommer från ett k6-testresultat)
# ─────────────────────────────────────────────────────────────────────────────

# p95-svarstid i millisekunder för produktlistans endpoint
PRODUKTLISTA_P95_MS = 380

# Andel misslyckade anrop (1.5% = 0.015)
FELFREKVENS = 0.015

# HTTP-statuskod från inloggningssidan
LOGIN_STATUSKOD = 200


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1 – Svarstid
# Fel: fel tröskelsvärde i assert
# ─────────────────────────────────────────────────────────────────────────────

def test_produktlista_svarstid():
    """
    Verifierar att p95-svarstiden för produktlistan är under 400 ms.
    SLA-krav från TechRetail AB: p95 < 400 ms.

    Nuvarande p95: 380 ms → ska gå igenom (380 < 400).

    Hitta buggen: Vilket värde jämförs mot 320?
    """
    # BUG: Fel tröskelsvärde — ändra till rätt SLA-gräns
    assert PRODUKTLISTA_P95_MS < 350, (
        f"Produktlistans svarstid (p95) överstiger SLA: "
        f"{PRODUKTLISTA_P95_MS} ms (max tillåtet: 400 ms)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 – Felfrekvens
# Fel: jämförelseoperatorn är fel
# ─────────────────────────────────────────────────────────────────────────────

def test_felfrekvens_inom_gransen():
    """
    Verifierar att felfrekvensen inte överstiger 2% (0.02).
    Nuvarande felfrekvens: 1.5% (0.015) → ska gå igenom.

    Hitta buggen: Vilken operator används för jämförelsen?
    """
    MAX_FELFREKVENS = 0.02

    # BUG: Fel operator — ändra så att testet verifierar rätt villkor
    assert FELFREKVENS > MAX_FELFREKVENS, (
        f"Felfrekvensen är för hög: {FELFREKVENS:.1%} (max tillåtet: {MAX_FELFREKVENS:.0%})"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 – HTTP-statuskod
# Fel: fel förväntat värde i assert
# ─────────────────────────────────────────────────────────────────────────────

def test_login_svarar_korrekt():
    """
    Verifierar att inloggningssidan svarar med statuskod 200.
    Nuvarande statuskod: 200 → ska gå igenom.

    Hitta buggen: Vilket värde förväntas i assert?
    """
    # BUG: Fel förväntat värde — ändra till rätt HTTP-statuskod
    assert LOGIN_STATUSKOD == 201, (
        f"Inloggningssidan svarade med {LOGIN_STATUSKOD}, förväntade 200"
    )
