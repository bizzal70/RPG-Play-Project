from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .ledger import ensure_ledger, load_manifest


def build_campaign_dashboard(
    campaign_id: str,
    ledger_dir: str | Path = "data/ledger",
    weekly_outputs_root: str | Path = "outputs/weekly",
) -> dict[str, Any]:
    paths = ensure_ledger(ledger_dir, campaign_id)
    manifest = load_manifest(paths)
    sessions_meta = manifest.get("sessions", [])

    sessions: list[dict[str, Any]] = []
    for meta in sessions_meta:
        path = meta.get("path")
        if not isinstance(path, str):
            continue
        payload_path = Path(path)
        if not payload_path.is_absolute():
            payload_path = Path.cwd() / payload_path
        if not payload_path.exists():
            continue

        with payload_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        sessions.append(payload)

    hp_trend: list[dict[str, Any]] = []
    fail_state_trend: list[dict[str, Any]] = []
    tpk_count = 0
    clue_count = 0
    stalled_turns_total = 0

    for session in sessions:
        session_id = session.get("session_id", "unknown")
        result = session.get("result", {})
        final_state = result.get("final_state", {})
        party = final_state.get("party", []) if isinstance(final_state, dict) else []
        log = final_state.get("log", []) if isinstance(final_state, dict) else []

        hp_values = [member.get("hp", 0) for member in party if isinstance(member, dict)]
        party_size = len(hp_values)
        avg_hp = round(sum(hp_values) / max(1, party_size), 2)
        defeated = sum(1 for hp in hp_values if hp <= 0)
        fail_ratio = round(defeated / max(1, party_size), 3)

        flags = final_state.get("flags", {}) if isinstance(final_state, dict) else {}
        clue_discovered = bool(flags.get("latest_discovery"))
        clue_count += 1 if clue_discovered else 0

        tpk = party_size > 0 and defeated == party_size
        tpk_count += 1 if tpk else 0

        session_stalled_turns = _estimate_stalled_turns(log if isinstance(log, list) else [])
        stalled_turns_total += session_stalled_turns

        hp_trend.append({
            "session_id": session_id,
            "avg_final_party_hp": avg_hp,
        })
        fail_state_trend.append({
            "session_id": session_id,
            "defeated_members": defeated,
            "party_size": party_size,
            "fail_state_ratio": fail_ratio,
            "tpk": tpk,
            "stalled_turns_estimate": session_stalled_turns,
        })

    risk_flags = _collect_risk_flags(campaign_id=campaign_id, weekly_outputs_root=weekly_outputs_root)
    party_panel = _build_party_panel(sessions)

    session_count = len(sessions)
    dashboard = {
        "campaign_id": campaign_id,
        "session_count": session_count,
        "summary": {
            "tpk_rate": round(tpk_count / max(1, session_count), 3),
            "clue_discovery_rate": round(clue_count / max(1, session_count), 3),
            "avg_stalled_turns_estimate": round(stalled_turns_total / max(1, session_count), 2),
        },
        "trends": {
            "party_hp": hp_trend,
            "fail_state": fail_state_trend,
            "recurring_risk_flags": risk_flags,
        },
        "panels": {
            "party": party_panel,
        },
        "manifest_path": str(paths["manifest"]),
    }

    dashboard_path = paths["root"] / "dashboard.json"
    with dashboard_path.open("w", encoding="utf-8") as file:
        json.dump(dashboard, file, ensure_ascii=False, indent=2)

    dashboard["dashboard_path"] = str(dashboard_path)
    return dashboard


def _estimate_stalled_turns(log_entries: list[str]) -> int:
    stalled = 0
    for entry in log_entries:
        lower = entry.lower()
        if "finds nothing useful" in lower or "fails to persuade" in lower:
            stalled += 1
    return stalled


def _collect_risk_flags(campaign_id: str, weekly_outputs_root: str | Path) -> list[dict[str, Any]]:
    root = Path(weekly_outputs_root) / campaign_id
    if not root.exists():
        return []

    counter: Counter[str] = Counter()
    report_files = sorted(root.glob("session_*/session_*_weekly_report.md"))
    for report_file in report_files:
        text = report_file.read_text(encoding="utf-8", errors="ignore")
        flags = _extract_risk_flags_from_report(text)
        counter.update(flags)

    return [
        {"risk_flag": flag, "count": count}
        for flag, count in counter.most_common(20)
    ]


def _extract_risk_flags_from_report(text: str) -> list[str]:
    lines = text.splitlines()
    capture = False
    flags: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "## Risk Flags":
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped.startswith("- "):
            flags.append(stripped[2:].strip())
    return [flag for flag in flags if flag]


def _build_party_panel(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    if not sessions:
        return {
            "latest_session_id": None,
            "members": [],
        }

    latest = sessions[-1]
    latest_session_id = latest.get("session_id", "unknown")
    result = latest.get("result", {}) if isinstance(latest, dict) else {}
    final_state = result.get("final_state", {}) if isinstance(result, dict) else {}
    party = final_state.get("party", []) if isinstance(final_state, dict) else []

    members: list[dict[str, Any]] = []
    for member in party:
        if not isinstance(member, dict):
            continue

        hp = int(member.get("hp", 0) or 0)
        status = "active" if hp > 0 else "down"
        members.append(
            {
                "name": member.get("name", "Unknown"),
                "level": member.get("level"),
                "class": member.get("char_class") or "unknown-class",
                "role": member.get("role") or "adventurer",
                "hp": hp,
                "status": status,
            }
        )

    return {
        "latest_session_id": latest_session_id,
        "members": members,
    }
