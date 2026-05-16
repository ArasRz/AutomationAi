"""
retry_fixture.py – Retry-logik med exponentiell backoff
Lektion 7: Mobiltest, Felsökning & Testobservabilitet

Flaky tests uppstår p.g.a. timing, nätverkslatens eller tillfälliga
miljöproblem. Retry-logik är ett SKYDDSNÄT — inte en lösning.
Lös alltid grundorsaken! Logga alltid retries så mönster syns.

Exponentiell backoff: 1s → 2s → 4s
  Varje försök väntar dubbelt så länge som föregående.
  Ger systemet tid att återhämta sig utan att bombardera det.

Taxi Stockholm-koppling: GPS-beroende i bokningsappen kan ge
sporadiska TimeoutError under hög belastning. Retry med backoff
ger systemet tid att återhämta sig utan att testet failar direkt.

Kör: pytest test_responsive.py -v  (retry_fixture importeras vid behov)
     python retry_fixture.py        (kör demo)
"""

import logging
import time
from typing import Any, Callable, Tuple, Type

logger = logging.getLogger(__name__)

# Vilka exceptions är "retry-bara" (tillfälliga fel)?
# Lägg till fler baserat på din tekniska miljö.
DEFAULT_RETRYABLE: Tuple[Type[Exception], ...] = (
    TimeoutError,
    ConnectionError,
    OSError,
)

# För Playwright-tester, lägg till:
# from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
# DEFAULT_RETRYABLE = (TimeoutError, ConnectionError, PlaywrightTimeoutError)


def retry_on_failure(
    func: Callable,
    max_retries: int = 3,
    backoff_base: float = 1.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRYABLE,
    test_name: str = "okänt test",
) -> Any:
    """
    Kör en funktion med exponentiell backoff vid tillfälliga fel.

    Väntetider med backoff_base=1: 1s → 2s → 4s

    Args:
        func:                  Funktion att köra (utan argument, använd lambda)
        max_retries:           Max antal omförsök efter första felet (standard: 3)
        backoff_base:          Baskonstant i sekunder för backoff-beräkning
        retryable_exceptions:  Vilka exceptions triggrar ett nytt försök
        test_name:             Testnamn för loggning

    Returns:
        Returvärdet från func() vid lyckat försök

    Raises:
        Samma exception som func() om alla försök misslyckas

    Exempel:
        # Klicka på en knapp som ibland inte är redo
        retry_on_failure(
            lambda: page.click("#book-taxi"),
            test_name="test_booking_flow"
        )

        # Hämta data som ibland ger ConnectionError
        data = retry_on_failure(
            lambda: requests.get(url).json(),
            max_retries=2,
            backoff_base=0.5,
        )
    """
    last_exception: Exception = Exception("Ingen körning gjordes")

    for attempt in range(max_retries + 1):
        try:
            result = func()
            if attempt > 0:
                # Logga att det lyckades efter retry — viktigt för spårning!
                logger.info(
                    f"[{test_name}] Lyckades på försök "
                    f"{attempt + 1}/{max_retries + 1} ✓"
                )
            return result

        except retryable_exceptions as exc:
            last_exception = exc

            if attempt == max_retries:
                logger.error(
                    f"[{test_name}] MISSLYCKADES efter {max_retries + 1} "
                    f"försök. Sista fel: {type(exc).__name__}: {exc}"
                )
                raise

            wait_time = backoff_base * (2 ** attempt)  # 1s, 2s, 4s, 8s...
            logger.warning(
                f"[{test_name}] Försök {attempt + 1}/{max_retries + 1} "
                f"misslyckades ({type(exc).__name__}: {exc}). "
                f"Väntar {wait_time:.1f}s innan nytt försök..."
            )
            time.sleep(wait_time)

    raise last_exception  # Nås aldrig i praktiken, men krävs av typcheckare


def with_retry(max_retries: int = 3, backoff_base: float = 1.0):
    """
    Dekorator för att lägga till retry-logik på en funktion.

    Användning som dekorator:
        @with_retry(max_retries=2, backoff_base=0.5)
        def klicka_bekrafta():
            page.click("#confirm-booking")

        klicka_bekrafta()  # Försöker automatiskt upp till 3 gånger

    Alternativt direkt i ett test:
        @with_retry()
        def hamta_pris():
            return page.locator("#price").text_content()

        pris = hamta_pris()
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return retry_on_failure(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                backoff_base=backoff_base,
                test_name=func.__name__,
            )
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# ─── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    """Kör som script för att se retry-logiken i aktion."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    attempt_counter = [0]

    def instabilt_anrop():
        """Simulerar ett anrop som misslyckas 2 gånger och sedan lyckas."""
        attempt_counter[0] += 1
        if attempt_counter[0] < 3:
            raise TimeoutError(f"Simulerat timeout (försök {attempt_counter[0]})")
        return f"Lyckades på försök {attempt_counter[0]}!"

    print("\n── Demo: retry_on_failure ─────────────────────────────")
    try:
        result = retry_on_failure(
            instabilt_anrop,
            max_retries=3,
            backoff_base=0.1,  # Kort väntetid för demo
            test_name="demo_bokning",
        )
        print(f"Resultat: {result}")
    except Exception as e:
        print(f"Misslyckades: {e}")

    print("\n── Demo: @with_retry dekorator ────────────────────────")
    counter = [0]

    @with_retry(max_retries=2, backoff_base=0.1)
    def alltid_misslyckas():
        counter[0] += 1
        raise ConnectionError(f"Servern svarar inte (försök {counter[0]})")

    try:
        alltid_misslyckas()
    except ConnectionError:
        print("Alla försök misslyckades — exception kastades vidare (korrekt).")
