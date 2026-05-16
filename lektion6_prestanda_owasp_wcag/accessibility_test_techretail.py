"""
Övning 3 – Tillgänglighetstestning med axe-core + Playwright (simulerad)
Lektion 6: Prestanda, Säkerhet & Tillgänglighetstest

OBS: I ett riktigt projekt körs axe-core inuti en Playwright-webbläsare.
Här simulerar vi axe-resultaten så att du kan köra testerna utan webbläsare.

Kör: pytest accessibility_test_techretail.py -v

Kör mot en riktig URL (kräver Playwright installerat):
  playwright install chromium
  pytest accessibility_test_techretail.py -v --real

WCAG 2.1 POUR-principerna:
  P – Perceivable   (Möjlig att uppfatta)
  O – Operable      (Möjlig att använda)
  U – Understandable (Begriplig)
  R – Robust        (Robust)
"""

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# POUR-KLASSIFICERING
# Mappar axe-core rule-IDs till WCAG POUR-principerna
# ─────────────────────────────────────────────────────────────────────────────

POUR_CLASSIFICATION = {
    # Perceivable — innehåll måste gå att uppfatta med minst ett sinne
    "image-alt":         "Perceivable",   # Bilder saknar alt-text
    "color-contrast":    "Perceivable",   # Otillräcklig färgkontrast
    "video-caption":     "Perceivable",   # Video saknar textning
    "audio-caption":     "Perceivable",   # Audio saknar textning

    # Operable — gränssnitt måste gå att använda
    "keyboard":          "Operable",      # Inte tillgängligt via tangentbord
    "focus-visible":     "Operable",      # Fokus-indikator saknas
    "bypass":            "Operable",      # Ingen "hoppa till innehåll"-länk
    "link-name":         "Operable",      # Länk saknar beskrivande text

    # Understandable — information och gränssnitt måste vara begripliga
    "label":             "Understandable", # Formulärfält saknar label
    "html-lang-valid":   "Understandable", # HTML lang-attribut saknas/ogiltigt
    "error-suggestion":  "Understandable", # Felmeddelanden saknar hjälptext

    # Robust — innehåll måste vara robust nog för hjälpmedel
    "aria-required-attr": "Robust",       # ARIA-attribut saknas
    "duplicate-id":       "Robust",       # Duplicerade ID:n
    "valid-lang":         "Robust",       # Ogiltigt language-attribut
}


def classify_violation(rule_id: str) -> str:
    """
    Returnerar POUR-kategorin för ett givet axe rule-ID.
    Okänd regel → 'Unknown'.
    """
    return POUR_CLASSIFICATION.get(rule_id, "Unknown")


# ─────────────────────────────────────────────────────────────────────────────
# AXE-SCANNER
# I ett riktigt projekt: injicerar axe-core.js i Playwright och kör analyze()
# ─────────────────────────────────────────────────────────────────────────────

