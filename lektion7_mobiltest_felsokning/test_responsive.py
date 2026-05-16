"""
Övning 1 – Responsiv Testning och Mobilsimulering med Playwright
Lektion 7: Mobiltest, Felsökning & Testobservabilitet

Testar en e-handelswebbshop på fyra standardviewport-storlekar:
  - iPhone SE      (375×667)   → is_mobile = True
  - iPhone 15 Pro  (430×932)   → is_mobile = True
  - iPad           (768×1024)  → is_mobile = False
  - Desktop        (1920×1080) → is_mobile = False

TechRetail AB-koppling: 68% av trafiken kommer från mobila enheter.
Taxi Stockholm-koppling: boknings-appen måste fungera felfritt på alla
vanliga mobilskärmar — en knapp som inte går att trycka på är en
förlorad bokning.

Kör: pytest test_responsive.py -v
     pytest test_responsive.py -v -k "iPhone_SE"   # bara mobilvy
     pytest test_responsive.py -v -k "Desktop"     # bara desktopvy
"""

import pytest
from playwright.sync_api import sync_playwright

# ─── Konfiguration ─────────────────────────────────────────────────────────
# books.toscrape.com är en öppen test-e-handelssajt avsedd för övning.
# Byt till din applikations URL när du anpassar testerna till ditt projekt.
BASE_URL = "https://books.toscrape.com"

# Fyra standardvieports som täcker de vanligaste enhetsklasserna
VIEWPORTS = [
    {"name": "iPhone_SE",     "width": 375,  "height": 667},
    {"name": "iPhone_15_Pro", "width": 430,  "height": 932},
    {"name": "iPad",          "width": 768,  "height": 1024},
    {"name": "Desktop",       "width": 1920, "height": 1080},
]


@pytest.fixture(params=VIEWPORTS, ids=[v["name"] for v in VIEWPORTS])
def page(request):
    """
    Skapar en Playwright-page med specifik viewport-storlek.

    Returnerar: tuple(page, viewport_dict)

    Designbeslut:
      - is_mobile=True aktiverar touch-events och ändrar hover-beteende
      - user_agent för mobil triggar eventuell server-side rendering
      - headless=True kör utan synligt fönster (snabbare i CI/CD)
      - context.close() + browser.close() frigör resurser korrekt
    """
    viewport = request.param
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": viewport["width"], "height": viewport["height"]},
            is_mobile=viewport["width"] < 768,
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile Safari/604.1"
                if viewport["width"] < 768 else None
            ),
        )
        pg = context.new_page()
        yield pg, viewport
        context.close()
        browser.close()


def test_navigation_responsive(page):
    """
    Verifierar att navigationsmenyn anpassar sig till viewportens storlek.

    TechRetail AB-mönster:
      - Mobil (<768px): hamburger-ikon [data-testid="mobile-menu"] synlig,
        desktop-nav [data-testid="desktop-nav"] dold
      - Desktop (>=768px): desktop-nav synlig, hamburger dold

    books.toscrape.com har ingen hamburger-meny — testet visar det
    generella mönstret och verifierar att sidan faktiskt laddar
    navigeringslänkar på alla viewports.

    ANPASSA: Ersätt selektorerna nedan med din apps verkliga element.
    """
    pg, viewport = page
    pg.goto(BASE_URL)
    pg.wait_for_load_state("networkidle")

    is_mobile = viewport["width"] < 768

    # ── TechRetail AB-mönster (anpassa selektorer till din app) ──────────
    # if is_mobile:
    #     assert pg.locator('[data-testid="mobile-menu"]').is_visible(), \
    #         f"Hamburger-ikon ska synas på mobil ({viewport['name']})"
    #     assert not pg.locator('[data-testid="desktop-nav"]').is_visible(), \
    #         "Desktop-nav ska vara dold på mobil"
    # else:
    #     assert pg.locator('[data-testid="desktop-nav"]').is_visible(), \
    #         f"Desktop-nav ska synas på {viewport['name']}"
    # ─────────────────────────────────────────────────────────────────────

    # Generisk kontroll: sidan ska ha navigeringslänkar på alla viewports
    nav_links = pg.locator("nav a, ul.nav a, header a, .side_categories a")
    link_count = nav_links.count()

    assert link_count > 0, (
        f"Inga navigeringslänkar hittades på {viewport['name']} "
        f"({viewport['width']}px). Kontrollera att sidan laddades korrekt."
    )

    # Bekräfta att viewport-bredden stämmer
    actual_width = pg.viewport_size["width"]
    assert actual_width == viewport["width"], (
        f"Fel viewport-bredd: {actual_width}px (förväntat {viewport['width']}px)"
    )


