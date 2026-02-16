from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


def render_dashboard_html(dashboard: dict[str, Any], output_path: str | Path) -> str:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    campaign_id = str(dashboard.get("campaign_id", "unknown"))
    session_count = int(dashboard.get("session_count", 0))
    summary = dashboard.get("summary", {}) if isinstance(dashboard.get("summary"), dict) else {}
    trends = dashboard.get("trends", {}) if isinstance(dashboard.get("trends"), dict) else {}

    hp_trend = trends.get("party_hp", []) if isinstance(trends.get("party_hp"), list) else []
    fail_trend = trends.get("fail_state", []) if isinstance(trends.get("fail_state"), list) else []
    risks = trends.get("recurring_risk_flags", []) if isinstance(trends.get("recurring_risk_flags"), list) else []

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Campaign Dashboard - {escape(campaign_id)}</title>
  <style>
    body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; background: #0f1115; color: #e6e9ef; }}
    h1, h2 {{ margin: 0 0 12px; }}
    .muted {{ color: #9aa3b2; }}
    .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); margin-bottom: 24px; }}
    .card {{ background: #171a21; border: 1px solid #242a36; border-radius: 10px; padding: 14px; }}
    .metric {{ font-size: 28px; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
    th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #262c38; font-size: 14px; }}
    th {{ color: #9aa3b2; font-weight: 600; }}
    .bar-wrap {{ background: #202533; border-radius: 6px; height: 8px; width: 100%; }}
    .bar {{ background: #5c8dff; height: 8px; border-radius: 6px; }}
    .section {{ margin-bottom: 24px; }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #202533; color: #c9d3e5; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>Campaign Dashboard <span class=\"pill\">{escape(campaign_id)}</span></h1>
  <p class=\"muted\">Session count: {session_count}</p>

  <div class=\"grid\">{_summary_cards(summary)}</div>

  <div class=\"section\">
    <h2>Party HP Trend</h2>
    {_hp_table(hp_trend)}
  </div>

  <div class=\"section\">
    <h2>Fail-State Trend</h2>
    {_fail_table(fail_trend)}
  </div>

  <div class=\"section\">
    <h2>Recurring Risk Flags</h2>
    {_risk_table(risks)}
  </div>
</body>
</html>
"""

    destination.write_text(html, encoding="utf-8")
    return str(destination)


def _summary_cards(summary: dict[str, Any]) -> str:
    items = [
        ("TPK Rate", summary.get("tpk_rate", 0)),
        ("Clue Discovery Rate", summary.get("clue_discovery_rate", 0)),
        ("Avg Stalled Turns", summary.get("avg_stalled_turns_estimate", 0)),
    ]
    cards = []
    for label, value in items:
        cards.append(
            f"<div class='card'><div class='muted'>{escape(label)}</div><div class='metric'>{escape(str(value))}</div></div>"
        )
    return "".join(cards)


def _hp_table(hp_trend: list[dict[str, Any]]) -> str:
    if not hp_trend:
        return "<p class='muted'>No trend data.</p>"

    max_hp = max(float(item.get("avg_final_party_hp", 0) or 0) for item in hp_trend) or 1.0
    rows = []
    for item in hp_trend:
        session_id = escape(str(item.get("session_id", "unknown")))
        hp = float(item.get("avg_final_party_hp", 0) or 0)
        width = max(2, int((hp / max_hp) * 100))
        rows.append(
            "".join(
                [
                    "<tr>",
                    f"<td>{session_id}</td>",
                    f"<td>{hp:.2f}</td>",
                    f"<td><div class='bar-wrap'><div class='bar' style='width:{width}%'></div></div></td>",
                    "</tr>",
                ]
            )
        )

    return (
        "<table><thead><tr><th>Session</th><th>Avg HP</th><th>Relative</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _fail_table(fail_trend: list[dict[str, Any]]) -> str:
    if not fail_trend:
        return "<p class='muted'>No fail-state data.</p>"

    rows = []
    for item in fail_trend:
        session_id = escape(str(item.get("session_id", "unknown")))
        defeated = int(item.get("defeated_members", 0) or 0)
        size = int(item.get("party_size", 0) or 0)
        ratio = float(item.get("fail_state_ratio", 0) or 0)
        tpk = bool(item.get("tpk", False))
        stalled = int(item.get("stalled_turns_estimate", 0) or 0)
        rows.append(
            "".join(
                [
                    "<tr>",
                    f"<td>{session_id}</td>",
                    f"<td>{defeated}/{size}</td>",
                    f"<td>{ratio:.3f}</td>",
                    f"<td>{'Yes' if tpk else 'No'}</td>",
                    f"<td>{stalled}</td>",
                    "</tr>",
                ]
            )
        )

    return (
        "<table><thead><tr><th>Session</th><th>Defeated</th><th>Fail Ratio</th><th>TPK</th><th>Stalled Est.</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _risk_table(risks: list[dict[str, Any]]) -> str:
    if not risks:
        return "<p class='muted'>No recurring risk flags yet.</p>"

    rows = []
    for item in risks:
        label = escape(str(item.get("risk_flag", "unknown")))
        count = int(item.get("count", 0) or 0)
        rows.append(f"<tr><td>{label}</td><td>{count}</td></tr>")

    return "<table><thead><tr><th>Risk Flag</th><th>Count</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
