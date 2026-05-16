"""
test_logger.py – Strukturerad logging i JSONL-format
Lektion 7: Mobiltest, Felsökning & Testobservabilitet

JSONL (JSON Lines) = en JSON-rad per händelse.
Varje rad är ett komplett, sökbart JSON-objekt.

Varför strukturerad logging?
  Med vanlig textlogg: "grep -i error app.log" ger röra
  Med JSONL:          "jq 'select(.status==\"failed\")'" filtrerar exakt
  Med JSONL:          Kompatibel med Grafana Loki, Elasticsearch, Datadog

Taxi Stockholm-koppling: strukturerade loggar gör det möjligt att
filtrera på suite_name="bokningsflöde" AND status="failed" för att
snabbt hitta alla misslyckade boknings-tester — utan att scrolla
igenom tusentals rader.

Kör: python test_logger.py    (kör inbyggd demo)
     pytest -s                (loggar visas i terminalen under testkörning)
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Standardinställningar för Python-logging (syns i pytest med -s)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

MAX_ERROR_LENGTH = 500  # Trunkera långa felmeddelanden för läsbarhet


class TestLogger:
    """
    Loggar testresultat i JSONL-format (en JSON-rad per händelse).

    Varje händelse innehåller alltid:
      timestamp   – ISO 8601 med UTC-tidszon (sökbar, sorterbar)
      event       – "test_start" | "test_end" | "suite_summary"
      suite_name  – För filtrering per testsvit

    Användning i ett pytest-test:
        from test_logger import TestLogger

        log = TestLogger("e2e_bokning")
        log.log_test_start("test_login", "test_auth.py")
        # ... kör testet ...
        log.log_test_end("test_login", "passed", 1234.5)
    """

    def __init__(
        self,
        suite_name: str,
        output_file: str = "test_results.jsonl",
    ):
        self.suite_name  = suite_name
        self.output_file = Path(output_file)
        # Skapa kataloger om de saknas
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"TestLogger startad: suite='{suite_name}' → {output_file}"
        )

    # ── Interna hjälpmetoder ────────────────────────────────────────────

    def _now(self) -> str:
        """ISO 8601 UTC-tidsstämpel, t.ex. '2026-05-10T14:30:00.123Z'."""
        return (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            + "Z"
        )

    def _write(self, data: dict) -> None:
        """Skriver ett JSON-objekt som en enda rad i JSONL-filen."""
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    # ── Publika loggmetoder ─────────────────────────────────────────────

    def log_test_start(self, test_name: str, test_file: str) -> None:
        """
        Loggar att ett test startar.

        Exempel-utdata (en rad i JSONL-filen):
            {"timestamp":"2026-05-10T14:30:00.123Z","event":"test_start",
             "test_name":"test_login","test_file":"test_auth.py",
             "suite_name":"e2e_bokning"}
        """
        entry = {
            "timestamp":  self._now(),
            "event":      "test_start",
            "test_name":  test_name,
            "test_file":  test_file,
            "suite_name": self.suite_name,
        }
        self._write(entry)
        logger.debug(f"START: {test_name}")

    def log_test_end(
        self,
        test_name:   str,
        status:      str,
        duration_ms: float,
        error:       Optional[str] = None,
    ) -> None:
        """
        Loggar att ett test avslutats.

        Args:
            test_name:   Testets namn
            status:      "passed" | "failed" | "skipped"
            duration_ms: Körtid i millisekunder
            error:       Felmeddelande vid failure (trunkeras till 500 tecken)

        Exempel-utdata:
            {"timestamp":"...","event":"test_end","test_name":"test_login",
             "status":"passed","duration_ms":2333,"suite_name":"e2e_bokning"}
        """
        entry = {
            "timestamp":   self._now(),
            "event":       "test_end",
            "test_name":   test_name,
            "status":      status,
            "duration_ms": round(duration_ms, 1),
            "suite_name":  self.suite_name,
        }
        if error:
            # Trunkera långa felstackar — JSONL-filen ska förbli läsbar
            entry["error"] = error[:MAX_ERROR_LENGTH]

        self._write(entry)

        log_level = logging.INFO if status == "passed" else logging.WARNING
        logger.log(
            log_level,
            f"  [{status.upper():7}] {test_name} ({duration_ms:.0f} ms)",
        )

    def log_suite_summary(
        self,
        total:   int,
        passed:  int,
        failed:  int,
        skipped: int,
    ) -> None:
        """
        Loggar sammanfattning när hela sviten är klar.

        Beräknar automatiskt pass_rate (0.0–1.0).

        Exempel-utdata:
            {"timestamp":"...","event":"suite_summary","total":25,
             "passed":23,"failed":2,"skipped":0,"pass_rate":0.92,
             "suite_name":"e2e_bokning"}
        """
        pass_rate = passed / total if total > 0 else 0.0
        entry = {
            "timestamp":  self._now(),
            "event":      "suite_summary",
            "total":      total,
            "passed":     passed,
            "failed":     failed,
            "skipped":    skipped,
            "pass_rate":  round(pass_rate, 4),
            "suite_name": self.suite_name,
        }
        self._write(entry)
        logger.info(
            f"SVIT KLAR — {passed}/{total} passerade "
            f"({pass_rate:.1%}), {failed} misslyckade, {skipped} hoppade"
        )


# ─── Demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    """Kör som script för att se JSONL-utdata i terminalen."""

    DEMO_FILE = "demo_results.jsonl"
    log = TestLogger("demo_bokning", output_file=DEMO_FILE)

    tester = [
        ("test_login_success",  "test_auth.py",    800,    "passed", None),
        ("test_booking_flow",   "test_booking.py", 12_500, "failed",
         "TimeoutError: #confirm-button ej synlig inom 10 000 ms"),
        ("test_logout",         "test_auth.py",    300,    "passed", None),
        ("test_map_load",       "test_map.py",     0,      "skipped",
         "Kräver GPS-hårdvara"),
    ]

    print(f"\n── Kör {len(tester)} demo-tester ──────────────────────────────")
    for name, fil, dur, status, err in tester:
        log.log_test_start(name, fil)
        time.sleep(0.01)  # Simulerar testkörtid
        log.log_test_end(name, status, dur, err)

    passed  = sum(1 for *_, s, _ in tester if s == "passed")
    failed  = sum(1 for *_, s, _ in tester if s == "failed")
    skipped = sum(1 for *_, s, _ in tester if s == "skipped")
    log.log_suite_summary(len(tester), passed, failed, skipped)

    print(f"\n── JSONL-loggfil ({DEMO_FILE}) ────────────────────────")
    with open(DEMO_FILE) as f:
        for rad in f:
            print(rad.rstrip())

    # Städa upp demo-filen
    import os
    os.remove(DEMO_FILE)
    print(f"\n(Demo-filen {DEMO_FILE} borttagen)")
