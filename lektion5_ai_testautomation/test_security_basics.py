"""
Lektion 5 – Koduppgift: Säkerhetstestning med pytest
Kopplar ihop AI-driven testning (L5) med säkerhetstestning (L6).

Tre testklasser:
  1. TestSQLInjection   — verifiera att SQL-injection-strängar saneras
  2. TestXSS            — verifiera att HTML-taggar escapas
  3. TestSecurityHeaders — verifiera att säkerhetsrelaterade HTTP-headers finns

OBS: sanitize_input() simulerar vad en riktig applikation bör göra.
I ett riktigt system (t.ex. Taxi Stockholms bokningsformulär) skulle
denna logik sitta i backend och förhindra att angripare manipulerar
databasen eller injicerar JavaScript i andra användares webbläsare.
"""

import pytest


# ─────────────────────────────────────────────
# Testdata — attackvektorer
# ─────────────────────────────────────────────

SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT * FROM users --",
    "admin'--",
]

XSS_PAYLOADS = [
    '<script>alert("XSS")</script>',
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
]


# ─────────────────────────────────────────────
# Sanerings-funktion
# Ersätt med din applikations faktiska logik i ett riktigt projekt.
# ─────────────────────────────────────────────

def sanitize_input(user_input: str) -> str:
    """
    Enkel sanitering — tar bort tecken som är farliga i SQL och HTML.
    I produktion används parameteriserade SQL-frågor och HTML-escaping
    via ramverkets inbyggda funktioner (t.ex. Jinja2 autoescape i Flask).
    """
    dangerous_chars = ["'", '"', ";", "--", "<", ">", "script"]
    result = user_input
    for char in dangerous_chars:
        result = result.replace(char, "")
    return result


# ─────────────────────────────────────────────
# KLASS 1: SQL-injection
# Taxi Stockholm-koppling: bokningsformuläret tar emot kunddata —
# en angripare som skickar SQL-kod i namnfältet ska inte kunna
# manipulera bokningsdatabasen.
# ─────────────────────────────────────────────

class TestSQLInjection:
    """Tester för SQL-injection-skydd."""

    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_login_rejects_sql_injection(self, payload):
        """
        Verifiera att SQL-injection-strängar saneras bort.
        Enkla citattecken och SQL-kommentarer (--) är de vanligaste vektorerna.
        """
        sanitized = sanitize_input(payload)

        assert "'" not in sanitized, (
            f"Enkla citattecken hittades i sanerad output: '{sanitized}'"
        )
        assert "--" not in sanitized, (
            f"SQL-kommentarer hittades i sanerad output: '{sanitized}'"
        )


# ─────────────────────────────────────────────
# KLASS 2: XSS (Cross-Site Scripting)
# Taxi Stockholm-koppling: om en angripare kan injicera JavaScript
# i t.ex. ett kommentarsfält kan de stjäla andra kunders sessions-cookies
# och ta över deras konton.
# ─────────────────────────────────────────────

class TestXSS:
    """Tester för XSS-skydd (Cross-Site Scripting)."""

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_input_escapes_html(self, payload):
        """
        Verifiera att HTML-taggar (<, >) escapas och inte når webbläsaren.
        En webbläsare som ser <script> kör koden — det måste förhindras.
        """
        sanitized = sanitize_input(payload)

        assert "<" not in sanitized, (
            f"HTML-tagg (<) hittades i sanerad output: '{sanitized}'"
        )
        assert ">" not in sanitized, (
            f"HTML-tagg (>) hittades i sanerad output: '{sanitized}'"
        )


# ─────────────────────────────────────────────
# KLASS 3: Säkerhetsrelaterade HTTP-headers
# Taxi Stockholm-koppling: dessa headers talar om för webbläsaren
# hur den ska skydda användaren — t.ex. att blockera sidan från
# att laddas i en iframe (clickjacking-skydd).
# ─────────────────────────────────────────────

class TestSecurityHeaders:
    """Tester för säkerhetsrelaterade HTTP-headers."""

    REQUIRED_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options":        "DENY",
        "X-XSS-Protection":       "1; mode=block",
    }

    def test_security_headers_present(self):
        """
        Verifiera att säkerhetsheaders finns och har rätt värde.

        X-Content-Type-Options: nosniff
            → Förhindrar webbläsaren från att gissa innehållstyp (MIME sniffing).

        X-Frame-Options: DENY
            → Förhindrar att sidan laddas i en iframe (clickjacking-skydd).

        X-XSS-Protection: 1; mode=block
            → Aktiverar webbläsarens inbyggda XSS-filter.

        OBS: I ett riktigt test anropar vi en riktig server med requests.get()
        och kontrollerar svar.headers istället för mock_headers nedan.
        """
        # Simulerat svar — ersätt med: svar = requests.get(URL); svar.headers
        mock_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options":        "DENY",
            "X-XSS-Protection":       "1; mode=block",
        }

        for header, expected_value in self.REQUIRED_HEADERS.items():
            assert header in mock_headers, (
                f"Saknad säkerhetsheader: '{header}'"
            )
            assert mock_headers[header] == expected_value, (
                f"Header '{header}' har fel värde: "
                f"förväntade '{expected_value}', fick '{mock_headers[header]}'"
            )
