"""
generate_dashboard.py – HTML-dashboard för testobservabilitet
Lektion 7: Mobiltest, Felsökning & Testobservabilitet

Läser metrics/test_metrics.jsonl (en rad per körning) och genererar
en statisk HTML-fil med interaktiva Chart.js-diagram.

Diagram som genereras:
  1. Pass Rate-trend  — linjediagram (senaste 10 körningar)
  2. Körtid-trend     — linjediagram (total_duration_seconds)
  3. Feltyper         — munkdiagram (doughnut) med felkategorier

Taxi Stockholm-koppling: samma typ av dashboard används av testteam
för att snabbt se om ett API-problem slog ut 50 tester på en natt
— utan att behöva scrolla igenom CI-loggar.

Kör:
  pytest lektion7_mobiltest_felsokning/ -v   (genererar metrics)
  python lektion7_mobiltest_felsokning/generate_dashboard.py
  open lektion7_mobiltest_felsokning/dashboard.html
"""

import json
from datetime import datetime
from pathlib import Path

# ── Sökvägar ────────────────────────────────────────────────────────────────
HERE          = Path(__file__).parent
METRICS_FILE  = HERE / "metrics" / "test_metrics.jsonl"
OUTPUT_FILE   = HERE / "dashboard.html"
MAX_RUNS      = 10   # Visa senaste 10 körningar i diagrammen


# ── Hjälpfunktioner ─────────────────────────────────────────────────────────

def load_metrics(path: Path, max_runs: int = MAX_RUNS) -> list[dict]:
    """
    Läser JSONL-filen och returnerar de senaste max_runs körningarna.

    Returnerar demo-data om filen saknas — så dashboarden alltid går
    att generera och visa utan att ha kört tester först.
    """
    if not path.exists():
        print(f"  OBS: {path.name} saknas — använder demo-data.")
        return _demo_data()

    runs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    runs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # Hoppa över trasiga rader

    if not runs:
        print("  OBS: Metrics-filen är tom — använder demo-data.")
        return _demo_data()

    return runs[-max_runs:]


def _demo_data() -> list[dict]:
    """
    Returnerar realistisk demo-data för 6 körningar.

    Visa trender: pass rate förbättras efter att bugs fixas,
    körtiden varierar något.
    """
    base = [
        {"timestamp": "2026-05-10T22:00:00.000Z", "total_duration_seconds": 45.2,
         "total_tests": 20, "passed": 15, "failed": 4, "skipped": 1,
         "pass_rate": 0.75, "tests_per_second": 0.44,
         "top_3_slowest": [
             {"test": "test_checkout_responsive[Desktop]", "duration_s": 8.1},
             {"test": "test_navigation_responsive[iPad]",  "duration_s": 6.4},
             {"test": "test_product_card_layout[iPhone_15_Pro]", "duration_s": 5.2},
         ],
         "failure_types": {"TimeoutError": 3, "AssertionError": 1}},
        {"timestamp": "2026-05-11T22:00:00.000Z", "total_duration_seconds": 42.8,
         "total_tests": 20, "passed": 16, "failed": 3, "skipped": 1,
         "pass_rate": 0.80, "tests_per_second": 0.47,
         "top_3_slowest": [
             {"test": "test_checkout_responsive[Desktop]", "duration_s": 7.9},
             {"test": "test_navigation_responsive[iPad]",  "duration_s": 6.1},
             {"test": "test_touch_targets_mobile[iPhone_SE]", "duration_s": 4.8},
         ],
         "failure_types": {"TimeoutError": 2, "AssertionError": 1}},
        {"timestamp": "2026-05-12T22:00:00.000Z", "total_duration_seconds": 38.5,
         "total_tests": 20, "passed": 18, "failed": 2, "skipped": 0,
         "pass_rate": 0.90, "tests_per_second": 0.52,
         "top_3_slowest": [
             {"test": "test_checkout_responsive[Desktop]", "duration_s": 7.3},
             {"test": "test_navigation_responsive[iPad]",  "duration_s": 5.8},
             {"test": "test_product_card_layout[iPhone_SE]", "duration_s": 4.5},
         ],
         "failure_types": {"TimeoutError": 1, "AssertionError": 1}},
        {"timestamp": "2026-05-13T22:00:00.000Z", "total_duration_seconds": 36.1,
         "total_tests": 20, "passed": 19, "failed": 1, "skipped": 0,
         "pass_rate": 0.95, "tests_per_second": 0.55,
         "top_3_slowest": [
             {"test": "test_checkout_responsive[Desktop]", "duration_s": 6.9},
             {"test": "test_navigation_responsive[iPad]",  "duration_s": 5.5},
             {"test": "test_touch_targets_mobile[iPhone_SE]", "duration_s": 4.2},
         ],
         "failure_types": {"AssertionError": 1}},
        {"timestamp": "2026-05-14T08:00:00.000Z", "total_duration_seconds": 34.7,
         "total_tests": 20, "passed": 20, "failed": 0, "skipped": 0,
         "pass_rate": 1.00, "tests_per_second": 0.58,
         "top_3_slowest": [
             {"test": "test_checkout_responsive[Desktop]", "duration_s": 6.7},
             {"test": "test_navigation_responsive[iPad]",  "duration_s": 5.2},
             {"test": "test_product_card_layout[iPad]", "duration_s": 4.0},
         ],
         "failure_types": {}},
    ]
    return base


