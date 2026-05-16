"""
wait_utils.py – Explicit wait-hjälpfunktioner
Lektion 7: Mobiltest, Felsökning & Testobservabilitet

Ersätter time.sleep() med deterministiska waits som väntar på
faktiskt tillstånd istället för en godtycklig tid.

Varför explicit wait istället för sleep?
  sleep(2) väntar alltid 2 sekunder — oavsett om elementet dyker
  upp efter 0.1s eller aldrig. Explicit wait är snabbare när det
  går bra och ger ett tydligare felmeddelande när det går dåligt.

Taxi Stockholm-koppling: bokningsflödet har flera AJAX-anrop
(hitta förare, beräkna pris, bekräfta). Explicit wait säkerställer
att vi väntar på rätt tillstånd, inte bara en godtycklig tid.

Kör: pytest test_responsive.py -v  (används automatiskt av testerna)
"""

import logging
import time

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


def wait_for_element(
    page: Page,
    selector: str,
    timeout: int = 10_000,
    state: str = "visible",
) -> None:
    """
    Vänta tills ett element når önskat tillstånd.

    Args:
        page:     Playwright page-objekt
        selector: CSS-selektor (t.ex. "#confirm-btn") eller XPath
        timeout:  Max väntetid i millisekunder (standard: 10 s)
        state:    "visible" | "hidden" | "attached" | "detached"

    Raises:
        AssertionError med beskrivande meddelande vid timeout

    Exempel:
        # Vänta tills bokningsbekräftelse visas (max 15 sek)
        wait_for_element(page, "#booking-confirmation", timeout=15_000)

        # Vänta tills laddningsspinner försvinner
        wait_for_element(page, ".loading-spinner", state="hidden")
    """
    try:
        page.wait_for_selector(selector, state=state, timeout=timeout)
        logger.debug(f"Element '{selector}' nådde tillstånd '{state}'")
    except PlaywrightTimeoutError:
        current_url = page.url
        raise AssertionError(
            f"Timeout ({timeout} ms): Element '{selector}' nådde inte "
            f"tillstånd '{state}'.\n"
            f"  Nuvarande URL: {current_url}\n"
            f"  Tips: Öka timeout eller kontrollera att selektorn är korrekt."
        )


def wait_for_navigation(
    page: Page,
    url_pattern: str,
    timeout: int = 10_000,
) -> None:
    """
    Vänta tills sidan navigerat till en URL som innehåller url_pattern.

    Args:
        page:        Playwright page-objekt
        url_pattern: Delsträng som ska finnas i URL:en
        timeout:     Max väntetid i millisekunder

    Raises:
        AssertionError om navigationen inte sker inom timeout

    Taxi Stockholm-exempel:
        wait_for_navigation(page, "/booking/confirm")
        # Väntar tills URL innehåller "/booking/confirm"
    """
    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        if url_pattern in page.url:
            logger.info(f"Navigerade till URL med '{url_pattern}': {page.url}")
            return
        time.sleep(0.1)

    raise AssertionError(
        f"Timeout ({timeout} ms): URL innehåller inte '{url_pattern}'.\n"
        f"  Nuvarande URL: {page.url}"
    )


def wait_for_text(
    page: Page,
    selector: str,
    expected_text: str,
    timeout: int = 10_000,
) -> None:
    """
    Vänta tills ett element innehåller förväntad text.

    Användbart för dynamiska meddelanden som visas efter AJAX-anrop,
    t.ex. "Bokning bekräftad" eller felmeddelanden vid felaktig inloggning.

    Args:
        page:          Playwright page-objekt
        selector:      CSS-selektor för elementet
        expected_text: Text som ska finnas i elementet
        timeout:       Max väntetid i millisekunder

    Raises:
        AssertionError om texten inte dyker upp inom timeout

    Exempel:
        wait_for_text(page, "#flash", "Bokning bekräftad")
    """
    try:
        # Använd page.wait_for_function för textkontroll
        safe_text = expected_text.replace("'", "\\'")
        safe_sel  = selector.replace("'", "\\'")
        page.wait_for_function(
            f"document.querySelector('{safe_sel}')?.textContent"
            f"?.includes('{safe_text}')",
            timeout=timeout,
        )
        logger.info(f"Text '{expected_text}' hittad i '{selector}'")
    except PlaywrightTimeoutError:
        actual_text = ""
        element = page.locator(selector)
        if element.count() > 0:
            actual_text = element.first.text_content() or ""
        raise AssertionError(
            f"Timeout ({timeout} ms): '{expected_text}' hittades inte "
            f"i '{selector}'.\n"
            f"  Faktisk text: '{actual_text[:150]}'"
        )
