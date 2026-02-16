from __future__ import annotations

import json
import os
import random
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .interfaces import BaseActor, BaseDirector
from .models import ActionIntent, CampaignState, Character, Scene


def load_policy_profile(path: str) -> dict[str, Any]:
    policy_path = Path(path)
    if not policy_path.exists():
        return {"campaign": {}, "default": {}, "characters": {}}

    with policy_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    default = payload.get("default", {})
    characters = payload.get("characters", {})
    campaign = payload.get("campaign", {})
    if not isinstance(campaign, dict):
        campaign = {}
    if not isinstance(default, dict):
        default = {}
    if not isinstance(characters, dict):
        characters = {}
    return {"campaign": campaign, "default": default, "characters": characters}


class AIDirector(BaseDirector):
    def __init__(
        self,
        fallback_director: BaseDirector,
        use_ai: bool = False,
        model: str = "gpt-4o-mini",
        api_key_env: str = "OPENAI_API_KEY",
        timeout_seconds: int = 30,
        director_guidance: str = "",
    ) -> None:
        self.fallback_director = fallback_director
        self.use_ai = use_ai
        self.model = model
        self.api_key_env = api_key_env
        self.timeout_seconds = timeout_seconds
        self.director_guidance = director_guidance

    def build_scene(self, campaign: CampaignState) -> Scene:
        fallback_scene = self.fallback_director.build_scene(campaign)
        api_key = os.environ.get(self.api_key_env, "")
        if not self.use_ai or not api_key:
            return self._apply_fallback_guidance(fallback_scene)

        response = _call_openai_json(
            api_key=api_key,
            model=self.model,
            timeout_seconds=self.timeout_seconds,
            system_prompt=(
                "You are an RPG game master. Return strict JSON with keys 'prompt' and 'options'. "
                "'prompt' must be a concise scene setup. 'options' must be an array of valid short action tokens."
                + (f" Guidance: {self.director_guidance}" if self.director_guidance else "")
            ),
            user_payload={
                "setting": campaign.setting_name,
                "chapter": campaign.chapter,
                "turn_index": campaign.turn_index,
                "party": [
                    {
                        "name": member.name,
                        "hp": member.hp,
                        "role": member.role,
                        "class": member.char_class,
                        "goal": member.goal,
                    }
                    for member in campaign.party
                ],
                "flags": campaign.flags,
                "recent_log": campaign.log[-6:],
                "fallback_scene": {
                    "prompt": fallback_scene.prompt,
                    "options": fallback_scene.options,
                },
            },
        )

        if not isinstance(response, dict):
            return fallback_scene

        prompt = response.get("prompt")
        options = response.get("options")
        if not isinstance(prompt, str) or not prompt.strip():
            prompt = fallback_scene.prompt

        cleaned_options = _clean_options(options)
        if cleaned_options:
            allowed = set(fallback_scene.options)
            cleaned_options = [option for option in cleaned_options if option in allowed]
        if not cleaned_options:
            cleaned_options = fallback_scene.options

        return Scene(prompt=prompt.strip(), options=cleaned_options)

    def _apply_fallback_guidance(self, scene: Scene) -> Scene:
        guidance = self.director_guidance.strip()
        if not guidance:
            return scene
        prompt = f"{scene.prompt} Tone cue: {guidance}"
        return Scene(prompt=prompt, options=scene.options)