def _short_label(ts: str) -> str:
    """
    Kortlabel för x-axeln, t.ex. '2026-05-14 08:00'.
    """
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%m-%d %H:%M")
    except ValueError:
        return ts[:16]


def _aggregate_failure_types(runs: list[dict]) -> tuple[list[str], list[int]]:
    """Summerar alla feltyper från alla körningar."""
    totals: dict[str, int] = {}
    for run in runs:
        for ftype, count in run.get("failure_types", {}).items():
            totals[ftype] = totals.get(ftype, 0) + count
    if not totals:
        return ["Inga fel"], [1]
    labels  = list(totals.keys())
    values  = [totals[k] for k in labels]
    return labels, values


# ── HTML-generator ───────────────────────────────────────────────────────────

def generate_html(runs: list[dict]) -> str:
    """Bygger hela dashboard-HTML:en som en sträng."""

    labels      = [_short_label(r["timestamp"]) for r in runs]
    pass_rates  = [round(r["pass_rate"] * 100, 1) for r in runs]
    durations   = [r["total_duration_seconds"] for r in runs]
    total_tests = runs[-1]["total_tests"] if runs else 0
    last_passed = runs[-1]["passed"]      if runs else 0
    last_failed = runs[-1]["failed"]      if runs else 0
    last_rate   = pass_rates[-1]          if pass_rates else 0

    ft_labels, ft_values = _aggregate_failure_types(runs)

    # JavaScript-arrayer (JSON-kodade för säkerhet)
    js_labels    = json.dumps(labels)
    js_rates     = json.dumps(pass_rates)
    js_durations = json.dumps(durations)
    js_ft_labels = json.dumps(ft_labels)
    js_ft_values = json.dumps(ft_values)

    # Statusfärg för KPI-kortet
    rate_color = (
        "#22c55e" if last_rate >= 90 else
        "#f59e0b" if last_rate >= 70 else
        "#ef4444"
    )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Testobservabilitet – Lektion 7 Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 2rem 1rem;
    }}

    h1 {{
      text-align: center;
      font-size: 1.6rem;
      font-weight: 700;
      margin-bottom: 0.3rem;
      color: #f8fafc;
    }}
    .subtitle {{
      text-align: center;
      font-size: 0.85rem;
      color: #94a3b8;
      margin-bottom: 2rem;
    }}

    /* KPI-kort */
    .kpi-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      justify-content: center;
      margin-bottom: 2rem;
    }}
    .kpi-card {{
      background: #1e293b;
      border-radius: 12px;
      padding: 1.2rem 1.8rem;
      min-width: 140px;
      text-align: center;
      border: 1px solid #334155;
    }}
    .kpi-value {{
      font-size: 2rem;
      font-weight: 800;
      line-height: 1;
      margin-bottom: 0.3rem;
    }}
    .kpi-label {{
      font-size: 0.78rem;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    /* Diagram-grid */
    .chart-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
    }}
    .chart-card {{
      background: #1e293b;
      border-radius: 12px;
      padding: 1.5rem;
      border: 1px solid #334155;
    }}
    .chart-card h2 {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #cbd5e1;
      margin-bottom: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .chart-card canvas {{
      max-height: 260px;
    }}

    /* Långsammaste tester */
    .slowest-card {{
      background: #1e293b;
      border-radius: 12px;
      padding: 1.5rem;
      border: 1px solid #334155;
      max-width: 1200px;
      margin: 1.5rem auto 0;
    }}
    .slowest-card h2 {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #cbd5e1;
      margin-bottom: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .slowest-row {{
      display: flex;
      align-items: center;
      gap: 0.8rem;
      padding: 0.5rem 0;
      border-bottom: 1px solid #334155;
    }}
    .slowest-row:last-child {{ border-bottom: none; }}
    .slowest-bar-bg {{
      flex: 1;
      background: #0f172a;
      border-radius: 4px;
      height: 8px;
      overflow: hidden;
    }}
    .slowest-bar {{
      height: 100%;
      background: #6366f1;
      border-radius: 4px;
    }}
    .slowest-name  {{ font-size: 0.82rem; color: #94a3b8; min-width: 260px; }}
    .slowest-value {{ font-size: 0.82rem; color: #e2e8f0; min-width: 52px; text-align: right; }}

    footer {{
      text-align: center;
      margin-top: 2.5rem;
      font-size: 0.75rem;
      color: #475569;
    }}
  </style>
</head>
<body>

<h1>Testobservabilitet – Lektion 7</h1>
<p class="subtitle">Genererad {generated_at} &nbsp;·&nbsp; Senaste {len(runs)} körning(ar) &nbsp;·&nbsp; {METRICS_FILE.name}</p>

<!-- KPI-kort -->
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-value" style="color:{rate_color}">{last_rate}%</div>
    <div class="kpi-label">Pass Rate</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#38bdf8">{total_tests}</div>
    <div class="kpi-label">Tester totalt</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#22c55e">{last_passed}</div>
    <div class="kpi-label">Godkänt</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#ef4444">{last_failed}</div>
    <div class="kpi-label">Misslyckade</div>
  </div>
</div>

<!-- Diagram -->
<div class="chart-grid">

  <!-- 1. Pass Rate-trend -->
  <div class="chart-card">
    <h2>Pass Rate-trend (%)</h2>
    <canvas id="passRateChart"></canvas>
  </div>

  <!-- 2. Körtid-trend -->
  <div class="chart-card">
    <h2>Körtid per körning (sekunder)</h2>
    <canvas id="durationChart"></canvas>
  </div>

  <!-- 3. Feltyper (doughnut) -->
  <div class="chart-card">
    <h2>Feltyper – alla körningar</h2>
    <canvas id="failureChart"></canvas>
  </div>

</div>

<!-- Långsammaste tester (från senaste körning) -->
<div class="slowest-card">
  <h2>Långsammaste tester – senaste körning</h2>
  <div id="slowest-list"></div>
</div>

<footer>
  Lektion 7 · Testautomation och AI inom IT-test · Frans Schartaus Handelsinstitut
</footer>

<script>
// ── Data från Python ────────────────────────────────────────────────────────
const labels    = {js_labels};
const passRates = {js_rates};
const durations = {js_durations};
const ftLabels  = {js_ft_labels};
const ftValues  = {js_ft_values};
const slowest   = {json.dumps(runs[-1].get("top_3_slowest", []) if runs else [])};

// ── Gemensamma inställningar ─────────────────────────────────────────────────
const gridColor  = "rgba(148,163,184,0.15)";
const tickColor  = "#94a3b8";
const baseFont   = {{ size: 11, family: "system-ui, sans-serif" }};

function lineOptions(yLabel, color) {{
  return {{
    responsive: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        backgroundColor: "#1e293b",
        titleColor: "#f1f5f9",
        bodyColor: "#cbd5e1",
        borderColor: "#334155",
        borderWidth: 1,
      }},
    }},
    scales: {{
      x: {{
        ticks: {{ color: tickColor, font: baseFont, maxRotation: 45 }},
        grid:  {{ color: gridColor }},
      }},
      y: {{
        title: {{ display: true, text: yLabel, color: tickColor, font: baseFont }},
        ticks: {{ color: tickColor, font: baseFont }},
        grid:  {{ color: gridColor }},
      }},
    }},
  }};
}}

// ── 1. Pass Rate ─────────────────────────────────────────────────────────────
new Chart(document.getElementById("passRateChart"), {{
  type: "line",
  data: {{
    labels,
    datasets: [{{
      label: "Pass Rate %",
      data: passRates,
      borderColor: "#22c55e",
      backgroundColor: "rgba(34,197,94,0.15)",
      pointBackgroundColor: "#22c55e",
      tension: 0.3,
      fill: true,
    }}],
  }},
  options: {{
    ...lineOptions("Pass Rate (%)", "#22c55e"),
    scales: {{
      ...lineOptions("Pass Rate (%)", "#22c55e").scales,
      y: {{
        ...lineOptions("Pass Rate (%)", "#22c55e").scales.y,
        min: 0,
        max: 100,
        ticks: {{
          color: tickColor,
          font: baseFont,
          callback: v => v + "%",
        }},
      }},
    }},
  }},
}});

// ── 2. Körtid ────────────────────────────────────────────────────────────────
new Chart(document.getElementById("durationChart"), {{
  type: "line",
  data: {{
    labels,
    datasets: [{{
      label: "Körtid (s)",
      data: durations,
      borderColor: "#38bdf8",
      backgroundColor: "rgba(56,189,248,0.15)",
      pointBackgroundColor: "#38bdf8",
      tension: 0.3,
      fill: true,
    }}],
  }},
  options: lineOptions("Sekunder", "#38bdf8"),
}});

// ── 3. Feltyper (munkdiagram) ────────────────────────────────────────────────
new Chart(document.getElementById("failureChart"), {{
  type: "doughnut",
  data: {{
    labels: ftLabels,
    datasets: [{{
      data: ftValues,
      backgroundColor: [
        "#ef4444", "#f59e0b", "#6366f1", "#ec4899",
        "#14b8a6", "#84cc16", "#f97316",
      ],
      borderColor: "#0f172a",
      borderWidth: 2,
    }}],
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{
        position: "bottom",
        labels: {{ color: tickColor, font: baseFont, padding: 14 }},
      }},
      tooltip: {{
        backgroundColor: "#1e293b",
        titleColor: "#f1f5f9",
        bodyColor: "#cbd5e1",
        borderColor: "#334155",
        borderWidth: 1,
      }},
    }},
    cutout: "60%",
  }},
}});

