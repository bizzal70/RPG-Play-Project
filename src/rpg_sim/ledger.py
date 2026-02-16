from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import CampaignState, SessionResult


def build_ledger_paths(ledger_dir: str | Path, campaign_id: str) -> dict[str, Path]:
    root = Path(ledger_dir) / campaign_id
    sessions = root / "sessions"
    manifest = root / "manifest.json"
    latest_state = root / "latest_state.json"
    return {
        "root": root,
        "sessions": sessions,
        "manifest": manifest,
        "latest_state": latest_state,
    }


def ensure_ledger(ledger_dir: str | Path, campaign_id: str) -> dict[str, Path]:
    paths = build_ledger_paths(ledger_dir, campaign_id)
    paths["root"].mkdir(parents=True, exist_ok=True)
    paths["sessions"].mkdir(parents=True, exist_ok=True)

    if not paths["manifest"].exists():
        manifest = {
            "campaign_id": campaign_id,
            "created_at": _utc_now(),
            "session_count": 0,
            "sessions": [],
        }
        _write_json(paths["manifest"], manifest)

    return paths


def load_manifest(paths: dict[str, Path]) -> dict[str, Any]:
    return _read_json(paths["manifest"])


def has_latest_state(paths: dict[str, Path]) -> bool:
    return paths["latest_state"].exists()


def save_latest_state(paths: dict[str, Path], state_payload: dict[str, Any]) -> None:
    _write_json(paths["latest_state"], state_payload)


def load_latest_state_payload(paths: dict[str, Path]) -> dict[str, Any]:
    return _read_json(paths["latest_state"])


def record_session(
    paths: dict[str, Path],
    result: SessionResult,
    run_seed: int,
    turns: int,
    source_profile: str,
) -> dict[str, Any]:
    manifest = load_manifest(paths)
    next_index = int(manifest.get("session_count", 0)) + 1
    session_id = f"session_{next_index:04d}"

    session_payload = {
        "session_id": session_id,
        "created_at": _utc_now(),
        "seed": run_seed,
        "turns": turns,
        "source_profile": source_profile,
        "result": result.to_dict(),
    }

    session_path = paths["sessions"] / f"{session_id}.json"
    _write_json(session_path, session_payload)
    save_latest_state(paths, result.to_dict()["final_state"])

    manifest.setdefault("sessions", []).append(
        {
            "session_id": session_id,
            "created_at": session_payload["created_at"],
            "seed": run_seed,
            "turns": turns,
            "source_profile": source_profile,
            "path": str(session_path),
        }
    )
    manifest["session_count"] = next_index
    manifest["updated_at"] = _utc_now()
    _write_json(paths["manifest"], manifest)

    return {
        "session_id": session_id,
        "path": str(session_path),
    }


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()