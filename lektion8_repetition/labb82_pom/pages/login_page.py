"""
login_page.py – LoginPage enligt Page Object Model
Labb 8.2: Page Object Model refaktorering
Lektion 8: Sammanfattning Del 1

Refaktorering av startkoden som:
  - Hade duplicerad logik i Test 1 och Test 2
  - Använde time.sleep() (anti-pattern)
  - Hade inga fixtures eller POM-struktur

Lösning:
  - LoginPage klass med lokalisatorer som klassattribut
  - Metoder för varje interaktion (SRP — Single Responsibility Principle)
  - Ärver BasePage → explicit wait utan duplicering

Taxi Stockholm-koppling: om login-knappens ID ändras från "login-btn"
till "signin-btn" ändrar vi BARA LoginPage.LOGIN_BUTTON — inte i 30 testfiler.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object för https://example.com/login.

    Lokalisatorer som klassattribut (By-tupler):
      - Ändra på ETT ställe om DOM ändras
      - Enkelt att läsa — ser ut som ett kontrakt

    Användning i test:
        login_page = LoginPage(driver)
        login_page.navigate_to("https://example.com/login")
        login_page.login("admin", "secret123")
        assert "Dashboard" in driver.title
    """

    # ── Lokalisatorer (By-tupler) ──────────────────────────────────────────
    USERNAME_FIELD  = (By.ID, "username")
    PASSWORD_FIELD  = (By.ID, "password")
    LOGIN_BUTTON    = (By.CSS_SELECTOR, "button.login-btn")
    ERROR_MESSAGE   = (By.CLASS_NAME, "error-msg")

    URL = "https://example.com/login"

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Individuella interaktionsmetoder ───────────────────────────────────

    def enter_username(self, username: str) -> None:
        """Fyller i användarnamnsfältet."""
        field = self.find_element(*self.USERNAME_FIELD)
        field.clear()
        field.send_keys(username)

    def enter_password(self, password: str) -> None:
        """Fyller i lösenordsfältet."""
        field = self.find_element(*self.PASSWORD_FIELD)
        field.clear()
        field.send_keys(password)

    def click_login(self) -> None:
        """Klickar på inloggningsknappen (väntar tills den är klickbar)."""
        self.find_clickable(*self.LOGIN_BUTTON).click()

    def get_error_message(self) -> str:
        """
        Returnerar felmeddelandet som visas vid misslyckad inloggning.

        Väntar tills felmeddelandet är synligt — annars risk för
        ElementNotFoundException om sidan inte hunnit uppdatera sig.
        """
        return self.find_element(*self.ERROR_MESSAGE).text

    # ── Hjälpmetod: kombinerar individuella steg ──────────────────────────

    def login(self, username: str, password: str) -> None:
        """
        Utför hela inloggningsflödet: fyll i fält och klicka.

        Används när testet inte behöver verifiera individuella steg,
        t.ex. som setup-steg före ett annat test.

        Exempel:
            login_page.login("admin", "secret123")
            # Förväntar sig att webbläsaren navigerat till dashboard
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
