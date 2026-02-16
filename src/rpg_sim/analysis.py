from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict

from .models import SessionResult


@dataclass
class SingleRunAnalysis:
    tpk: bool
    average_party_hp: float
    low_hp_turns: int
    stalled_turns: int
    clue_discovered: bool
    recommendations: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_session(result: SessionResult) -> SingleRunAnalysis:
    final_party = result.final_state.party
    average_party_hp = sum(member.hp for member in final_party) / max(1, len(final_party))
    tpk = all(member.hp <= 0 for member in final_party)

    low_hp_turns = 0
    stalled_turns = 0
    for turn in result.turns:
        actions = [intent.action for intent in turn.intents]
        if any(action == "rest" for action in actions):
            low_hp_turns += 1
        if actions and all(action in {"rest", "defend"} for action in actions):
            stalled_turns += 1

    clue_discovered = result.final_state.flags.get("latest_discovery", "") != ""

    recommendations: list[str] = []
    if tpk:
        recommendations.append("Lower early threat or increase safety valves to avoid full party defeat.")
    if average_party_hp < 3:
        recommendations.append("Add healing opportunities or reduce attrition pressure between scenes.")
    if stalled_turns >= max(1, result.total_turns // 3):
        recommendations.append("Increase actionable hooks per scene to reduce defensive dead turns.")
    if not clue_discovered:
        recommendations.append("Seed guaranteed clue paths so investigation failures do not stall progression.")
    if not recommendations:
        recommendations.append("Current scenario appears stable in this run; test with more seeds for confidence.")

    return SingleRunAnalysis(
        tpk=tpk,
        average_party_hp=round(average_party_hp, 2),
        low_hp_turns=low_hp_turns,
        stalled_turns=stalled_turns,
        clue_discovered=clue_discovered,
        recommendations=recommendations,
    )


def summarize_analyses(analyses: list[SingleRunAnalysis]) -> dict:
    if not analyses:
        return {
            "runs": 0,
            "tpk_rate": 0,
            "avg_final_party_hp": 0,
            "avg_stalled_turns": 0,
            "common_recommendations": [],
        }

    tpk_rate = sum(1 for analysis in analyses if analysis.tpk) / len(analyses)
    avg_final_party_hp = sum(analysis.average_party_hp for analysis in analyses) / len(analyses)
    avg_stalled_turns = sum(analysis.stalled_turns for analysis in analyses) / len(analyses)

    recommendation_counts = Counter(
        recommendation
        for analysis in analyses
        for recommendation in analysis.recommendations
    )

    common_recommendations = [
        {"recommendation": recommendation, "count": count}
        for recommendation, count in recommendation_counts.most_common(5)
    ]

    return {
        "runs": len(analyses),
        "tpk_rate": round(tpk_rate, 3),
        "avg_final_party_hp": round(avg_final_party_hp, 2),
        "avg_stalled_turns": round(avg_stalled_turns, 2),
        "common_recommendations": common_recommendations,
    }