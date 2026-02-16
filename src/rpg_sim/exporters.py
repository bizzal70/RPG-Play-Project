from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .models import SessionResult, TurnResult


@dataclass
class EpisodeSceneCard:
    turn_index: int
    title: str
    narration: str
    actions: list[str]
    outcomes: list[str]
    image_prompt: str
    tts_voice_hint: str


@dataclass
class EpisodePackage:
    episode_title: str
    setting_name: str
    seed: int
    total_turns: int
    summary: str
    scene_cards: list[EpisodeSceneCard]


def build_episode_package(result: SessionResult, seed: int) -> EpisodePackage:
    scene_cards = [_build_scene_card(turn) for turn in result.turns]
    final_hp = ", ".join(f"{member.name}: {member.hp} HP" for member in result.final_state.party)
    roster = "; ".join(
        (
            f"{member.name}"
            f" ({member.char_class or 'Adventurer'}"
            f"/{member.role or 'generalist'}"
            f"/{member.background or 'unknown background'})"
        )
        for member in result.final_state.party
    )
    summary = (
        f"Party roster: {roster}. "
        f"Automated session complete in {result.total_turns} turns. "
        f"Final party condition: {final_hp}."
    )

    return EpisodePackage(
        episode_title=f"{result.setting_name} - Simulated Episode (Seed {seed})",
        setting_name=result.setting_name,
        seed=seed,
        total_turns=result.total_turns,
        summary=summary,
        scene_cards=scene_cards,
    )


def write_episode_exports(package: EpisodePackage, output_dir: str | Path) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    episode_json = output_path / "episode_package.json"
    tts_script = output_path / "tts_script.txt"
    image_prompts = output_path / "image_prompts.txt"

    with episode_json.open("w", encoding="utf-8") as file:
        json.dump(asdict(package), file, indent=2)

    with tts_script.open("w", encoding="utf-8") as file:
        file.write(_build_tts_script(package))

    with image_prompts.open("w", encoding="utf-8") as file:
        file.write(_build_image_prompt_pack(package))

    return {
        "episode_json": str(episode_json),
        "tts_script": str(tts_script),
        "image_prompts": str(image_prompts),
    }


def _build_scene_card(turn: TurnResult) -> EpisodeSceneCard:
    actions = [f"{intent.actor_name}: {intent.action}" for intent in turn.intents]
    outcomes = [outcome.summary for outcome in turn.outcomes]
    narration = (
        f"Scene {turn.turn_index}. {turn.scene_prompt} "
        f"The party acts: {'; '.join(actions) if actions else 'No action recorded'}. "
        f"Outcomes: {'; '.join(outcomes) if outcomes else 'No outcomes recorded'}."
    )
    image_prompt = (
        f"Cinematic fantasy scene, turn {turn.turn_index}. {turn.scene_prompt}. "
        f"Mood-rich lighting, dramatic composition, detailed environment, narrative realism."
    )

    return EpisodeSceneCard(
        turn_index=turn.turn_index,
        title=f"Turn {turn.turn_index}",
        narration=narration,
        actions=actions,
        outcomes=outcomes,
        image_prompt=image_prompt,
        tts_voice_hint="Narrator, calm cinematic tone, medium pacing",
    )


def _build_tts_script(package: EpisodePackage) -> str:
    lines = [package.episode_title, "", package.summary, ""]
    for scene in package.scene_cards:
        lines.append(f"[{scene.title}]")
        lines.append(scene.narration)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _build_image_prompt_pack(package: EpisodePackage) -> str:
    lines = [package.episode_title, ""]
    for scene in package.scene_cards:
        lines.append(f"{scene.title}: {scene.image_prompt}")
    return "\n".join(lines).strip() + "\n"