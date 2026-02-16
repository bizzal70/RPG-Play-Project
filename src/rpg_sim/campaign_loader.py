from __future__ import annotations

import json
from dataclasses import asdict

from .models import CampaignState, Character, Encounter


def load_campaign_from_json(path: str) -> CampaignState:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    party = [_parse_character(character) for character in data["party"]]

    encounters = [
        Encounter(
            id=encounter["id"],
            title=encounter["title"],
            threat=encounter["threat"],
            description=encounter["description"],
        )
        for encounter in data.get("encounters", [])
    ]

    return CampaignState(
        setting_name=data["setting_name"],
        chapter=data.get("chapter", "Chapter 1"),
        turn_index=0,
        party=party,
        encounters=encounters,
        flags=data.get("flags", {}),
        log=[],
    )


def load_party_from_json(path: str) -> list[Character]:
    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    members = payload.get("party", payload)
    if not isinstance(members, list):
        raise ValueError("Party JSON must be either a list of characters or an object with a 'party' list")

    return [_parse_character(member) for member in members]


def campaign_state_from_dict(data: dict) -> CampaignState:
    party = [_parse_character(character) for character in data.get("party", [])]

    encounters = [
        Encounter(
            id=encounter["id"],
            title=encounter["title"],
            threat=encounter["threat"],
            description=encounter["description"],
        )
        for encounter in data.get("encounters", [])
    ]

    return CampaignState(
        setting_name=data.get("setting_name", "Unknown Setting"),
        chapter=data.get("chapter", "Chapter 1"),
        turn_index=int(data.get("turn_index", 0)),
        party=party,
        encounters=encounters,
        flags=data.get("flags", {}),
        log=data.get("log", []),
    )


def campaign_state_to_dict(state: CampaignState) -> dict:
    return asdict(state)


def _parse_character(character: dict) -> Character:
    return Character(
        name=character["name"],
        hp=character["hp"],
        stats=character.get("stats", {}),
        tags=character.get("tags", []),
        role=character.get("role", ""),
        char_class=character.get("char_class", ""),
        background=character.get("background", ""),
        personality=character.get("personality", ""),
        goal=character.get("goal", ""),
        flaw=character.get("flaw", ""),
    )