"""
Labb 4.2 – Datadriven API-testning med parametrize
Samma teknik som i Lektion 3 (söktermer) — men nu mot ett REST API.

Istället för att skriva ett test per endpoint skriver vi ett test
och matar in många olika endpoints/metoder som testdata.
"""

import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


# ─────────────────────────────────────────────
# ÖVNING 1: Testa flera endpoints med GET
#
# Varje rad = (endpoint, förväntat statuskod, beskrivning)
# ─────────────────────────────────────────────

@pytest.mark.parametrize("endpoint, forvantat_statuskod, beskrivning", [
    ("/users",          200, "Lista med alla användare"),
    ("/users/1",        200, "En specifik användare"),
    ("/posts",          200, "Lista med alla inlägg"),
    ("/posts/1",        200, "Ett specifikt inlägg"),
    ("/comments",       200, "Lista med alla kommentarer"),
    ("/todos",          200, "Lista med alla todos"),
    ("/users/99999",    404, "Obefintlig användare"),
    ("/invalid",        404, "Ogiltig endpoint"),
])
def test_get_endpoint(endpoint, forvantat_statuskod, beskrivning):
    """
    Testar att varje GET-endpoint returnerar rätt statuskod.
    Körs automatiskt en gång per rad i listan ovan.

    I ett riktigt projekt: verifiera att alla API-endpoints i
    Taxi Stockholms bokningssystem svarar korrekt.
    """
    svar = requests.get(f"{BASE_URL}{endpoint}")

    assert svar.status_code == forvantat_statuskod, (
        f"{beskrivning} ({endpoint}): "
        f"förväntade {forvantat_statuskod}, fick {svar.status_code}"
    )


# ─────────────────────────────────────────────
# ÖVNING 2: Verifiera att svaret innehåller rätt fält
#
# Varje rad = (endpoint, lista med fält som måste finnas)
# ─────────────────────────────────────────────

@pytest.mark.parametrize("endpoint, obligatoriska_falt", [
    ("/users/1",    ["id", "name", "email", "phone"]),
    ("/posts/1",    ["id", "title", "body", "userId"]),
    ("/comments/1", ["id", "name", "email", "body"]),
    ("/todos/1",    ["id", "title", "completed", "userId"]),
])
def test_svar_innehaller_ratt_falt(endpoint, obligatoriska_falt):
    """
    Kontraktstestning: verifierar att API:et alltid returnerar de fält
    som vår app förväntar sig.

    I ett riktigt projekt: om backend-teamet byter namn på ett fält
    (t.ex. 'email' → 'emailAddress') fångas det direkt här, innan
    det kraschar i appen för riktiga användare.
    """
    svar = requests.get(f"{BASE_URL}{endpoint}")
    assert svar.status_code == 200

    data = svar.json()
    for falt in obligatoriska_falt:
        assert falt in data, (
            f"Fältet '{falt}' saknas i svaret från {endpoint}. "
            f"Svaret innehöll: {list(data.keys())}"
        )


# ─────────────────────────────────────────────
# ÖVNING 3: Testa POST med olika payload
#
# Varje rad = (titel, body, userId, förväntat statuskod)
# ─────────────────────────────────────────────

@pytest.mark.parametrize("titel, body, user_id, forvantat_statuskod", [
    ("Giltig bokning",   "Resa från Arlanda till city", 1, 201),
    ("Annan användare",  "Resa från Bromma",            5, 201),
    ("Tom titel",        "Bara body, ingen titel",      1, 201),
])
def test_post_med_olika_data(titel, body, user_id, forvantat_statuskod):
    """
    Testar POST med olika kombinationer av indata.

    OBS: JSONPlaceholder accepterar alltid POST, även med saknade fält.
    I ett riktigt boknings-API skulle vi testa att:
      - Giltig data → 201
      - Saknad obligatorisk info → 400
      - Ogiltig användare → 404 eller 400
    """
    payload = {
        "title": titel,
        "body": body,
        "userId": user_id
    }

    svar = requests.post(f"{BASE_URL}/posts", json=payload)

    assert svar.status_code == forvantat_statuskod, (
        f"POST med titel='{titel}': "
        f"förväntade {forvantat_statuskod}, fick {svar.status_code}"
    )

    if forvantat_statuskod == 201:
        data = svar.json()
        assert "id" in data, "Svaret ska innehålla ett id för det skapade objektet"
