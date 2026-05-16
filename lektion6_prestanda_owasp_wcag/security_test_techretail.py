"""
Övning 2 – Säkerhetstestning med OWASP ZAP (simulerad)
Lektion 6: Prestanda, Säkerhet & Tillgänglighetstest

OBS: I ett riktigt projekt anropar ZAPScanner en riktig OWASP ZAP-instans
via python-owasp-zap-v2.4 (ZAP REST API). Här simulerar vi svaren så att
du kan köra testerna utan att ha ZAP installerat.

Kör: pytest security_test_techretail.py -v
"""

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# OWASP ZAP Scanner
# I ett riktigt projekt:
#   from zapv2 import ZAPv2
#   zap = ZAPv2(apikey='din-api-nyckel', proxies={'http': 'http://localhost:8080'})
# ─────────────────────────────────────────────────────────────────────────────

class ZAPScanner:
    """
    Klass som kapslar in OWASP ZAP-funktionalitet.

    Taxi Stockholm-koppling: används för att skanna bokningssystemets
    webbgränssnitt efter kända säkerhetssårbarheter (OWASP Top 10).
    """

    # Risk-nivåer enligt OWASP ZAP terminologi
    RISK_HIGH   = "High"
    RISK_MEDIUM = "Medium"
    RISK_LOW    = "Low"
    RISK_INFO   = "Informational"

    def __init__(self, target_url: str):
        self.target_url = target_url
        # I produktion: self.zap = ZAPv2(apikey=..., proxies=...)

    def spider_scan(self) -> list[str]:
        """
        Crawlar målwebbplatsen och hittar alla URL:er.
        Returnerar lista med hittade URL:er.

        I produktion:
            scan_id = self.zap.spider.scan(self.target_url)
            self.zap.spider.wait_for_complete(scan_id)
            return self.zap.spider.results(scan_id)
        """
        # Simulerade URL:er som ZAP skulle hitta på TechRetail AB:s sajt
        return [
            f"{self.target_url}/",
            f"{self.target_url}/products",
            f"{self.target_url}/products/1",
            f"{self.target_url}/cart",
            f"{self.target_url}/checkout",
            f"{self.target_url}/login",
            f"{self.target_url}/api/products",
        ]

    def active_scan(self) -> str:
        """
        Kör aktiv skanning — ZAP skickar attackvektorer mot varje URL.
        Returnerar scan-ID (används för att hämta resultat).

        I produktion:
            scan_id = self.zap.ascan.scan(self.target_url)
            while int(self.zap.ascan.status(scan_id)) < 100:
                time.sleep(5)
            return scan_id
        """
        return "scan_12345"  # Simulerat scan-ID

    def get_alerts(self) -> list[dict]:
        """
        Hämtar alla fynd (alerts) från den aktiva skanningen.
        Returnerar lista med alert-dictionaries.

        I produktion:
            return self.zap.core.alerts(baseurl=self.target_url)
        """
        # Simulerade fynd — dessa är realistiska ZAP-alerts
        return [
            {
                "name":        "X-Content-Type-Options Header Missing",
                "risk":        self.RISK_LOW,
                "confidence":  "Medium",
                "url":         f"{self.target_url}/",
                "description": "HTTP-headern X-Content-Type-Options saknas, "
                               "vilket tillåter MIME-type sniffing.",
                "solution":    "Lägg till 'X-Content-Type-Options: nosniff' i alla HTTP-svar.",
            },
            {
                "name":        "Cookie Without Secure Flag",
                "risk":        self.RISK_MEDIUM,
                "confidence":  "Medium",
                "url":         f"{self.target_url}/login",
                "description": "Session-cookien saknar Secure-flaggan och kan "
                               "skickas över okrypterade HTTP-anslutningar.",
                "solution":    "Sätt Secure-flaggan på alla session-cookies.",
            },
            {
                "name":        "SQL Injection",
                "risk":        self.RISK_HIGH,
                "confidence":  "High",
                "url":         f"{self.target_url}/products?id=1",
                "description": "Möjlig SQL-injection i parametern 'id'. "
                               "En angripare kan manipulera databas-frågor.",
                "solution":    "Använd parameteriserade SQL-frågor (prepared statements).",
            },
            {
                "name":        "Application Error Disclosure",
                "risk":        self.RISK_LOW,
                "confidence":  "Medium",
                "url":         f"{self.target_url}/checkout",
                "description": "Applikationen avslöjar stack trace i felmeddelanden.",
                "solution":    "Dölj interna felmeddelanden i produktionsmiljön.",
            },
            {
                "name":        "Information Disclosure - Debug Error Messages",
                "risk":        self.RISK_INFO,
                "confidence":  "Low",
                "url":         f"{self.target_url}/api/products",
                "description": "Debug-information finns i HTTP-svaret.",
                "solution":    "Stäng av debug-läget i produktionsmiljön.",
            },
        ]

    def categorize_alerts(self) -> dict[str, list[dict]]:
        """
        Grupperar alerts efter risknivå.
        Returnerar dict med High/Medium/Low/Informational som nycklar.

        Taxi Stockholm-koppling: ger en snabb överblick av hur allvarliga
        säkerhetsproblemen är — High kräver omedelbar åtgärd.
        """
        alerts = self.get_alerts()
        categorized = {
            self.RISK_HIGH:   [],
            self.RISK_MEDIUM: [],
            self.RISK_LOW:    [],
            self.RISK_INFO:   [],
        }
        for alert in alerts:
            risk = alert.get("risk", self.RISK_INFO)
            if risk in categorized:
                categorized[risk].append(alert)
        return categorized

    def get_alert_summary(self) -> dict[str, int]:
        """
        Returnerar antal fynd per risknivå.
        Används för att snabbt avgöra om en sajt har kritiska problem.

        Exempel på en pass/fail-regel i CI/CD:
            assert summary['High'] == 0, "Kritiska säkerhetsproblem hittades!"
        """
        categorized = self.categorize_alerts()
        return {
            risk: len(alerts)
            for risk, alerts in categorized.items()
        }


