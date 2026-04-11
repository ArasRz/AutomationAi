# Enhetstester testar enskilda funktioner och klasser isolerat
# Ingen webbläsare behövs — de körs snabbt och på alla pull requests

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lektion2_selenium_playwright"))

from lektion2_selenium_playwright.pages.selenium_login_page import LoginPage
from lektion2_selenium_playwright.pages.dashboard_page import DashboardPage


def test_login_page_url():
    """Verifiera att login-sidans URL är korrekt definierad"""
    assert LoginPage.URL == "https://the-internet.herokuapp.com/login"


def test_login_page_has_username_locator():
    """Verifiera att username-lokalisatorn är definierad"""
    assert LoginPage.USERNAME_INPUT is not None


def test_login_page_has_password_locator():
    """Verifiera att password-lokalisatorn är definierad"""
    assert LoginPage.PASSWORD_INPUT is not None


def test_login_page_has_login_button_locator():
    """Verifiera att login-knappens lokalisator är definierad"""
    assert LoginPage.LOGIN_BUTTON is not None


def test_dashboard_page_has_logout_locator():
    """Verifiera att logout-knappens lokalisator är definierad"""
    assert DashboardPage.LOGOUT_BUTTON is not None
