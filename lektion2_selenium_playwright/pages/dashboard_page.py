from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class DashboardPage(BasePage):
    # Lokalisatorer
    LOGOUT_BUTTON   = (By.CSS_SELECTOR, "a[href='/logout']")
    FLASH_MESSAGE   = (By.ID, "flash")
    SECURE_HEADING  = (By.TAG_NAME, "h2")

    def logout(self):
        """Klicka på logout-knappen och vänta tills sidan navigerat till /login"""
        self.click(self.LOGOUT_BUTTON)
        self.wait.until(EC.url_contains("/login"))

    def get_flash_message(self):
        """Hämta meddelandet efter logout"""
        return self.get_text(self.FLASH_MESSAGE)

    def get_heading(self):
        """Hämta rubriken på dashboard-sidan"""
        return self.get_text(self.SECURE_HEADING)
