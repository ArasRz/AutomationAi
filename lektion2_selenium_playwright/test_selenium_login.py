import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestLogin:

    @pytest.fixture(autouse=True)
    def setup(self):
        options = Options()
        if os.environ.get("CI"):
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get("https://the-internet.herokuapp.com/login")
        self.wait = WebDriverWait(self.driver, 10)
        yield
        self.driver.quit()

    def test_page_title(self):
        """Kontrollera att sidans titel är korrekt"""
        assert "The Internet" in self.driver.title

    def test_username_field_exists(self):
        """Kontrollera att användarnamn-fältet finns"""
        username_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        assert username_field.is_displayed()

    def test_successful_login(self):
        """Logga in med rätt autentiseringsuppgifter"""
        self.driver.find_element(By.ID, "username").send_keys("tomsmith")
        self.driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        flash = self.wait.until(EC.visibility_of_element_located((By.ID, "flash")))
        assert "You logged into a secure area!" in flash.text

    def test_failed_login_invalid_password(self):
        """Verifiera felmeddelande vid fel lösenord"""
        self.driver.find_element(By.ID, "username").send_keys("tomsmith")
        self.driver.find_element(By.ID, "password").send_keys("FelLösenord!")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        flash = self.wait.until(EC.visibility_of_element_located((By.ID, "flash")))
        assert "Your password is invalid!" in flash.text
