"""
base_page.py – BasePage med gemensam funktionalitet
Labb 8.2: Page Object Model refaktorering
Lektion 8: Sammanfattning Del 1

VG-bonusuppgift: Alla Page Object-klasser ärver från BasePage.
Det ger ett enda ställe för:
  - WebDriverWait-skapande (ingen duplicering)
  - wait_for_element()-metod (DRY-principen)
  - navigate_to()-metod

Taxi Stockholm-koppling: om LoginPage, BookingPage och MapPage
alla ärver BasePage, räcker det att ändra standardtimeout på ETT ställe.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BasePage:
    """
    Basklass för alla Page Objects.

    Tillhandahåller:
      driver     – Webbläsarinstansen
      wait       – WebDriverWait med konfigurerad standardtimeout
      navigate_to()  – Navigera till URL
      find_element() – Väntar tills elementet är synligt och returnerar det
    """

    DEFAULT_TIMEOUT = 10  # sekunder

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        # WebDriverWait skapas EN gång och återanvänds av alla metoder.
        # Utan BasePage måste varje sidklass skapa sin egen wait — duplicering.
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

    def navigate_to(self, url: str) -> None:
        """
        Navigera till angiven URL.

        Exempel:
            login_page.navigate_to("https://example.com/login")
        """
        self.driver.get(url)

    def find_element(self, by: str, value: str) -> WebElement:
        """
        Väntar tills elementet är synligt och returnerar det.

        Ersätter:
            driver.find_element(By.ID, "username")  ← Ingen wait → instabilt
        Med:
            self.find_element(By.ID, "username")    ← Explicit wait → stabilt

        Args:
            by:    Lokalisatortyp, t.ex. By.ID, By.CSS_SELECTOR
            value: Lokalisatorvärde, t.ex. "username"

        Returns:
            WebElement — elementet när det är synligt

        Raises:
            AssertionError om elementet inte dyker upp inom DEFAULT_TIMEOUT
        """
        return self.wait.until(
            EC.visibility_of_element_located((by, value)),
            message=f"Element '{value}' (by={by}) syntes inte inom {self.DEFAULT_TIMEOUT}s"
        )

    def find_clickable(self, by: str, value: str) -> WebElement:
        """
        Väntar tills elementet är klickbart (synligt + aktiverat).

        Används för knappar och länkar — ett element kan vara synligt men
        grått/inaktivt, vilket ger ElementNotInteractableException.
        """
        return self.wait.until(
            EC.element_to_be_clickable((by, value)),
            message=f"Element '{value}' (by={by}) var inte klickbart inom {self.DEFAULT_TIMEOUT}s"
        )
