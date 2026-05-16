"""
conftest.py – Delade pytest-fixtures för Labb 8.2
Lektion 8: Sammanfattning Del 1

Fixtures här är tillgängliga för ALLA tester i labb82_pom/
och dess undermappar — utan import.

Fixtures:
  driver     – Chrome WebDriver-instans (scope=function)
  login_page – LoginPage kopplad till driver (scope=function)

scope=function innebär att varje TEST får en fräsch webbläsarinstans.
Det förhindrar att ett tests state påverkar nästa test.

Varför yield istället för return?
  yield pausar fixturen under testet och fortsätter (teardown) när
  testet är klart. driver.quit() körs ALLTID — även om testet failar.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def driver():
    """
    Skapar och stänger en Chrome-webbläsarinstans per test.

    headless=True gör att webbläsaren körs utan synligt fönster —
    nödvändigt i CI/CD-miljöer (GitHub Actions, Jenkins) som saknar
    bildskärm.

    Yields:
        WebDriver — Chrome-instansen
    """
    options = Options()
    options.add_argument("--headless")          # Osynlig webbläsare (CI-vänlig)
    options.add_argument("--no-sandbox")        # Krävs i Docker/GitHub Actions
    options.add_argument("--disable-dev-shm-usage")  # Förhindrar minnesproblem i CI

    chrome_driver = webdriver.Chrome(options=options)
    chrome_driver.implicitly_wait(0)  # ALDRIG implicit wait — vi använder explicit wait

    yield chrome_driver  # Testet körs här

    chrome_driver.quit()  # Teardown: stängs alltid, även vid test-failure


@pytest.fixture(scope="function")
def login_page(driver):
    """
    Ger ett konfigurerat LoginPage-objekt med öppen webbläsare.

    Navigerar automatiskt till login-sidan före testet.

    Yields:
        LoginPage — redo att använda

    Exempel i test:
        def test_login(login_page):
            login_page.login("admin", "secret123")
            assert "Dashboard" in login_page.driver.title
    """
    page = LoginPage(driver)
    page.navigate_to(LoginPage.URL)
    yield page
    # Ingen specifik teardown — driver-fixturen stänger webbläsaren
