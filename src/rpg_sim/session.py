from __future__ import annotations

from .interfaces import BaseActor, BaseDirector, BaseRuleset
from .models import CampaignState, SessionResult, TurnResult


class SessionEngine:
    def __init__(self, ruleset: BaseRuleset, director: BaseDirector, actor: BaseActor) -> None:
        self.ruleset = ruleset
        self.director = director
        self.actor = actor

    def run(self, campaign: CampaignState, max_turns: int) -> SessionResult:
        turn_results: list[TurnResult] = []

        for turn_number in range(1, max_turns + 1):
            campaign.turn_index = turn_number
            scene = self.director.build_scene(campaign)

            intents = []
            outcomes = []
            for character in campaign.party:
                if character.hp <= 0:
                    continue

                intent = self.actor.choose_action(campaign, scene, character.name)
                if not self.ruleset.validate_intent(campaign, intent):
                    campaign.log.append(f"Turn {turn_number}: {character.name} submitted invalid action")
                    continue

                outcome = self.ruleset.resolve_intent(campaign, intent)
                self._apply_outcome(campaign, outcome)

                intents.append(intent)
                outcomes.append(outcome)
                campaign.log.append(f"Turn {turn_number}: {outcome.summary}")

            turn_results.append(
                TurnResult(
                    turn_index=turn_number,
                    scene_prompt=scene.prompt,
                    intents=intents,
                    outcomes=outcomes,
                )
            )

            if self._all_party_defeated(campaign):
                campaign.log.append("Session ended: all party members defeated")
                break

        return SessionResult(
            setting_name=campaign.setting_name,
            total_turns=campaign.turn_index,
            final_state=campaign,
            turns=turn_results,
        )

    @staticmethod
    def _apply_outcome(campaign: CampaignState, outcome) -> None:
        for name, hp_change in outcome.hp_delta.items():
            for member in campaign.party:
                if member.name == name:
                    member.hp = max(0, member.hp + hp_change)

        campaign.flags.update(outcome.flag_updates)

    @staticmethod
    def _all_party_defeated(campaign: CampaignState) -> bool:
        return all(member.hp <= 0 for member in campaign.party)