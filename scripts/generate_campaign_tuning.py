from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rpg_sim.campaign_loader import load_campaign_from_json, load_party_from_json
from src.rpg_sim.source_profiles import load_source_profiles, save_source_profiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate campaign-specific AI tuning (theme/tone policy + prompt guidance) and optionally bind it to a source profile"
    )
    parser.add_argument("--source-profile", required=True, help="Source profile to tune (for example: cos)")
    parser.add_argument("--source-profiles-json", default="data/source_profiles.json", help="Path to source profiles JSON")
    parser.add_argument("--campaign-json", default="data/campaign_template.json", help="Campaign JSON path (profile campaign_json is used when left as default)")
    parser.add_argument("--party-json", default="", help="Optional party JSON override (campaign party is used when omitted)")
    parser.add_argument("--out", default="", help="Output policy JSON path (defaults to data/policies/<profile>_policy.json)")
    parser.add_argument("--preset", default="balanced", choices=["balanced", "aggressive", "cautious", "investigative"], help="Base behavior preset before campaign tone adjustments")
    parser.add_argument("--apply-profile", action="store_true", help="Write generated policy path to profile ai_policy_json")
    parser.add_argument("--ai-model", default="gpt-4o-mini", help="OpenAI model used for campaign AI drafting")
    parser.add_argument("--ai-api-key-env", default="OPENAI_API_KEY", help="Environment variable containing OpenAI API key")
    parser.add_argument("--ai-timeout", type=int, default=30, help="OpenAI request timeout seconds for AI drafting")
    parser.add_argument("--ai-max-chunks", type=int, default=3, help="Max source chunks to include in AI drafting context")
    parser.add_argument("--ai-max-chars", type=int, default=900, help="Max characters per source chunk in AI drafting context")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    profiles = load_source_profiles(args.source_profiles_json)
    profile = profiles.get(args.source_profile)
    if profile is None:
        available = ", ".join(sorted(profiles.keys()))
        raise ValueError(f"Unknown source profile '{args.source_profile}'. Available: {available}")

    active_campaign_json = _resolve_campaign_json(args.campaign_json, profile)
    output_path = Path(args.out) if args.out else Path(f"data/policies/{args.source_profile}_policy.json")

    campaign = load_campaign_from_json(active_campaign_json)
    party = load_party_from_json(args.party_json) if args.party_json else campaign.party

    source_hint = str(profile.get("source_chunks_json", ""))
    theme = _infer_theme(
        source_profile=args.source_profile,
        setting_name=campaign.setting_name,
        chapter=campaign.chapter,
        source_hint=source_hint,
    )

    campaign_block = _campaign_guidance(theme)
    ai_draft = _draft_campaign_guidance_ai(
        profile=profile,
        source_profile=args.source_profile,
        campaign_json=active_campaign_json,
        setting_name=campaign.setting_name,
        chapter=campaign.chapter,
        inferred_theme=theme,
        model=args.ai_model,
        api_key_env=args.ai_api_key_env,
        timeout_seconds=args.ai_timeout,
        max_chunks=args.ai_max_chunks,
        max_chars=args.ai_max_chars,
    )
    campaign_block = _merge_campaign_guidance(campaign_block, ai_draft)

    payload: dict[str, Any] = {
        "campaign": campaign_block,
        "default": _preset_defaults(args.preset),
        "characters": {},
    }

    _apply_theme_to_default(payload["default"], theme)

    for member in party:
        payload["characters"][member.name] = _policy_for_member(member, theme=theme)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.apply_profile:
        updated = dict(profile)
        updated["ai_policy_json"] = str(output_path)
        profiles[args.source_profile] = updated
        save_source_profiles(args.source_profiles_json, profiles)

    print(
        json.dumps(
            {
                "ok": True,
                "source_profile": args.source_profile,
                "campaign_json": active_campaign_json,
                "theme": theme,
                "policy_json": str(output_path),
                "profile_updated": args.apply_profile,
                "ai_draft_applied": True,
                "ai_model": args.ai_model,
            },
            indent=2,
        )
    )


def _resolve_campaign_json(campaign_arg: str, profile: dict[str, Any]) -> str:
    default_campaign_json = "data/campaign_template.json"
    if campaign_arg == default_campaign_json and isinstance(profile.get("campaign_json"), str):
        return str(profile["campaign_json"])
    return campaign_arg


