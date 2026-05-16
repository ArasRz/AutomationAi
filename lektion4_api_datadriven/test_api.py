"""
Labb 4.1 – REST API-testning med requests
Testar det publika API:et JSONPlaceholder: https://jsonplaceholder.typicode.com

JSONPlaceholder är en gratis "fake" REST API som returnerar låtsasdata.
Det är perfekt för övningar eftersom det inte kräver konto eller autentisering.

Resurser som används:
  GET  /users        → lista med 10 användare
  GET  /users/{id}   → en specifik användare
  POST /posts        → skapa ett nytt inlägg (sparas inte på riktigt)
  PUT  /posts/{id}   → uppdatera ett inlägg
  DELETE /posts/{id} → ta bort ett inlägg
"""

import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


# ─────────────────────────────────────────────
# GET – hämta data
# ─────────────────────────────────────────────

def test_get_all_users():
    """
    GET /users → ska returnera 200 och en lista med användare.
    I ett riktigt projekt: verifiera att kundregistret laddas korrekt.
    """
    svar = requests.get(f"{BASE_URL}/users")

    assert svar.status_code == 200, f"Förväntade 200, fick {svar.status_code}"

    data = svar.json()
    assert isinstance(data, list), "Svaret ska vara en lista"
    assert len(data) > 0, "Listan ska inte vara tom"


def test_get_single_user():
    """
    GET /users/1 → ska returnera 200 och användaren med id 1.
    I ett riktigt projekt: verifiera att en enskild användarprofil hämtas korrekt.
    """
    svar = requests.get(f"{BASE_URL}/users/1")

    assert svar.status_code == 200

    data = svar.json()
    assert data["id"] == 1, "Fel id i svaret"
    assert "name" in data, "Svaret saknar fältet 'name'"
    assert "email" in data, "Svaret saknar fältet 'email'"


# ─────────────────────────────────────────────
# POST – skapa ny resurs
# ─────────────────────────────────────────────

def test_create_post():
    """
    POST /posts → ska returnera 201 (Created) och det skapade objektet.
    I ett riktigt projekt: verifiera att en ny bokning skapas korrekt.
    """
    ny_post = {
        "title": "Test",
        "body": "Det här är ett testinlägg",
        "userId": 1
    }

    svar = requests.post(f"{BASE_URL}/posts", json=ny_post)

    assert svar.status_code == 201, f"Förväntade 201 Created, fick {svar.status_code}"

    data = svar.json()
    assert data["title"] == "Test", "Titeln i svaret stämmer inte"
    assert "id" in data, "Svaret ska innehålla ett id för det skapade objektet"


# ─────────────────────────────────────────────
# PUT – uppdatera befintlig resurs
# ─────────────────────────────────────────────

def test_update_post():
    """
    PUT /posts/1 → ska returnera 200 och det uppdaterade objektet.
    I ett riktigt projekt: verifiera att en bokning kan ändras.
    """
    uppdaterad_post = {
        "id": 1,
        "title": "Updated",
        "body": "Uppdaterat innehåll",
        "userId": 1
    }

    svar = requests.put(f"{BASE_URL}/posts/1", json=uppdaterad_post)

    assert svar.status_code == 200

    data = svar.json()
    assert data["title"] == "Updated", "Den uppdaterade titeln syns inte i svaret"


# ─────────────────────────────────────────────
# DELETE – ta bort resurs
# ─────────────────────────────────────────────

def test_delete_post():
    """
    DELETE /posts/1 → ska returnera 200 (eller 204) utan felmeddelande.
    I ett riktigt projekt: verifiera att en avbokad resa tas bort.
    """
    svar = requests.delete(f"{BASE_URL}/posts/1")

    assert svar.status_code == 200, f"Förväntade 200, fick {svar.status_code}"


# ─────────────────────────────────────────────
# Felhantering – negativa testfall
# ─────────────────────────────────────────────

def test_get_nonexistent_user():
    """
    GET /users/99999 → ska returnera 404 (Not Found).
    I ett riktigt projekt: verifiera att en ogiltig kund-id hanteras korrekt.
    """
    svar = requests.get(f"{BASE_URL}/users/99999")

    assert svar.status_code == 404, (
        f"En obefintlig resurs ska ge 404, fick {svar.status_code}"
    )


def test_invalid_endpoint():
    """
    GET /invalid → ska returnera 404 för en okänd sökväg.
    I ett riktigt projekt: verifiera att felaktiga API-anrop hanteras säkert.
    """
    svar = requests.get(f"{BASE_URL}/invalid")

    assert svar.status_code == 404


def test_create_post_missing_fields():
    """
    POST /posts med tomt body → JSONPlaceholder returnerar ändå 201 eftersom det är
    en fake-API, men i ett riktigt system ska saknade obligatoriska fält ge 400.

    OBS: Detta test dokumenterar det faktiska beteendet hos JSONPlaceholder.
    I ett riktigt API (t.ex. Taxi Stockholms boknings-API) skulle svaret vara 400.
    """
    svar = requests.post(f"{BASE_URL}/posts", json={})

    # JSONPlaceholder är tolerant och returnerar 201 även för tomma anrop
    assert svar.status_code in (201, 400), (
        f"Förväntade 201 eller 400 för saknade fält, fick {svar.status_code}"
    )
