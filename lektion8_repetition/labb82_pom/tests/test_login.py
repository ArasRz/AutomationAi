"""
test_login.py – Refaktorerade login-tester med POM och AAA
Labb 8.2: Page Object Model refaktorering
Lektion 8: Sammanfattning Del 1

FÖRE (startkod — problemet):
  - Duplicerad kod i varje test (driver setup, navigation, lokalisatorer)
  - time.sleep(3) och time.sleep(5) — anti-patterns
  - Inga fixtures — manuell driver.quit() i varje test
  - Spaghetti-kod utan struktur

EFTER (denna fil):
  - LoginPage-klass hanterar ALL lokalisatorlogik
  - conftest.py-fixtures hanterar setup/teardown
  - AAA-mönstret gör varje test lättläst och fokuserat
  - Explicit wait inbyggt i BasePage (inga sleep)

Kör: pytest lektion8_repetition/labb82_pom/ -v
"""

import pytest
from pages.login_page import LoginPage


class TestLogin:
    """
    Testklass för LoginPage.

    Klassen grupperar relaterade tester — pytest kör alla test_*-metoder.
    """

    def test_successful_login_redirects_to_dashboard(self, login_page: LoginPage) -> None:
        """
        Verifierar att korrekt login navigerar till Dashboard.

        Täcker: happy path / positiv testning
        Kopplar till: WCAG (tillgänglighet kräver att inloggning fungerar)
        """
        # Arrange — login_page-fixturen navigerade redan till login-URL

        # Act
        login_page.login("admin", "secret123")

        # Assert
        assert "Dashboard" in login_page.driver.title, (
            f"Förväntade 'Dashboard' i sidtiteln, fick: '{login_page.driver.title}'"
        )

    def test_invalid_password_shows_error_message(self, login_page: LoginPage) -> None:
        """
        Verifierar att felaktigt lösenord visar rätt felmeddelande.

        Täcker: negativ testning / felhantering
        WCAG 3.3.1 kräver att felmeddelanden är tydliga och informativa.
        """
        # Arrange
        fel_lösenord = "wrongpass"

        # Act
        login_page.login("admin", fel_lösenord)

        # Assert
        error_text = login_page.get_error_message()
        assert error_text == "Invalid credentials", (
            f"Förväntade 'Invalid credentials', fick: '{error_text}'"
        )

    def test_empty_username_shows_error(self, login_page: LoginPage) -> None:
        """
        Verifierar att tomt användarnamn hindrar inloggning.

        Gränsvärdesfall: tomt fält = ogiltigt input.
        """
        # Arrange — tomt användarnamn

        # Act
        login_page.enter_username("")
        login_page.enter_password("secret123")
        login_page.click_login()

        # Assert
        error_text = login_page.get_error_message()
        assert error_text != "", "Inget felmeddelande visades för tomt användarnamn"

    def test_empty_password_shows_error(self, login_page: LoginPage) -> None:
        """
        Verifierar att tomt lösenord hindrar inloggning.

        Symmetrisk test med test_empty_username — båda fält är obligatoriska.
        """
        # Arrange

        # Act
        login_page.enter_username("admin")
        login_page.enter_password("")
        login_page.click_login()

        # Assert
        error_text = login_page.get_error_message()
        assert error_text != "", "Inget felmeddelande visades för tomt lösenord"

    @pytest.mark.parametrize("username,password", [
        ("admin",        "secret123"),  # Korrekt
        ("superuser",    "adminpass"),  # Annat giltigt konto
    ])
    def test_valid_credentials_reach_dashboard(
        self,
        login_page: LoginPage,
        username: str,
        password: str,
    ) -> None:
        """
        Verifierar att FLERA giltiga konton kan logga in.

        Kombinerar POM med parametrize — datadriven E2E-testning.
        Utan parametrize skulle vi behöva N identiska testfunktioner.
        """
        # Arrange — parametrize ger olika username/password per körning

        # Act
        login_page.login(username, password)

        # Assert
        assert "Dashboard" in login_page.driver.title


# ── Kommentar: Refaktorering-jämförelse ──────────────────────────────────────
#
# STARTKOD (problemet):
#   driver = webdriver.Chrome()
#   driver.get("https://example.com/login")
#   time.sleep(3)                                # ← Anti-pattern
#   driver.find_element(By.ID, "username").send_keys("admin")
#   driver.find_element(By.ID, "password").send_keys("secret123")
#   driver.find_element(By.CSS_SELECTOR, "button.login-btn").click()
#   time.sleep(5)                                # ← Anti-pattern
#   assert "Dashboard" in driver.title
#   driver.quit()                                # ← Körs inte vid failure!
#
# REFAKTORERAD KOD (denna fil):
#   def test_successful_login_redirects_to_dashboard(self, login_page):
#       login_page.login("admin", "secret123")   # ← Explicit wait inbyggt
#       assert "Dashboard" in login_page.driver.title
#
# Vinster:
#   ✓ 3 rader istället för 9
#   ✓ Inga time.sleep()
#   ✓ driver.quit() garanterat (fixture teardown)
#   ✓ Lokalisatorer på ett ställe (LoginPage)
#   ✓ AAA-struktur tydlig