def _infer_theme(source_profile: str, setting_name: str, chapter: str, source_hint: str) -> str:
    text = " ".join([source_profile, setting_name, chapter, source_hint]).lower()
    text = re.sub(r"\s+", " ", text)

    gothic_tokens = ["strahd", "barovia", "ravenloft", "mist", "vampire", "gothic", "horror"]
    if any(token in text for token in gothic_tokens):
        return "gothic_horror"

    if any(token in text for token in ["nautical", "pirate", "sea", "ship"]):
        return "swashbuckling"

    if any(token in text for token in ["abyss", "eldritch", "void", "cosmic"]):
        return "eldritch_horror"

    if any(token in text for token in ["survival", "wilderness", "frozen", "desert"]):
        return "survival"

    return "heroic_fantasy"


def _campaign_guidance(theme: str) -> dict[str, Any]:
    if theme == "gothic_horror":
        return {
            "theme": theme,
            "tone": "dreadful, tragic, oppressive, morally gray",
            "director_guidance": (
                "Maintain gothic horror atmosphere, emphasize dread and consequence, use sensory decay and ominous foreshadowing, "
                "and keep victories costly rather than triumphant."
            ),
            "actor_guidance": (
                "Play cautiously under pressure, protect allies, investigate signs and lore, and avoid reckless heroics unless survival demands it."
            ),
            "preferred_actions": ["investigate", "defend", "use-equipment", "negotiate"],
            "avoid_actions": ["attack"],
        }

    if theme == "swashbuckling":
        return {
            "theme": theme,
            "tone": "bold, kinetic, adventurous",
            "director_guidance": "Favor momentum, daring opportunities, and cinematic reversals.",
            "actor_guidance": "Take initiative and exploit dynamic terrain and social leverage.",
            "preferred_actions": ["attack", "exploit-mastery", "negotiate"],
            "avoid_actions": ["rest"],
        }

    if theme == "eldritch_horror":
        return {
            "theme": theme,
            "tone": "uncanny, unsettling, alien",
            "director_guidance": "Lean into incomprehensible threats and psychological pressure.",
            "actor_guidance": "Gather information first, avoid direct confrontation when uncertain.",
            "preferred_actions": ["investigate", "defend"],
            "avoid_actions": ["attack"],
        }

    if theme == "survival":
        return {
            "theme": theme,
            "tone": "harsh, resource-constrained, pragmatic",
            "director_guidance": "Highlight scarcity, weather, distance, and hard tradeoffs.",
            "actor_guidance": "Conserve resources and favor risk-managed decisions.",
            "preferred_actions": ["defend", "use-equipment", "rest", "investigate"],
            "avoid_actions": ["negotiate"],
        }

    return {
        "theme": "heroic_fantasy",
        "tone": "adventurous, hopeful, dangerous",
        "director_guidance": "Balance danger with momentum and opportunities for heroic action.",
        "actor_guidance": "Pursue objectives proactively while protecting the party.",
        "preferred_actions": ["investigate", "attack", "defend"],
        "avoid_actions": [],
    }


def _merge_campaign_guidance(base: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)

    for key in ["theme", "tone", "director_guidance", "actor_guidance"]:
        value = draft.get(key)
        if isinstance(value, str) and value.strip():
            merged[key] = value.strip()

    preferred = _normalize_action_list(draft.get("preferred_actions"))
    if preferred:
        merged["preferred_actions"] = preferred

    avoid = _normalize_action_list(draft.get("avoid_actions"))
    if avoid:
        merged["avoid_actions"] = avoid

    return merged


def _normalize_action_list(raw: Any) -> list[str]:
    allowed = {"attack", "defend", "investigate", "negotiate", "rest", "use-equipment", "exploit-mastery"}
    if not isinstance(raw, list):
        return []

    cleaned: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        token = item.strip().lower()
        if token in allowed and token not in cleaned:
            cleaned.append(token)
    return cleaned[:6]


