from __future__ import annotations

import random

from ..interfaces import BaseRuleset
from ..models import ActionIntent, ActionOutcome, CampaignState


class GenericD20Ruleset(BaseRuleset):
    def __init__(self, random_seed: int = 42) -> None:
        self.random = random.Random(random_seed)

    def validate_intent(self, campaign: CampaignState, intent: ActionIntent) -> bool:
        allowed = {"attack", "defend", "investigate", "negotiate", "rest"}
        return intent.action in allowed

    def resolve_intent(self, campaign: CampaignState, intent: ActionIntent) -> ActionOutcome:
        roll = self.random.randint(1, 20)
        success_threshold = 10

        if intent.action == "attack":
            success = roll >= success_threshold
            hp_delta = {intent.actor_name: -1 if not success else 0}
            summary = (
                f"{intent.actor_name} attacks and lands a hit (roll={roll})"
                if success
                else f"{intent.actor_name} misses and takes strain (roll={roll})"
            )
            return ActionOutcome(
                actor_name=intent.actor_name,
                success=success,
                summary=summary,
                hp_delta=hp_delta,
            )

        if intent.action == "defend":
            success = roll >= 8
            summary = (
                f"{intent.actor_name} fortifies position (roll={roll})"
                if success
                else f"{intent.actor_name} fails to brace in time (roll={roll})"
            )
            return ActionOutcome(actor_name=intent.actor_name, success=success, summary=summary)

        if intent.action == "investigate":
            success = roll >= 11
            discovered = "clue_discovered" if success else ""
            summary = (
                f"{intent.actor_name} uncovers a clue (roll={roll})"
                if success
                else f"{intent.actor_name} finds nothing useful (roll={roll})"
            )
            return ActionOutcome(
                actor_name=intent.actor_name,
                success=success,
                summary=summary,
                flag_updates={"latest_discovery": discovered} if discovered else {},
            )

        if intent.action == "negotiate":
            success = roll >= 12
            summary = (
                f"{intent.actor_name} secures a favorable bargain (roll={roll})"
                if success
                else f"{intent.actor_name} fails to persuade (roll={roll})"
            )
            return ActionOutcome(actor_name=intent.actor_name, success=success, summary=summary)

        success = True
        summary = f"{intent.actor_name} takes a breath and recovers (roll={roll})"
        return ActionOutcome(
            actor_name=intent.actor_name,
            success=success,
            summary=summary,
            hp_delta={intent.actor_name: +1},
        )