class PolicyDrivenActor(BaseActor):
    def __init__(
        self,
        policy_profile: dict[str, Any] | None = None,
        use_ai: bool = False,
        model: str = "gpt-4o-mini",
        api_key_env: str = "OPENAI_API_KEY",
        random_seed: int = 42,
        timeout_seconds: int = 30,
        actor_guidance: str = "",
    ) -> None:
        self.policy_profile = policy_profile or {"campaign": {}, "default": {}, "characters": {}}
        self.use_ai = use_ai
        self.model = model
        self.api_key_env = api_key_env
        self.random = random.Random(random_seed)
        self.timeout_seconds = timeout_seconds
        self.actor_guidance = actor_guidance

    def choose_action(self, campaign: CampaignState, scene: Scene, actor_name: str) -> ActionIntent:
        actor = next(member for member in campaign.party if member.name == actor_name)
        policy = self._resolve_policy(actor_name)
        campaign_policy = self._campaign_policy()

        deterministic_choice = self._choose_from_policy(campaign, scene, actor, policy)

        api_key = os.environ.get(self.api_key_env, "")
        if not self.use_ai or not api_key:
            return ActionIntent(actor_name=actor_name, action=deterministic_choice)

        response = _call_openai_json(
            api_key=api_key,
            model=self.model,
            timeout_seconds=self.timeout_seconds,
            system_prompt=(
                "You are controlling one player character in a tabletop RPG simulation. "
                "Return strict JSON with keys 'action' and optional 'target'. "
                "Action must be one of the provided allowed_actions."
                + (f" Guidance: {self.actor_guidance}" if self.actor_guidance else "")
            ),
            user_payload={
                "actor": {
                    "name": actor.name,
                    "hp": actor.hp,
                    "stats": actor.stats,
                    "role": actor.role,
                    "class": actor.char_class,
                    "background": actor.background,
                    "personality": actor.personality,
                    "goal": actor.goal,
                    "flaw": actor.flaw,
                },
                "policy": policy,
                "campaign_policy": campaign_policy,
                "scene": scene.prompt,
                "allowed_actions": scene.options,
                "party_hp": {member.name: member.hp for member in campaign.party},
                "flags": campaign.flags,
                "recent_log": campaign.log[-4:],
                "fallback_action": deterministic_choice,
            },
        )

        if not isinstance(response, dict):
            return ActionIntent(actor_name=actor_name, action=deterministic_choice)

        action = response.get("action")
        target = response.get("target")
        if not isinstance(action, str) or action not in scene.options:
            action = deterministic_choice
        if not isinstance(target, str):
            target = None

        return ActionIntent(actor_name=actor_name, action=action, target=target)

    def _resolve_policy(self, actor_name: str) -> dict[str, Any]:
        base = dict(self.policy_profile.get("default", {}))
        character_overrides = self.policy_profile.get("characters", {}).get(actor_name, {})
        if isinstance(character_overrides, dict):
            merged = dict(base)
            for key, value in character_overrides.items():
                if key == "priorities" and isinstance(value, dict):
                    priorities = dict(base.get("priorities", {}))
                    priorities.update(value)
                    merged[key] = priorities
                else:
                    merged[key] = value
            return merged
        return base

    def _campaign_policy(self) -> dict[str, Any]:
        campaign = self.policy_profile.get("campaign", {})
        return campaign if isinstance(campaign, dict) else {}

    def _choose_from_policy(
        self,
        campaign: CampaignState,
        scene: Scene,
        actor: Character,
        policy: dict[str, Any],
    ) -> str:
        scores: dict[str, float] = {option: 1.0 for option in scene.options}
        priorities = policy.get("priorities", {})
        if isinstance(priorities, dict):
            for option, value in priorities.items():
                if option in scores and isinstance(value, (int, float)):
                    scores[option] += float(value)

        caution = _as_float(policy.get("caution"), default=0.5)
        aggression = _as_float(policy.get("aggression"), default=0.5)
        exploration = _as_float(policy.get("exploration"), default=0.5)

        if actor.hp <= 3:
            if "rest" in scores:
                scores["rest"] += 2.5 + caution
            if "defend" in scores:
                scores["defend"] += 1.5 + caution
            if "attack" in scores:
                scores["attack"] -= 1.0

        if campaign.flags.get("latest_discovery") in (None, "") and "investigate" in scores:
            scores["investigate"] += 1.5 + exploration

        role_text = f"{actor.role} {actor.personality}".lower()
        class_text = actor.char_class.lower()

        if "negotiate" in scores and any(token in role_text for token in ["face", "diplomat", "charisma"]):
            scores["negotiate"] += 1.2
        if "attack" in scores and any(token in class_text for token in ["fighter", "barbarian", "paladin", "ranger"]):
            scores["attack"] += 1.2 + aggression
        if "investigate" in scores and any(token in class_text for token in ["wizard", "cleric", "rogue", "bard"]):
            scores["investigate"] += 1.0 + exploration
        if "exploit-mastery" in scores and any(token in class_text for token in ["fighter", "barbarian", "ranger"]):
            scores["exploit-mastery"] += 1.0 + aggression
        if "use-equipment" in scores and actor.background:
            scores["use-equipment"] += 0.6

        campaign_policy = self._campaign_policy()
        preferred_actions = campaign_policy.get("preferred_actions", [])
        if isinstance(preferred_actions, list):
            for action in preferred_actions:
                if isinstance(action, str) and action in scores:
                    scores[action] += 0.35

        avoid_actions = campaign_policy.get("avoid_actions", [])
        if isinstance(avoid_actions, list):
            for action in avoid_actions:
                if isinstance(action, str) and action in scores:
                    scores[action] -= 0.45

        best_score = max(scores.values())
        best_actions = [option for option, score in scores.items() if score == best_score]
        if len(best_actions) == 1:
            return best_actions[0]

        tie_breaker = policy.get("tie_breaker", [])
        if isinstance(tie_breaker, list):
            for preferred in tie_breaker:
                if isinstance(preferred, str) and preferred in best_actions:
                    return preferred

        ordered = [option for option in scene.options if option in best_actions]
        if ordered:
            return ordered[self.random.randrange(0, len(ordered))]
        return scene.options[0]


def _clean_options(raw_options: Any) -> list[str]:
    if not isinstance(raw_options, list):
        return []
    cleaned: list[str] = []
    for option in raw_options:
        if not isinstance(option, str):
            continue
        token = option.strip()
        if token and token not in cleaned:
            cleaned.append(token)
    return cleaned[:8]


def _as_float(value: Any, default: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


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
        "temperature": 0.5,
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