def _draft_campaign_guidance_ai(
    profile: dict[str, Any],
    source_profile: str,
    campaign_json: str,
    setting_name: str,
    chapter: str,
    inferred_theme: str,
    model: str,
    api_key_env: str,
    timeout_seconds: int,
    max_chunks: int,
    max_chars: int,
) -> dict[str, Any] | None:
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        raise ValueError(f"Missing API key in env var '{api_key_env}'. AI tuning is required.")

    source_chunks_json = profile.get("source_chunks_json", "")
    snippets = _load_source_snippets(source_chunks_json, max_chunks=max_chunks, max_chars=max_chars)

    response = _call_openai_json(
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
        system_prompt=(
            "You generate campaign tone guidance for tabletop RPG simulation AI. "
            "Return strict JSON with keys: theme, tone, director_guidance, actor_guidance, preferred_actions, avoid_actions. "
            "preferred_actions and avoid_actions must be arrays using only: attack, defend, investigate, negotiate, rest, use-equipment, exploit-mastery. "
            "Keep guidance concise and practical."
        ),
        user_payload={
            "source_profile": source_profile,
            "campaign_json": campaign_json,
            "setting_name": setting_name,
            "chapter": chapter,
            "inferred_theme": inferred_theme,
            "source_snippets": snippets,
        },
    )

    if not isinstance(response, dict):
        raise RuntimeError("OpenAI did not return valid JSON guidance for campaign tuning")

    normalized = _merge_campaign_guidance({}, response)
    if not normalized:
        raise RuntimeError("OpenAI guidance was empty after normalization")
    return normalized


def _load_source_snippets(source_chunks_json: Any, max_chunks: int, max_chars: int) -> list[str]:
    if not isinstance(source_chunks_json, str) or not source_chunks_json:
        return []

    path = Path(source_chunks_json)
    if not path.exists():
        return []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    chunks = payload.get("chunks", []) if isinstance(payload, dict) else []
    if not isinstance(chunks, list):
        return []

    snippets: list[str] = []
    for chunk in chunks[: max(1, max_chunks)]:
        if not isinstance(chunk, dict):
            continue
        text = chunk.get("text", "")
        if not isinstance(text, str):
            continue
        compact = re.sub(r"\s+", " ", text).strip()
        if compact:
            snippets.append(compact[: max(120, max_chars)])
    return snippets


def _call_openai_json(
    api_key: str,
    model: str,
    timeout_seconds: int,
    system_prompt: str,
    user_payload: dict[str, Any],
) -> dict[str, Any] | None:
    request_body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }

    data = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    try:
        content = payload["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return None

    return parsed if isinstance(parsed, dict) else None


def _preset_defaults(preset: str) -> dict[str, Any]:
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


def _apply_theme_to_default(default_policy: dict[str, Any], theme: str) -> None:
    priorities = default_policy.setdefault("priorities", {})
    if not isinstance(priorities, dict):
        priorities = {}
        default_policy["priorities"] = priorities

    if theme == "gothic_horror":
        default_policy["caution"] = min(1.0, float(default_policy.get("caution", 0.5)) + 0.2)
        default_policy["exploration"] = min(1.0, float(default_policy.get("exploration", 0.5)) + 0.2)
        default_policy["aggression"] = max(0.0, float(default_policy.get("aggression", 0.5)) - 0.1)
        priorities["investigate"] = float(priorities.get("investigate", 0.0)) + 0.7
        priorities["defend"] = float(priorities.get("defend", 0.0)) + 0.5
        priorities["attack"] = float(priorities.get("attack", 0.0)) - 0.2
        default_policy["tie_breaker"] = ["investigate", "defend", "use-equipment", "negotiate", "attack", "rest"]


def _policy_for_member(member: Any, theme: str) -> dict[str, Any]:
    role_text = f"{member.role} {member.personality}".lower()
    class_text = member.char_class.lower()

    priorities: dict[str, float] = {}
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

    if any(token in role_text for token in ["tank", "guardian", "protector", "frontliner"]):
        priorities["defend"] = 0.8
        caution = 0.7

    if member.flaw:
        priorities["rest"] = priorities.get("rest", 0.0) + 0.2

    if theme == "gothic_horror":
        caution = min(1.0, caution + 0.1)
        exploration = min(1.0, exploration + 0.1)
        aggression = max(0.0, aggression - 0.1)
        priorities["investigate"] = priorities.get("investigate", 0.0) + 0.4
        priorities["defend"] = priorities.get("defend", 0.0) + 0.3

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
            "theme": theme,
        },
    }


if __name__ == "__main__":
    main()
