from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .interfaces import BaseDirector
from .models import ActionIntent, ActionOutcome, CampaignState, Scene
from .rules.generic import GenericD20Ruleset


@dataclass
class SRDContent:
    source_path: str
    version: str
    categories: list[str]
    conditions: list[str]
    equipment_names: list[str]
    background_names: list[str]
    weapon_property_names: list[str]
    mastery_property_names: list[str]
    damage_types: list[str]

    @property
    def summary(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "version": self.version,
            "categories": len(self.categories),
            "conditions": len(self.conditions),
            "equipment": len(self.equipment_names),
            "backgrounds": len(self.background_names),
            "weapon_properties": len(self.weapon_property_names),
            "mastery_properties": len(self.mastery_property_names),
            "damage_types": len(self.damage_types),
        }


def load_srd_content(path: str | Path) -> SRDContent:
    resolved = Path(path)
    with resolved.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    files = payload.get("files", {})
    categories = sorted(files.keys())

    conditions = _extract_name_list(files.get("5e-SRD-Conditions.json", []))
    equipment_names = _extract_name_list(files.get("5e-SRD-Equipment.json", []))
    background_names = _extract_name_list(files.get("5e-SRD-Backgrounds.json", []))
    weapon_property_names = _extract_name_list(files.get("5e-SRD-Weapon-Properties.json", []))
    mastery_property_names = _extract_name_list(files.get("5e-SRD-Weapon-Mastery-Properties.json", []))
    damage_types = _extract_name_list(files.get("5e-SRD-Damage-Types.json", []))

    return SRDContent(
        source_path=str(resolved),
        version=str(payload.get("version", "unknown")),
        categories=categories,
        conditions=conditions,
        equipment_names=equipment_names,
        background_names=background_names,
        weapon_property_names=weapon_property_names,
        mastery_property_names=mastery_property_names,
        damage_types=damage_types,
    )


def _extract_name_list(items: list[dict[str, Any]] | Any) -> list[str]:
    if not isinstance(items, list):
        return []
    names = [item.get("name", "") for item in items if isinstance(item, dict)]
    return [name for name in names if name]


class SRD2024Director(BaseDirector):
    def __init__(self, srd: SRDContent, random_seed: int = 42, source_chunks: list[str] | None = None) -> None:
        self.srd = srd
        self.random = random.Random(random_seed)
        self.source_chunks = source_chunks or []

    def build_scene(self, campaign: CampaignState) -> Scene:
        if campaign.encounters:
            encounter = campaign.encounters[(campaign.turn_index - 1) % len(campaign.encounters)]
            base_prompt = (
                f"{campaign.chapter}: {encounter.title}. "
                f"Threat {encounter.threat}. {encounter.description}"
            )
        else:
            base_prompt = f"{campaign.chapter}: A quiet moment with uncertain tension."

        condition = self._pick(self.srd.conditions)
        equipment = self._pick(self.srd.equipment_names)
        background = self._pick(self.srd.background_names)
        mastery = self._pick(self.srd.mastery_property_names)

        srd_flavor = (
            f"SRD context: condition={condition}, useful_equipment={equipment}, "
            f"background_hook={background}, mastery_angle={mastery}."
        )
        source_flavor = ""
        if self.source_chunks:
            excerpt = self.random.choice(self.source_chunks)[:240]
            source_flavor = f" Source excerpt: {excerpt}"

        options = [
            "attack",
            "defend",
            "investigate",
            "negotiate",
            "rest",
            "use-equipment",
            "exploit-mastery",
        ]
        return Scene(prompt=f"{base_prompt} {srd_flavor}{source_flavor}", options=options)

    def _pick(self, items: list[str]) -> str:
        return self.random.choice(items) if items else "none"


class SRD2024Ruleset(GenericD20Ruleset):
    def __init__(self, srd: SRDContent, random_seed: int = 42) -> None:
        super().__init__(random_seed=random_seed)
        self.srd = srd

    def validate_intent(self, campaign: CampaignState, intent: ActionIntent) -> bool:
        allowed = {
            "attack",
            "defend",
            "investigate",
            "negotiate",
            "rest",
            "use-equipment",
            "exploit-mastery",
        }
        return intent.action in allowed

    def resolve_intent(self, campaign: CampaignState, intent: ActionIntent) -> ActionOutcome:
        if intent.action == "use-equipment":
            roll = self.random.randint(1, 20)
            item = self.random.choice(self.srd.equipment_names) if self.srd.equipment_names else "gear"
            success = roll >= 9
            summary = (
                f"{intent.actor_name} uses {item} effectively (roll={roll})"
                if success
                else f"{intent.actor_name} fumbles {item} under pressure (roll={roll})"
            )
            return ActionOutcome(
                actor_name=intent.actor_name,
                success=success,
                summary=summary,
                hp_delta={intent.actor_name: 0 if success else -1},
            )

        if intent.action == "exploit-mastery":
            roll = self.random.randint(1, 20)
            mastery = self.random.choice(self.srd.mastery_property_names) if self.srd.mastery_property_names else "mastery"
            success = roll >= 11
            summary = (
                f"{intent.actor_name} applies {mastery} mastery to gain momentum (roll={roll})"
                if success
                else f"{intent.actor_name} fails to trigger {mastery} mastery (roll={roll})"
            )
            return ActionOutcome(
                actor_name=intent.actor_name,
                success=success,
                summary=summary,
                flag_updates={"latest_mastery": mastery} if success else {},
            )

        return super().resolve_intent(campaign, intent)