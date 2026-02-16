from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_SOURCE_PROFILES: dict[str, dict[str, Any]] = {
    "none": {},
    "srd": {
        "campaign_json": "data/campaign_template.json",
        "use_srd": True,
        "srd_json": "data/srd/srd_5e_2024_merged.json",
        "use_source_chunks": False,
    },
    "cos": {
        "campaign_json": "data/campaign_cos.json",
        "campaign_id": "strahd_weekly",
        "party_json": "data/parties/party_cos_survival.json",
        "ai_policy_json": "data/policies/cos_policy.json",
        "use_srd": True,
        "srd_json": "data/srd/srd_5e_2024_merged.json",
        "use_source_chunks": True,
        "source_chunks_json": "data/sources/curse_of_strahd_chunks.json",
    },
    "lmop": {
        "campaign_json": "data/campaign_lmop.json",
        "campaign_id": "lmop_weekly",
        "ai_policy_json": "data/policies/lmop_policy.json",
        "use_srd": True,
        "srd_json": "data/srd/srd_5e_2024_merged.json",
        "use_source_chunks": False,
        "source_chunks_json": "data/sources/lost_mine_of_phandelver_chunks.json",
    },
}


def load_source_profiles(path: str | Path) -> dict[str, dict[str, Any]]:
    profiles = dict(DEFAULT_SOURCE_PROFILES)
    source = Path(path)
    if not source.exists():
        return profiles

    with source.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        return profiles

    for key, value in payload.items():
        if isinstance(key, str) and isinstance(value, dict):
            profiles[key] = value
    return profiles


def save_source_profiles(path: str | Path, profiles: dict[str, dict[str, Any]]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as file:
        json.dump(profiles, file, ensure_ascii=False, indent=2)