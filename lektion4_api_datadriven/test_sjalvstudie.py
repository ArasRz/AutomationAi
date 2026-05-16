"""
Självstudier – Lektion 4
API-testning med requests mot JSONPlaceholder

Din uppgift: Fyll i de 5 testfunktionerna nedan.
Använd test_api.py som referens om du fastnar.

API-dokumentation: https://jsonplaceholder.typicode.com
Tillgängliga resurser:
  /users      - användare
  /posts      - inlägg
  /comments   - kommentarer
  /todos      - att-göra-lista
  /albums     - album
  /photos     - foton
"""

import requests

BASE_URL = "https://jsonplaceholder.typicode.com"


# ─────────────────────────────────────────────
# TEST 1
# Hämta alla todos (att-göra-uppgifter) och verifiera att:
#   - statuskoden är 200
#   - svaret är en lista
#   - listan inte är tom
# ─────────────────────────────────────────────
def test_get_all_todos():
    # Skriv din kod här
    pass


# ─────────────────────────────────────────────
# TEST 2
# Hämta todo med id 1 och verifiera att:
#   - statuskoden är 200
#   - svaret innehåller fälten "id", "title" och "completed"
#   - id är 1
# ─────────────────────────────────────────────
def test_get_single_todo():
    # Skriv din kod här
    pass


# ─────────────────────────────────────────────
# TEST 3
# Skapa ett nytt album med POST till /albums
# Skicka med: title och userId
# Verifiera att:
#   - statuskoden är 201
#   - svaret innehåller ett "id"
#   - titeln i svaret stämmer med det du skickade
# ─────────────────────────────────────────────
def test_create_album():
    # Skriv din kod här
    pass


# ─────────────────────────────────────────────
# TEST 4
# Hämta ett comment med ett id som inte finns (t.ex. 99999)
# Verifiera att statuskoden är 404
# ─────────────────────────────────────────────
def test_get_nonexistent_comment():
    # Skriv din kod här
    pass


# ─────────────────────────────────────────────
# TEST 5
# Uppdatera todo med id 1 med PUT
# Skicka med: id, title, completed (sätt till True) och userId
# Verifiera att:
#   - statuskoden är 200
#   - "completed" i svaret är True
# ─────────────────────────────────────────────
def test_update_todo():
    # Skriv din kod här
    pass