class AxeScanner:
    """
    Kapslar in axe-core-skanningen och POUR-klassificeringen.

    Taxi Stockholm-koppling: skannar bokningsformuläret och kontrollerar
    att det uppfyller WCAG 2.1 AA — ett krav från Diskrimineringslagen
    och EU:s tillgänglighetsdirektiv.
    """

    def __init__(self, target_url: str):
        self.target_url = target_url

    def scan_page(self, path: str = "/") -> dict:
        """
        Skannar en sida med axe-core och returnerar resultatet.

        I produktion:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(self.target_url + path)
                axe_script = open("axe.min.js").read()
                page.evaluate(axe_script)
                results = page.evaluate("axe.run()")
                browser.close()
                return results
        """
        # Simulerade axe-core-resultat för TechRetail AB:s startsida
        return {
            "url":      self.target_url + path,
            "passes":   self._get_simulated_passes(),
            "violations": self._get_simulated_violations(),
            "incomplete": [],
            "inapplicable": [],
        }

    def _get_simulated_passes(self) -> list[dict]:
        """Simulerade regler som KLARAR axe-genomgången."""
        return [
            {"id": "html-lang-valid",    "description": "HTML har giltigt lang-attribut"},
            {"id": "aria-required-attr", "description": "Alla ARIA-attribut är korrekt ifyllda"},
            {"id": "duplicate-id",       "description": "Inga duplicerade ID:n"},
        ]

    def _get_simulated_violations(self) -> list[dict]:
        """
        Simulerade överträdelser — dessa är vanliga verkliga fynd på e-handelssajter.
        Varje violation kan påverka ett eller flera HTML-element (nodes).
        """
        return [
            {
                "id":          "image-alt",
                "impact":      "critical",
                "description": "Bilder måste ha alt-text",
                "help":        "Lägg till alt-attribut på alla <img>-element",
                "helpUrl":     "https://dequeuniversity.com/rules/axe/4.4/image-alt",
                "nodes": [
                    {"html": '<img src="/products/laptop.jpg">',
                     "failureSummary": "Fix any of the following: Element does not have an alt attribute"},
                    {"html": '<img src="/banner.png">',
                     "failureSummary": "Fix any of the following: Element does not have an alt attribute"},
                ],
            },
            {
                "id":          "color-contrast",
                "impact":      "serious",
                "description": "Textens kontrast mot bakgrunden är otillräcklig",
                "help":        "Säkerställ kontrastförhållande ≥ 4.5:1 (WCAG AA)",
                "helpUrl":     "https://dequeuniversity.com/rules/axe/4.4/color-contrast",
                "nodes": [
                    {"html": '<p class="price-label" style="color:#aaa">299 kr</p>',
                     "failureSummary": "Expected contrast ratio of 4.5:1, got 2.1:1"},
                ],
            },
            {
                "id":          "label",
                "impact":      "critical",
                "description": "Formulärfält saknar associerad label",
                "help":        "Lägg till <label for='...'> eller aria-label",
                "helpUrl":     "https://dequeuniversity.com/rules/axe/4.4/label",
                "nodes": [
                    {"html": '<input type="email" placeholder="Din e-post">',
                     "failureSummary": "Fix any of the following: Form element does not have an implicit (wrapped) <label>"},
                ],
            },
            {
                "id":          "link-name",
                "impact":      "serious",
                "description": "Länkar måste ha ett tillgängligt namn",
                "help":        "Lägg till synlig text, aria-label eller title på alla <a>-element",
                "helpUrl":     "https://dequeuniversity.com/rules/axe/4.4/link-name",
                "nodes": [
                    {"html": '<a href="/cart"><img src="cart-icon.svg"></a>',
                     "failureSummary": "Fix all of the following: Element is in tab order and does not have accessible text"},
                ],
            },
        ]

    def get_violations_by_pour(self, violations: list[dict]) -> dict[str, list[dict]]:
        """
        Grupperar violations efter POUR-princip.
        Ger en överskådlig bild av vilken tillgänglighetsaspekt som brister.

        Taxi Stockholm-koppling: rapport till produktägaren kan fokusera
        på vilka POUR-kategorier som har flest problem.
        """
        by_pour: dict[str, list[dict]] = {
            "Perceivable":    [],
            "Operable":       [],
            "Understandable": [],
            "Robust":         [],
            "Unknown":        [],
        }
        for violation in violations:
            category = classify_violation(violation["id"])
            by_pour[category].append(violation)
        return by_pour

    def count_affected_nodes(self, violations: list[dict]) -> int:
        """
        Räknar totalt antal påverkade HTML-element.
        Ett enda problem kan påverka många element (t.ex. alla bilder utan alt-text).
        """
        return sum(len(v.get("nodes", [])) for v in violations)

    def generate_report(self, scan_result: dict) -> str:
        """
        Genererar en läsbar textrapport från skanningsresultatet.

        I ett riktigt projekt: exporteras till HTML eller JSON för CI/CD-artefakter.
        """
        violations = scan_result.get("violations", [])
        passes     = scan_result.get("passes", [])
        url        = scan_result.get("url", "okänd URL")

        lines = [
            f"=== Tillgänglighetsrapport: {url} ===",
            f"Klara regler:      {len(passes)}",
            f"Överträdelser:     {len(violations)}",
            f"Påverkade element: {self.count_affected_nodes(violations)}",
            "",
        ]

        if violations:
            lines.append("--- Överträdelser (sorterade efter allvarlighet) ---")
            for v in violations:
                pour = classify_violation(v["id"])
                lines.append(
                    f"  [{v['impact'].upper():8}] [{pour:13}] {v['id']}: {v['description']}"
                )
                lines.append(f"    Åtgärd: {v['help']}")

        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# PYTEST-FIXTURER
# ─────────────────────────────────────────────────────────────────────────────

TARGET_URL = "https://techretail-staging.example.com"


@pytest.fixture(scope="module")
def axe():
    """Skapar en AxeScanner-instans för hela testmodulen."""
    return AxeScanner(TARGET_URL)


