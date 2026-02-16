from __future__ import annotations

import random

from .interfaces import BaseActor, BaseDirector
from .models import ActionIntent, CampaignState, Scene


class SimpleDirector(BaseDirector):
    def __init__(self, source_chunks: list[str] | None = None, random_seed: int = 42) -> None:
        self.source_chunks = source_chunks or []
        self.random = random.Random(random_seed)

    def build_scene(self, campaign: CampaignState) -> Scene:
        if campaign.encounters:
            encounter = campaign.encounters[(campaign.turn_index - 1) % len(campaign.encounters)]
            prompt = (
                f"{campaign.chapter}: {encounter.title}. "
                f"Threat {encounter.threat}. {encounter.description}"
            )
        else:
            prompt = f"{campaign.chapter}: A quiet moment with uncertain tension."

        if self.source_chunks:
            excerpt = self.random.choice(self.source_chunks)[:240]
            prompt = f"{prompt} Source excerpt: {excerpt}"

        options = ["attack", "defend", "investigate", "negotiate", "rest"]
        return Scene(prompt=prompt, options=options)


class HeuristicActor(BaseActor):
    def choose_action(self, campaign: CampaignState, scene: Scene, actor_name: str) -> ActionIntent:
        actor = next(member for member in campaign.party if member.name == actor_name)
        if actor.hp <= 3 and "rest" in scene.options:
            return ActionIntent(actor_name=actor_name, action="rest")

        if campaign.flags.get("latest_discovery") in (None, "") and "investigate" in scene.options:
            return ActionIntent(actor_name=actor_name, action="investigate")

        if "attack" in scene.options:
            return ActionIntent(actor_name=actor_name, action="attack")

        return ActionIntent(actor_name=actor_name, action=scene.options[0])


class LLMActorAdapter(BaseActor):
    def __init__(self, callable_client) -> None:
        self.client = callable_client

    def choose_action(self, campaign: CampaignState, scene: Scene, actor_name: str) -> ActionIntent:
        payload = {
            "actor_name": actor_name,
            "scene": scene.prompt,
            "allowed_actions": scene.options,
            "party_hp": {member.name: member.hp for member in campaign.party},
            "flags": campaign.flags,
        }

        response = self.client(payload)
        action = response.get("action", "defend")
        target = response.get("target")
        return ActionIntent(actor_name=actor_name, action=action, target=target)