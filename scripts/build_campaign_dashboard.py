from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rpg_sim.dashboard import build_campaign_dashboard
from src.rpg_sim.dashboard_view import render_dashboard_html


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build campaign dashboard JSON from ledger + weekly reports")
    parser.add_argument("--campaign-id", required=True, help="Campaign id in ledger")
    parser.add_argument("--ledger-dir", default="data/ledger", help="Ledger root")
    parser.add_argument("--weekly-outputs-root", default="outputs/weekly", help="Weekly outputs root for report parsing")
    parser.add_argument("--html", action=argparse.BooleanOptionalAction, default=True, help="Also build dashboard HTML view")
    parser.add_argument("--html-out", default="", help="Optional custom output path for dashboard HTML")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dashboard = build_campaign_dashboard(
        campaign_id=args.campaign_id,
        ledger_dir=args.ledger_dir,
        weekly_outputs_root=args.weekly_outputs_root,
    )

    html_path = None
    if args.html:
        if args.html_out:
            html_path = render_dashboard_html(dashboard, args.html_out)
        else:
            default_html = Path(args.ledger_dir) / args.campaign_id / "dashboard.html"
            html_path = render_dashboard_html(dashboard, default_html)

    payload = dict(dashboard)
    payload["dashboard_html_path"] = html_path
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
