from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ActionIntent, ActionOutcome, CampaignState, Scene


class BaseRuleset(ABC):
    @abstractmethod
    def validate_intent(self, campaign: CampaignState, intent: ActionIntent) -> bool:
        raise NotImplementedError

    @abstractmethod
    def resolve_intent(self, campaign: CampaignState, intent: ActionIntent) -> ActionOutcome:
        raise NotImplementedError


class BaseDirector(ABC):
    @abstractmethod
    def build_scene(self, campaign: CampaignState) -> Scene:
        raise NotImplementedError


class BaseActor(ABC):
    @abstractmethod
    def choose_action(self, campaign: CampaignState, scene: Scene, actor_name: str) -> ActionIntent:
        raise NotImplementedError