def test_product_card_layout(page):
    """
    Verifierar att produktkorten anpassar sin layout till viewport-bredden.

    Regler:
      - Mobil (<768px): kort tar minst 70% av viewport (smalt → enkolumn)
      - Desktop (>=768px): kort är smalare än 80% av viewport (grid-layout)

    books.toscrape.com: article.product_pod
    TechRetail AB:     [data-testid="product-card"]

    Taxi Stockholm-koppling: om taxiboks-listan på mobilsidan inte
    fyller skärmbredden uppstår onödigt tomrum och dålig UX.
    """
    pg, viewport = page
    pg.goto(BASE_URL)
    pg.wait_for_load_state("networkidle")

    is_mobile = viewport["width"] < 768

    # Hitta första produktkortet
    card = pg.locator("article.product_pod").first

    if card.count() == 0:
        pytest.skip(
            "Inga produktkort hittades — anpassa selektorn till din app "
            "(TechRetail AB: [data-testid='product-card'])"
        )

    box = card.bounding_box()
    assert box is not None, (
        f"Produktkortet ska vara synligt och mätbart på {viewport['name']}"
    )

    if is_mobile:
        min_width = viewport["width"] * 0.70
        assert box["width"] >= min_width, (
            f"Produktkort för smalt på {viewport['name']}: "
            f"{box['width']:.0f}px (förväntat ≥{min_width:.0f}px = 70% av viewport)"
        )
    else:
        # I grid-layout ska korten inte spänna hela viewport-bredden
        max_width = viewport["width"] * 0.80
        assert box["width"] < max_width, (
            f"Produktkort för brett på {viewport['name']}: "
            f"{box['width']:.0f}px (förväntat <{max_width:.0f}px för grid-layout)"
        )


def test_touch_targets_mobile(page):
    """
    Verifierar att interaktiva element uppfyller WCAG 2.5.5 (minst 44×44px).

    WCAG 2.5.5 Target Size: klickbara element ska vara stora nog för
    tryck med fingret — annars missar användaren och klickar fel.

    Testet körs BARA för mobila viewports (<768px).

    OBS: Många äldre siter misslyckas här — det är poängen!
    Testet visar var tillgänglighetsförbättringar behövs.

    Notera: vi samlar ALLA violations innan assertion (soft assertion-mönster).
    Det ger ett komplett felmeddelande som visar alla problem, inte bara det första.
    """
    pg, viewport = page

    if viewport["width"] >= 768:
        pytest.skip("Touch target-test är bara relevant för mobila viewports (<768px)")

    pg.goto(BASE_URL)
    pg.wait_for_load_state("networkidle")

    # Hitta interaktiva element
    interactive = pg.locator("button, a[href], input[type=submit], [role=button]")
    count = interactive.count()

    if count == 0:
        pytest.skip("Inga interaktiva element hittades på sidan")

    violations = []
    checked = 0

    for i in range(count):
        if checked >= 10:
            break  # Kontrollera max 10 element

        element = interactive.nth(i)
        if not element.is_visible():
            continue

        box = element.bounding_box()
        if box and (box["height"] < 44 or box["width"] < 44):
            text = (element.text_content() or f"element #{i}").strip()[:40]
            violations.append(
                f"  '{text}': {box['width']:.0f}×{box['height']:.0f}px"
            )
        checked += 1

    assert len(violations) == 0, (
        f"WCAG 2.5.5-brott på {viewport['name']} ({viewport['width']}px): "
        f"{len(violations)} element <44×44px:\n"
        + "\n".join(violations)
        + "\n  Lösning: Öka padding/min-height/min-width i CSS för dessa element."
    )


def test_checkout_responsive(page):
    """
    Verifierar att formulärfält är användbara på alla viewports.

    Regler:
      - Input-fält ≥200px breda på mobil (kreditkortsnummer kräver plats)
      - Submit-knapp ska synas utan att användaren scrollar

    books.toscrape.com har ett sökfält (input[name="q"]) som kan testas.
    TechRetail AB: byt FORM_URL till din checkout-sida och anpassa selektorer.
    """
    pg, viewport = page
    is_mobile = viewport["width"] < 768

    # Anpassa FORM_URL till din checkout-sida för verkliga projekt
    FORM_URL = BASE_URL  # books.toscrape.com har ett sökfält som demonstration
    INPUT_SELECTOR = "input[type='text'], input[type='search'], input[name='q']"
    SUBMIT_SELECTOR = "button[type='submit'], input[type='submit'], button.btn"

    pg.goto(FORM_URL)
    pg.wait_for_load_state("networkidle")

    # Verifiera att ett formulärfält finns och har tillräcklig bredd
    inputs = pg.locator(INPUT_SELECTOR)
    if inputs.count() == 0:
        pytest.skip(
            "Inget formulärfält hittades — anpassa FORM_URL och INPUT_SELECTOR "
            "till din applikations checkout-sida"
        )

    first_input = inputs.first
    if not first_input.is_visible():
        pytest.skip("Formulärfält är inte synligt på sidan")

    box = first_input.bounding_box()
    if box and is_mobile:
        assert box["width"] >= 200, (
            f"Input-fält för smalt på {viewport['name']}: "
            f"{box['width']:.0f}px (förväntat ≥200px för touch-användbarhet)"
        )

    # Verifiera att submit-knapp syns inom viewport utan scroll
    submit = pg.locator(SUBMIT_SELECTOR).first
    if submit.is_visible():
        submit_box = submit.bounding_box()
        if submit_box:
            assert submit_box["y"] + submit_box["height"] <= viewport["height"], (
                f"Submit-knapp hamnar utanför viewport på {viewport['name']}: "
                f"y={submit_box['y']:.0f}px + h={submit_box['height']:.0f}px "
                f"> viewport höjd={viewport['height']}px"
            )
