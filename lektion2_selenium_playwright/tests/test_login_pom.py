import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pages.selenium_login_page import LoginPage
from pages.dashboard_page import DashboardPage


def test_page_title(driver):
    """Kontrollera att sidans titel är korrekt"""
    LoginPage(driver)
    assert "The Internet" in driver.title


def test_username_field_exists(driver):
    """Kontrollera att användarnamn-fältet finns och syns"""
    login_page = LoginPage(driver)
    assert login_page.is_username_field_visible()


def test_successful_login(driver):
    """Logga in med rätt autentiseringsuppgifter"""
    login_page = LoginPage(driver)
    login_page.login("tomsmith", "SuperSecretPassword!")
    assert "You logged into a secure area!" in login_page.get_flash_message()


def test_failed_login_invalid_password(driver):
    """Verifiera felmeddelande vid fel lösenord"""
    login_page = LoginPage(driver)
    login_page.login("tomsmith", "FelLösenord!")
    assert "Your password is invalid!" in login_page.get_flash_message()


def test_logout(driver):
    """Logga in och verifiera att logout fungerar"""
    login_page = LoginPage(driver)
    login_page.login("tomsmith", "SuperSecretPassword!")

    dashboard = DashboardPage(driver)
    dashboard.logout()

    assert "/login" in driver.current_url
    assert "You logged out of the secure area!" in dashboard.get_flash_message()