// ── 4. Långsammaste tester ───────────────────────────────────────────────────
const container = document.getElementById("slowest-list");
if (!slowest.length) {{
  container.innerHTML = '<p style="color:#64748b;font-size:0.85rem">Inga data tillgängliga.</p>';
}} else {{
  const maxDur = Math.max(...slowest.map(s => s.duration_s));
  slowest.forEach(s => {{
    const pct = Math.round((s.duration_s / maxDur) * 100);
    container.innerHTML += `
      <div class="slowest-row">
        <span class="slowest-name">${{s.test}}</span>
        <div class="slowest-bar-bg">
          <div class="slowest-bar" style="width:${{pct}}%"></div>
        </div>
        <span class="slowest-value">${{s.duration_s}} s</span>
      </div>`;
  }});
}}
</script>
</body>
</html>"""


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'─' * 52}")
    print("  Lektion 7 – Genererar testdashboard")
    print(f"{'─' * 52}")

    runs = load_metrics(METRICS_FILE)
    print(f"  Körningar inlästa: {len(runs)}")

    html = generate_html(runs)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"  Dashboard sparad  → {OUTPUT_FILE}")
    print(f"  Öppna med:          open {OUTPUT_FILE.relative_to(Path.cwd())}")
    print(f"{'─' * 52}\n")
