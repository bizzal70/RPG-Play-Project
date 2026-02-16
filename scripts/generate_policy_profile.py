from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rpg_sim.campaign_loader import load_party_from_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate per-character AI policy profiles from party JSON")
    parser.add_argument("--party-json", required=True, help="Input party JSON path")
    parser.add_argument("--out", default="data/policies/character_policies.json", help="Output policy JSON path")
    parser.add_argument("--preset", default="balanced", choices=["balanced", "aggressive", "cautious", "investigative"], help="Global default policy preset")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    party = load_party_from_json(args.party_json)
    payload = {
        "default": _preset_defaults(args.preset),
        "characters": {},
    }

    for member in party:
        payload["characters"][member.name] = _policy_for_member(member)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(out_path), "characters": len(party)}, indent=2))


def _preset_defaults(preset: str) -> dict:
    if preset == "aggressive":
        return {
            "aggression": 0.9,
            "caution": 0.2,
            "exploration": 0.4,
            "priorities": {"attack": 1.3, "exploit-mastery": 0.8, "rest": -0.4},
            "tie_breaker": ["attack", "exploit-mastery", "investigate", "defend", "rest"],
        }
    if preset == "cautious":
        return {
            "aggression": 0.2,
            "caution": 0.9,
            "exploration": 0.4,
            "priorities": {"defend": 0.8, "rest": 0.8, "attack": -0.2},
            "tie_breaker": ["defend", "rest", "investigate", "negotiate", "attack"],
        }
    if preset == "investigative":
        return {
            "aggression": 0.4,
            "caution": 0.5,
            "exploration": 1.0,
            "priorities": {"investigate": 1.2, "negotiate": 0.6},
            "tie_breaker": ["investigate", "negotiate", "defend", "attack", "rest"],
        }
    return {
        "aggression": 0.5,
        "caution": 0.5,
        "exploration": 0.6,
        "priorities": {"investigate": 0.5, "attack": 0.3, "defend": 0.2},
        "tie_breaker": ["investigate", "attack", "defend", "negotiate", "rest"],
    }


def _policy_for_member(member) -> dict:
    role_text = f"{member.role} {member.personality}".lower()
    class_text = member.char_class.lower()

    priorities = {}
    tie_breaker = ["attack", "investigate", "defend", "negotiate", "rest"]
    aggression = 0.5
    caution = 0.5
    exploration = 0.5

    if any(token in class_text for token in ["fighter", "barbarian", "paladin", "ranger"]):
        priorities["attack"] = 1.0
        priorities["exploit-mastery"] = 0.8
        aggression = 0.8

    if any(token in class_text for token in ["wizard", "cleric", "rogue", "bard", "druid"]):
        priorities["investigate"] = 0.9
        exploration = 0.8

    if any(token in role_text for token in ["face", "diplomat", "charisma"]):
        priorities["negotiate"] = 1.1
        tie_breaker = ["negotiate", "investigate", "defend", "attack", "rest"]

    if any(token in role_text for token in ["tank", "guardian", "protector"]):
        priorities["defend"] = 0.8
        caution = 0.7

    if member.flaw:
        priorities["rest"] = priorities.get("rest", 0.0) + 0.2

    return {
        "aggression": aggression,
        "caution": caution,
        "exploration": exploration,
        "priorities": priorities,
        "tie_breaker": tie_breaker,
        "notes": {
            "goal": member.goal,
            "flaw": member.flaw,
            "background": member.background,
        },
    }


if __name__ == "__main__":
    main()