# ─────────────────────────────────────────────────────────────────────────────
# PYTEST-FIXTURER
# ─────────────────────────────────────────────────────────────────────────────

TARGET_URL = "https://techretail-staging.example.com"


@pytest.fixture(scope="module")
def scanner():
    """
    Skapar en ZAPScanner-instans för alla tester i modulen.
    scope="module" = skapas en gång, återanvänds av alla tester.
    """
    return ZAPScanner(TARGET_URL)


@pytest.fixture(scope="module")
def alerts(scanner):
    """Kör aktiv skanning och returnerar alla alerts."""
    scanner.spider_scan()
    scanner.active_scan()
    return scanner.get_alerts()


@pytest.fixture(scope="module")
def summary(scanner):
    """Returnerar alert-sammanfattningen per risknivå."""
    return scanner.get_alert_summary()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Spider scan hittar URL:er
# ─────────────────────────────────────────────────────────────────────────────

def test_spider_hittar_urls(scanner):
    """
    Verifierar att spider-skanningen hittar URL:er på sajten.

    Taxi Stockholm-koppling: ZAP crawlar bokningssystemets sidor
    och bygger upp en karta över alla endpoints att skanna.
    """
    urls = scanner.spider_scan()

    assert len(urls) > 0, "Spider-skanningen hittade inga URL:er"
    assert any(TARGET_URL in url for url in urls), (
        f"Inga URL:er tillhör måldomänen {TARGET_URL}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Inga High-risk-alerts
# ─────────────────────────────────────────────────────────────────────────────

def test_inga_kritiska_sarbarheter(summary):
    """
    Verifierar att inga High-risk-alerts finns.
    Detta är det viktigaste testet — High-risk innebär omedelbar fara.

    I ett riktigt CI/CD-flöde: detta test blockerar deployment om
    kritiska sårbarheter hittas. Säkerhetsteamet måste åtgärda dem.

    OBS: I simulationen finns en High-risk SQL Injection — testet
    kommer att misslyckas medvetet för att visa hur det ser ut i verkligheten.
    Kommentera bort SQL Injection-alerten i get_alerts() för att se testet grönt.
    """
    high_risk_count = summary.get(ZAPScanner.RISK_HIGH, 0)

    assert high_risk_count == 0, (
        f"Hittade {high_risk_count} kritisk(a) säkerhetssårbarhet(er) (High risk). "
        f"Åtgärda dessa innan deployment!"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Max 3 Medium-risk-alerts
# ─────────────────────────────────────────────────────────────────────────────

def test_fa_medium_sarbarheter(summary):
    """
    Verifierar att det finns max 3 Medium-risk-alerts.
    Medium-risk ska åtgärdas men blockerar inte nödvändigtvis deployment.

    Taxi Stockholm-koppling: definieras i testmandatet — hur många
    Medium-alerts tolereras i staging innan release?
    """
    medium_risk_count = summary.get(ZAPScanner.RISK_MEDIUM, 0)

    assert medium_risk_count <= 3, (
        f"Hittade {medium_risk_count} Medium-risk-alerts (max tillåtet: 3). "
        f"Granska och åtgärda."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Kategorisering fungerar korrekt
# ─────────────────────────────────────────────────────────────────────────────

def test_kategorisering_av_alerts(scanner):
    """
    Verifierar att kategoriseringen grouperar alerts korrekt.
    Alla alerts ska hamna i rätt risknivå-bucket.
    """
    categorized = scanner.categorize_alerts()

    # Alla fyra kategorier ska finnas
    for risk_level in [ZAPScanner.RISK_HIGH, ZAPScanner.RISK_MEDIUM,
                       ZAPScanner.RISK_LOW, ZAPScanner.RISK_INFO]:
        assert risk_level in categorized, (
            f"Risknivå '{risk_level}' saknas i kategoriseringen"
        )

    # Totalt antal kategoriserade alerts ska stämma med rådata
    total_kategoriserade = sum(len(v) for v in categorized.values())
    total_raw = len(scanner.get_alerts())

    assert total_kategoriserade == total_raw, (
        f"Kategorisering tappade alerts: {total_raw} raw, "
        f"men {total_kategoriserade} kategoriserade"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: SQL Injection-alert innehåller lösningsförslag
# ─────────────────────────────────────────────────────────────────────────────

def test_sql_injection_alert_har_losning(alerts):
    """
    Verifierar att SQL Injection-alerten (om den finns) innehåller
    ett lösningsförslag.

    I ett riktigt projekt: ZAP returnerar alltid en 'solution'-text.
    Testet verifierar att vår kategorisering bevarar all metadata.

    Taxi Stockholm-koppling: teamen behöver konkreta åtgärdsförslag,
    inte bara "SQL Injection hittades".
    """
    sql_alerts = [
        a for a in alerts
        if "SQL Injection" in a.get("name", "")
    ]

    if not sql_alerts:
        pytest.skip("Ingen SQL Injection-alert hittades — hoppar över testet")

    for alert in sql_alerts:
        assert "solution" in alert, (
            f"SQL Injection-alert saknar lösningsförslag: {alert}"
        )
        assert len(alert["solution"]) > 0, (
            "SQL Injection-alert har tomt lösningsförslag"
        )
