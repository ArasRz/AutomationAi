from playwright.sync_api import Page


def test_page_title(page: Page):
    """Kontrollera att sidans titel är korrekt"""
    page.goto("https://the-internet.herokuapp.com/login")
    page.screenshot(path="screenshot_title.png")
    assert "The Internet" in page.title()


def test_username_field_exists(page: Page):
    """Kontrollera att användarnamn-fältet finns och syns"""
    page.goto("https://the-internet.herokuapp.com/login")
    page.screenshot(path="screenshot_username_field.png")
    assert page.locator("#username").is_visible()


def test_lyckad_inloggning(page: Page):
    """Logga in med rätt autentiseringsuppgifter"""
    page.goto("https://the-internet.herokuapp.com/login")
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")

    page.screenshot(path="screenshot_lyckad_inloggning.png")
    assert "/secure" in page.url
    assert page.locator("#flash").is_visible()
    assert "You logged into a secure area!" in page.locator("#flash").text_content()


def test_misslyckad_inloggning(page: Page):
    """Verifiera felmeddelande vid fel lösenord"""
    page.goto("https://the-internet.herokuapp.com/login")
    page.fill("#username", "tomsmith")
    page.fill("#password", "FelLösenord!")
    page.click("button[type='submit']")

    page.screenshot(path="screenshot_misslyckad_inloggning.png")
    assert page.locator("#flash").is_visible()
    assert "Your password is invalid!" in page.locator("#flash").text_content()
