"""
conftest.py – pytest-hooks för automatisk metrics-insamling
Lektion 7: Mobiltest, Felsökning & Testobservabilitet

Dessa hooks körs automatiskt av pytest utan att du ändrar något i testfilerna.

Hooks som används:
  pytest_configure       – Initialisera räknare och timer vid sessionstart
  pytest_runtest_makereport – Samla in per-test-resultat (status, tid, feltyp)
  pytest_sessionfinish   – Skriv metrics till JSONL-fil vid sessionens slut

Metrics sparas i: lektion7_mobiltest_felsokning/metrics/test_metrics.jsonl
Varje körning lägger till EN RAD (append) — historik bevaras.

Kör: pytest lektion7_mobiltest_felsokning/ -v
     → Metrics sparas automatiskt
     → Generera dashboard: python lektion7_mobiltest_felsokning/generate_dashboard.py
"""

import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

# Metrics sparas i metrics/-undermappen relativt denna conftest.py
METRICS_FILE = Path(__file__).parent / "metrics" / "test_metrics.jsonl"


def pytest_configure(config: Any) -> None:
    """Initialisera metrics-datainsamling när sessionen startar."""
    config._l7_start_time = time.time()
    config._l7_results = {
        "passed":         0,
        "failed":         0,
        "skipped":        0,
        "errors":         [],   # {"test", "type", "duration", "message"}
        "test_durations": {},   # {"testnamn": duration_sekunder}
    }
    # Säkerställ att metrics-katalogen finns
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Any:
    """
    Samla in resultat per test.

    hookwrapper=True ger åtkomst till rapporten EFTER att pytest skapat den.
    call.when == "call" är själva testfasen (setup/teardown exkluderas).

    Feltypen (t.ex. "TimeoutError", "AssertionError") sparas för
    kategorisering — samma mönster som failure_analysis.md Del A.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return  # Hoppa över setup/teardown

    results = item.config._l7_results

    if report.passed:
        results["passed"] += 1

    elif report.failed:
        results["failed"] += 1
        error_type = "Unknown"
        error_msg  = ""
        if call.excinfo:
            error_type = type(call.excinfo.value).__name__
            error_msg  = str(call.excinfo.value)[:200]
        results["errors"].append({
            "test":     item.name,
            "type":     error_type,
            "duration": round(report.duration, 3),
            "message":  error_msg,
        })

    elif report.skipped:
        results["skipped"] += 1

    # Spara körtid för "slowest tests"-beräkning
    results["test_durations"][item.name] = report.duration


def pytest_sessionfinish(session: Any, exitstatus: Any) -> None:
    """
    Skriv metrics till JSONL-fil när hela sessionen är klar.

    Filen använder JSONL-format (en rad per körning) — historik bevaras
    och kan läsas av generate_dashboard.py.
    """
    results = session.config._l7_results
    total_duration = time.time() - session.config._l7_start_time

    total    = results["passed"] + results["failed"] + results["skipped"]
    pass_rate = results["passed"] / total if total > 0 else 0.0

    # De 3 långsammaste testerna
    top_3_slowest = [
        {"test": name, "duration_s": round(dur, 3)}
        for name, dur in sorted(
            results["test_durations"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]
    ]

    # Antal fel per feltyp (för cirkeldiagrammet i dashboarden)
    failure_types: dict = defaultdict(int)
    for err in results["errors"]:
        failure_types[err["type"]] += 1

    metrics = {
        "timestamp":              (
            datetime.now(timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        ),
        "total_duration_seconds": round(total_duration, 2),
        "total_tests":            total,
        "passed":                 results["passed"],
        "failed":                 results["failed"],
        "skipped":                results["skipped"],
        "pass_rate":              round(pass_rate, 4),
        "tests_per_second":       round(total / total_duration, 2) if total_duration > 0 else 0,
        "top_3_slowest":          top_3_slowest,
        "failure_types":          dict(failure_types),
    }

    # Append en rad — historik bevaras mellan körningar
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(metrics, ensure_ascii=False) + "\n")

    # Sammanfattning i terminalen
    print(f"\n{'─' * 52}")
    print(f"  Metrics sparade → {METRICS_FILE.name}")
    print(f"  Pass rate:  {pass_rate:.1%}  ({results['passed']}/{total})")
    print(f"  Körtid:     {total_duration:.1f} s")
    if failure_types:
        print(f"  Feltyper:   {dict(failure_types)}")
    print(f"  Dashboard:  python generate_dashboard.py")
    print(f"{'─' * 52}")
