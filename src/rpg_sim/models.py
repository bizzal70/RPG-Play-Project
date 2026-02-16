from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Character:
    name: str
    hp: int
    stats: dict[str, int]
    tags: list[str] = field(default_factory=list)
    role: str = ""
    char_class: str = ""
    background: str = ""
    personality: str = ""
    goal: str = ""
    flaw: str = ""


@dataclass
class Encounter:
    id: str
    title: str
    threat: int
    description: str


@dataclass
class CampaignState:
    setting_name: str
    chapter: str
    turn_index: int
    party: list[Character]
    encounters: list[Encounter]
    flags: dict[str, Any] = field(default_factory=dict)
    log: list[str] = field(default_factory=list)


@dataclass
class Scene:
    prompt: str
    options: list[str]


@dataclass
class ActionIntent:
    actor_name: str
    action: str
    target: str | None = None


@dataclass
class ActionOutcome:
    actor_name: str
    success: bool
    summary: str
    hp_delta: dict[str, int] = field(default_factory=dict)
    flag_updates: dict[str, Any] = field(default_factory=dict)


@dataclass
class TurnResult:
    turn_index: int
    scene_prompt: str
    intents: list[ActionIntent]
    outcomes: list[ActionOutcome]


@dataclass
class SessionResult:
    setting_name: str
    total_turns: int
    final_state: CampaignState
    turns: list[TurnResult]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)