@pytest.fixture(scope="module")
def scan_result(axe):
    """Kör skanningen en gång och återanvänder resultatet i alla tester."""
    return axe.scan_page("/")


@pytest.fixture(scope="module")
def violations(scan_result):
    """Returnerar listan med violations från skanningsresultatet."""
    return scan_result.get("violations", [])


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Inga kritiska (critical) violations
# ─────────────────────────────────────────────────────────────────────────────

def test_inga_critical_violations(violations):
    """
    Verifierar att inga kritiska WCAG-violations finns.
    'critical' i axe-core = direkt hinder för användare med hjälpmedel.

    OBS: Testet misslyckas medvetet i simulationen (image-alt och label är critical).
    I ett riktigt projekt åtgärdar frontendteamet dessa innan release.

    Taxi Stockholm-koppling: en skärmläsaranvändare kan inte boka taxi
    om formulärfält saknar labels — bokningsknappen är oanvändbar.
    """
    critical = [v for v in violations if v.get("impact") == "critical"]

    assert len(critical) == 0, (
        f"Hittade {len(critical)} kritisk(a) WCAG-violation(er):\n"
        + "\n".join(f"  - {v['id']}: {v['description']}" for v in critical)
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Bilder har alt-text (Perceivable)
# ─────────────────────────────────────────────────────────────────────────────

def test_bilder_har_alt_text(violations):
    """
    Verifierar att image-alt-regeln inte är bruten.
    WCAG 1.1.1 (nivå A) — saknad alt-text är ett av de vanligaste felen.

    Taxi Stockholm-koppling: produktbilder i appen ska vara tillgängliga
    för synskadade kunder som använder VoiceOver (iOS) eller TalkBack (Android).
    """
    image_violations = [v for v in violations if v["id"] == "image-alt"]

    assert len(image_violations) == 0, (
        f"Bilder utan alt-text hittades! Påverkade element:\n"
        + "\n".join(
            f"  - {node['html']}"
            for v in image_violations
            for node in v.get("nodes", [])
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Formulärfält har labels (Understandable)
# ─────────────────────────────────────────────────────────────────────────────

def test_formularfalt_har_labels(violations):
    """
    Verifierar att alla formulärfält har associerade labels.
    WCAG 1.3.1 + 3.3.2 — formulär utan labels är oanvändbara med skärmläsare.

    Taxi Stockholm-koppling: bokningsformuläret (datum, tid, avreseadress)
    måste vara fullt tillgängligt för tangentbordsanvändare och skärmläsare.
    """
    label_violations = [v for v in violations if v["id"] == "label"]

    assert len(label_violations) == 0, (
        f"Formulärfält utan labels hittades! "
        f"Antal påverkade element: "
        f"{sum(len(v.get('nodes', [])) for v in label_violations)}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: POUR-klassificering täcker alla violations
# ─────────────────────────────────────────────────────────────────────────────

def test_alla_violations_ar_klassificerade(axe, violations):
    """
    Verifierar att ingen violation hamnar i 'Unknown'-kategorin.
    Om 'Unknown' > 0 behöver POUR_CLASSIFICATION uppdateras med nya rule-IDs.

    Taxi Stockholm-koppling: en rapport med 'Unknown'-kategorier ger inte
    produktägaren tillräcklig information för att prioritera åtgärder.
    """
    by_pour = axe.get_violations_by_pour(violations)
    unknown = by_pour.get("Unknown", [])

    assert len(unknown) == 0, (
        f"Följande violations saknar POUR-klassificering: "
        + ", ".join(v["id"] for v in unknown)
        + "\nLägg till dem i POUR_CLASSIFICATION-dictionen."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Rapport genereras och innehåller rätt sektioner
# ─────────────────────────────────────────────────────────────────────────────

def test_rapport_genereras_korrekt(axe, scan_result):
    """
    Verifierar att rapporten innehåller de sektioner som behövs.
    Rapporten används av testledaren för att kommunicera fynd till teamet.

    Taxi Stockholm-koppling: rapporten skickas till UX-teamet och
    produktägaren — den måste innehålla tillräcklig information för
    att kunna prioritera åtgärder.
    """
    rapport = axe.generate_report(scan_result)

    assert "Tillgänglighetsrapport" in rapport, "Rubriken saknas i rapporten"
    assert "Klara regler" in rapport,           "Statistik om godkända regler saknas"
    assert "Överträdelser" in rapport,          "Statistik om violations saknas"
    assert "Påverkade element" in rapport,      "Antal påverkade element saknas"
