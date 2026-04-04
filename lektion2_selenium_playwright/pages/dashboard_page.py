from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class DashboardPage(BasePage):
    # Lokalisatorer
    LOGOUT_BUTTON   = (By.CSS_SELECTOR, "a[href='/logout']")
    FLASH_MESSAGE   = (By.ID, "flash")
    SECURE_HEADING  = (By.TAG_NAME, "h2")

    def logout(self):
        """Klicka på logout-knappen"""
        self.click(self.LOGOUT_BUTTON)

    def get_flash_message(self):
        """Hämta meddelandet efter logout"""
        return self.get_text(self.FLASH_MESSAGE)

    def get_heading(self):
        """Hämta rubriken på dashboard-sidan"""
        return self.get_text(self.SECURE_HEADING)
