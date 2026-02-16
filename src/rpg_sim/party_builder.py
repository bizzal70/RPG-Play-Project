from __future__ import annotations

import json
import random
from dataclasses import asdict
from pathlib import Path

from .models import Character
from .srd import SRDContent

ROLE_TEMPLATES = [
    {"role": "frontliner", "char_class": "Fighter", "hp": 14, "stats": {"might": 4, "grit": 3, "wit": 1}},
    {"role": "divine_support", "char_class": "Cleric", "hp": 12, "stats": {"might": 2, "grit": 3, "wit": 3}},
    {"role": "arcane_control", "char_class": "Wizard", "hp": 9, "stats": {"might": 1, "grit": 1, "wit": 5}},
    {"role": "scout", "char_class": "Rogue", "hp": 10, "stats": {"might": 2, "grit": 2, "wit": 4}},
    {"role": "face", "char_class": "Bard", "hp": 10, "stats": {"might": 1, "grit": 2, "wit": 4}},
    {"role": "striker", "char_class": "Ranger", "hp": 11, "stats": {"might": 3, "grit": 2, "wit": 3}},
]

NAME_POOL = [
    "Alaric", "Brina", "Cassian", "Delia", "Ember", "Fen", "Galen", "Hale", "Iris", "Joran",
    "Kael", "Liora", "Mira", "Nolan", "Orin", "Piper", "Quill", "Rhea", "Sylas", "Tamsin",
]

PERSONALITY_POOL = [
    "grim but loyal", "curious and analytical", "brash and fearless", "quietly compassionate",
    "sardonic and pragmatic", "optimistic despite danger", "ritualistic and disciplined",
]

GOAL_POOL = [
    "break Strahd's hold over Barovia",
    "recover a lost family relic",
    "protect innocents trapped in the valley",
    "uncover the true history of Castle Ravenloft",
    "redeem a past failure",
]

FLAW_POOL = [
    "overconfident in battle", "cannot resist a mystery", "trusts too slowly", "acts before planning",
    "haunted by nightmares", "too protective of allies",
]

PRESET_CONFIG = {
    "balanced": {
        "templates": ["frontliner", "divine_support", "arcane_control", "scout", "face", "striker"],
        "hp_delta": 0,
        "personality": PERSONALITY_POOL,
    },
    "hardcore": {
        "templates": ["frontliner", "frontliner", "divine_support", "striker", "scout"],
        "hp_delta": -1,
        "personality": [
            "grim but loyal",
            "sardonic and pragmatic",
            "ritualistic and disciplined",
            "brash and fearless",
        ],
    },
    "story-heavy": {
        "templates": ["face", "arcane_control", "divine_support", "scout", "striker"],
        "hp_delta": 0,
        "personality": [
            "quietly compassionate",
            "curious and analytical",
            "optimistic despite danger",
            "cannot stop cataloging omens",
            "soft-spoken but relentless",
        ],
    },
    "cos-survival": {
        "templates": ["frontliner", "frontliner", "divine_support", "divine_support", "striker"],
        "hp_delta": 2,
        "personality": [
            "grim but loyal",
            "ritualistic and disciplined",
            "quietly compassionate",
            "sardonic and pragmatic",
        ],
    },
}


def generate_party(
    size: int = 4,
    seed: int = 42,
    srd: SRDContent | None = None,
    preset: str = "balanced",
) -> list[Character]:
    if size <= 0:
        raise ValueError("Party size must be positive")
    if preset not in PRESET_CONFIG:
        raise ValueError(f"Unknown preset: {preset}")

    randomizer = random.Random(seed)
    template_by_role = {template["role"]: template for template in ROLE_TEMPLATES}
    config = PRESET_CONFIG[preset]
    selected_templates = [template_by_role[role] for role in config["templates"] if role in template_by_role]
    templates = selected_templates or ROLE_TEMPLATES.copy()
    randomizer.shuffle(templates)

    backgrounds = srd.background_names if srd and srd.background_names else ["Acolyte", "Criminal", "Sage", "Soldier"]
    names = NAME_POOL.copy()
    randomizer.shuffle(names)

    hp_delta = int(config["hp_delta"])
    personalities = list(config["personality"])

    party: list[Character] = []
    for index in range(size):
        template = templates[index % len(templates)]
        name = names[index % len(names)]
        background = randomizer.choice(backgrounds)
        hp_value = max(6, template["hp"] + hp_delta)

        character = Character(
            name=name,
            hp=hp_value,
            stats=template["stats"],
            tags=[template["role"], template["char_class"].lower(), f"preset:{preset}"],
            role=template["role"],
            char_class=template["char_class"],
            background=background,
            personality=randomizer.choice(personalities),
            goal=randomizer.choice(GOAL_POOL),
            flaw=randomizer.choice(FLAW_POOL),
        )
        party.append(character)

    return party


def save_party_json(party: list[Character], output_path: str | Path) -> dict:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "party": [asdict(member) for member in party],
        "party_size": len(party),
    }
    with destination.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    return payload