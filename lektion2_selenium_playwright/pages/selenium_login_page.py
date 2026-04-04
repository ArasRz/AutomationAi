from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LoginPage(BasePage):
    # Lokalisatorer
    USERNAME_INPUT  = (By.ID, "username")
    PASSWORD_INPUT  = (By.ID, "password")
    LOGIN_BUTTON    = (By.CSS_SELECTOR, "button[type='submit']")
    FLASH_MESSAGE   = (By.ID, "flash")

    URL = "https://the-internet.herokuapp.com/login"

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(self.URL)

    def login(self, username, password):
        """Logga in med användarnamn och lösenord"""
        self.send_keys(self.USERNAME_INPUT, username)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_flash_message(self):
        """Hämta framgångs- eller felmeddelande"""
        return self.get_text(self.FLASH_MESSAGE)

    def is_username_field_visible(self):
        """Kontrollera att användarnamn-fältet syns"""
        return self.is_displayed(self.USERNAME_INPUT)
