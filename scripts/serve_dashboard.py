from __future__ import annotations

import argparse
import http.server
import json
import socket
import socketserver
import sys
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve campaign dashboard HTML over localhost")
    parser.add_argument("--campaign-id", default="strahd_weekly", help="Campaign id under ledger dir")
    parser.add_argument("--ledger-dir", default="data/ledger", help="Ledger root containing dashboard.html")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind")
    parser.add_argument("--auto-port", action="store_true", help="Find and use the next available port if requested one is busy")
    parser.add_argument("--open-browser", action=argparse.BooleanOptionalAction, default=True, help="Open browser automatically")
    parser.add_argument("--dry-run", action="store_true", help="Print target URL and exit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    dashboard_dir = (Path(args.ledger_dir) / args.campaign_id).resolve()
    dashboard_html = dashboard_dir / "dashboard.html"
    if not dashboard_html.exists():
        raise SystemExit(
            f"Dashboard HTML not found: {dashboard_html}\n"
            "Run: python scripts/build_campaign_dashboard.py --campaign-id <id>"
        )

    port = _resolve_port(args.host, args.port, args.auto_port)
    url = f"http://{args.host}:{port}/dashboard.html"
    payload = {
        "campaign_id": args.campaign_id,
        "dashboard_dir": str(dashboard_dir),
        "dashboard_html": str(dashboard_html),
        "port": port,
        "url": url,
    }

    if args.dry_run:
        print(json.dumps({"dry_run": True, **payload}, indent=2))
        return

    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(dashboard_dir), **kw)

    try:
        server = socketserver.TCPServer((args.host, port), handler)
    except OSError as error:
        raise SystemExit(
            f"Could not bind to {args.host}:{port} ({error}). "
            "Try a different --port or add --auto-port."
        )

    with server:
        print(json.dumps({"serving": True, **payload}, indent=2))
        if args.open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def _resolve_port(host: str, port: int, auto_port: bool) -> int:
    if not auto_port:
        return port

    candidate = port
    for _ in range(200):
        if _is_port_available(host, candidate):
            return candidate
        candidate += 1

    raise SystemExit(f"Unable to find an open port starting at {port}")


def _is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex((host, port)) != 0


if __name__ == "__main__":
    main()
