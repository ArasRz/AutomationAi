import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ─────────────────────────────────────────────
# FIXTURE: Startar och stänger webbläsaren
# autouse=False → körs bara när "browser" används som parameter
# ─────────────────────────────────────────────
@pytest.fixture
def browser():
    options = Options()
    if os.environ.get("CI"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://automationexercise.com/products")

    yield driver  # Testet körs här

    driver.quit()  # Körs alltid efter testet, även vid fel


# ─────────────────────────────────────────────
# PARAMETRIZE: En testfunktion — många inputs
# Varje rad i listan = ett separat testfall
# Format: (sökterm, minsta antal förväntade resultat)
# ─────────────────────────────────────────────
@pytest.mark.parametrize("sokterm, min_resultat", [
    ("top",      1),
    ("dress",    1),
    ("jeans",    1),
    ("tshirt",   1),
    ("saree",    1),
])
def test_sok(browser, sokterm, min_resultat):
    """
    Testar att sökning returnerar minst 'min_resultat' produkter.
    Körs automatiskt en gång per rad i parametrize-listan ovan.
    """
    wait = WebDriverWait(browser, 10)

    # Vänta tills sökrutan finns i DOM:en
    sokruta = wait.until(EC.presence_of_element_located((By.ID, "search_product")))
    sokknapp = browser.find_element(By.ID, "submit_search")

    # Använd JavaScript för att skriva och klicka — kringgår consent-popup som blockerar sidan
    browser.execute_script("arguments[0].value = arguments[1];", sokruta, sokterm)
    browser.execute_script("arguments[0].click();", sokknapp)

    # Vänta på att sökresultaten laddas
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "productinfo")))

    # Räkna antal produktkort på sidan
    produkter = browser.find_elements(By.CLASS_NAME, "productinfo")
    antal = len(produkter)

    assert antal >= min_resultat, (
        f"Sökning på '{sokterm}' returnerade {antal} resultat "
        f"— förväntade minst {min_resultat}"
    )
