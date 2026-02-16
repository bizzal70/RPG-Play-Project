from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rpg_sim.ledger import ensure_ledger, load_manifest
from src.rpg_sim.dashboard import build_campaign_dashboard
from src.rpg_sim.dashboard_view import render_dashboard_html
from src.rpg_sim.source_profiles import load_source_profiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly autonomous campaign sessions with auto resume + briefings")
    parser.add_argument("--campaign", default="data/campaign_template.json", help="Campaign JSON path")
    parser.add_argument("--source-profile", default="cos", help="Source profile name")
    parser.add_argument("--source-profiles-json", default="data/source_profiles.json", help="Source profiles JSON path")
    parser.add_argument("--party-json", default="data/parties/party_cos_survival.json", help="Party JSON path (default auto-resolves from source profile when configured)")
    parser.add_argument("--campaign-id", default="strahd_weekly", help="Ledger campaign id (default auto-resolves from source profile)")
    parser.add_argument("--ledger-dir", default="data/ledger", help="Ledger root directory")
    parser.add_argument("--turns", type=int, default=8, help="Turns per weekly session")
    parser.add_argument("--base-seed", type=int, default=7, help="Seed used for first session")
    parser.add_argument("--policy-actors", action=argparse.BooleanOptionalAction, default=True, help="Use per-character policy actor")
    parser.add_argument("--ai-actors", action=argparse.BooleanOptionalAction, default=True, help="Use OpenAI-backed character action decisions")
    parser.add_argument("--ai-director", action=argparse.BooleanOptionalAction, default=True, help="Use OpenAI-backed DM scene generation")
    parser.add_argument("--ai-policy-json", default="data/policies/character_policies.json", help="Path to per-character AI policy JSON")
    parser.add_argument("--ai-model", default="gpt-4o-mini", help="OpenAI model for AI director/actors")
    parser.add_argument("--ai-api-key-env", default="OPENAI_API_KEY", help="OpenAI API key env var for AI director/actors")
    parser.add_argument("--publish", action="store_true", help="Auto-export episode assets after scheduled run")
    parser.add_argument("--weekly-report", action=argparse.BooleanOptionalAction, default=True, help="Generate weekly report markdown after each scheduled run")
    parser.add_argument("--update-dashboard", action=argparse.BooleanOptionalAction, default=True, help="Refresh campaign dashboard JSON after each scheduled run")
    parser.add_argument("--dashboard-html", action=argparse.BooleanOptionalAction, default=True, help="Generate HTML dashboard view when dashboard is updated")
    parser.add_argument("--render-media", action="store_true", help="Render TTS/images during publish mode")
    parser.add_argument("--assemble-video", action="store_true", help="Assemble MP4 during publish mode")
    parser.add_argument("--export-root", default="outputs/weekly", help="Root directory for scheduled publish outputs")
    parser.add_argument("--tts-provider", default="openai", help="TTS provider passed to main.py")
    parser.add_argument("--image-provider", default="openai", help="Image provider passed to main.py")
    parser.add_argument("--video-filename", default="episode.mp4", help="Video filename passed to main.py")
    parser.add_argument("--openai-api-key-env", default="OPENAI_API_KEY", help="OpenAI key env var name")
    parser.add_argument("--openai-tts-model", default="gpt-4o-mini-tts", help="OpenAI TTS model")
    parser.add_argument("--openai-tts-voice", default="alloy", help="OpenAI TTS voice")
    parser.add_argument("--openai-image-model", default="gpt-image-1", help="OpenAI image model")
    parser.add_argument("--openai-image-size", default="1024x1024", help="OpenAI image size")
    parser.add_argument("--elevenlabs-api-key-env", default="ELEVENLABS_API_KEY", help="ElevenLabs key env var name")
    parser.add_argument("--elevenlabs-voice-id", default="EXAVITQu4vr4xnSDxMaL", help="ElevenLabs voice id")
    parser.add_argument("--elevenlabs-model-id", default="eleven_multilingual_v2", help="ElevenLabs model id")
    parser.add_argument("--dry-run", action="store_true", help="Print planning info without running main.py")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    profiles = load_source_profiles(args.source_profiles_json)
    profile = profiles.get(args.source_profile)
    if profile is None:
        available = ", ".join(sorted(profiles.keys()))
        raise ValueError(f"Unknown source profile '{args.source_profile}'. Available: {available}")

    default_campaign_json = "data/campaign_template.json"
    active_campaign_json = args.campaign
    if args.campaign == default_campaign_json and isinstance(profile.get("campaign_json"), str):
        active_campaign_json = str(profile["campaign_json"])

    default_ai_policy_json = "data/policies/character_policies.json"
    active_ai_policy_json = args.ai_policy_json
    if args.ai_policy_json == default_ai_policy_json and isinstance(profile.get("ai_policy_json"), str):
        active_ai_policy_json = str(profile["ai_policy_json"])

    default_campaign_id = "strahd_weekly"
    active_campaign_id = args.campaign_id
    if args.campaign_id == default_campaign_id:
        if isinstance(profile.get("campaign_id"), str) and profile.get("campaign_id"):
            active_campaign_id = str(profile["campaign_id"])
        else:
            active_campaign_id = f"{args.source_profile}_weekly"

    default_party_json = "data/parties/party_cos_survival.json"
    active_party_json = args.party_json
    if args.party_json == default_party_json:
        if isinstance(profile.get("party_json"), str):
            resolved_party = str(profile.get("party_json") or "").strip()
            active_party_json = resolved_party
        else:
            active_party_json = ""

    paths = ensure_ledger(args.ledger_dir, active_campaign_id)
    manifest = load_manifest(paths)

    sessions = manifest.get("sessions", [])
    session_count = int(manifest.get("session_count", 0))
    resume = session_count > 0
    next_session_index = session_count + 1

    if sessions:
        last_seed = int(sessions[-1].get("seed", args.base_seed - 1))
        next_seed = last_seed + 1
    else:
        next_seed = args.base_seed

    briefing_path = _write_briefing(paths["root"], next_session_index, sessions)
    session_export_dir = Path(args.export_root) / args.campaign_id / f"session_{next_session_index:04d}"

    command = [
        sys.executable,
        "main.py",
        "--campaign",
        active_campaign_json,
        "--source-profile",
        args.source_profile,
        "--source-profiles-json",
        args.source_profiles_json,
        "--use-ledger",
        "--campaign-id",
        active_campaign_id,
        "--ledger-dir",
        args.ledger_dir,
        "--turns",
        str(args.turns),
        "--seed",
        str(next_seed),
    ]
    if active_party_json:
        command.extend(["--party-json", active_party_json])
    if resume:
        command.append("--resume")

    if args.policy_actors:
        command.extend(["--policy-actors", "--ai-policy-json", active_ai_policy_json])
    if args.ai_actors:
        command.extend([
            "--ai-actors",
            "--ai-policy-json",
            active_ai_policy_json,
            "--ai-model",
            args.ai_model,
            "--ai-api-key-env",
            args.ai_api_key_env,
        ])
    if args.ai_director:
        command.extend([
            "--ai-director",
            "--ai-model",
            args.ai_model,
            "--ai-api-key-env",
            args.ai_api_key_env,
        ])

    if args.publish:
        command.extend([
            "--export-episodes",
            "--export-dir",
            str(session_export_dir),
        ])

        if args.render_media:
            command.extend([
                "--render-media",
                "--tts-provider",
                args.tts_provider,
                "--image-provider",
                args.image_provider,
                "--openai-api-key-env",
                args.openai_api_key_env,
                "--openai-tts-model",
                args.openai_tts_model,
                "--openai-tts-voice",
                args.openai_tts_voice,
                "--openai-image-model",
                args.openai_image_model,
                "--openai-image-size",
                args.openai_image_size,
                "--elevenlabs-api-key-env",
                args.elevenlabs_api_key_env,
                "--elevenlabs-voice-id",
                args.elevenlabs_voice_id,
                "--elevenlabs-model-id",
                args.elevenlabs_model_id,
            ])

        if args.assemble_video:
            command.extend([
                "--assemble-video",
                "--video-filename",
                args.video_filename,
            ])

    planning = {
        "campaign_id": active_campaign_id,
        "campaign_json": active_campaign_json,
        "party_json": active_party_json or None,
        "existing_sessions": session_count,
        "next_session": next_session_index,
        "resume": resume,
        "next_seed": next_seed,
        "policy_actors": args.policy_actors or args.ai_actors,
        "ai_actors": args.ai_actors,
        "ai_director": args.ai_director,
        "ai_policy_json": active_ai_policy_json if (args.policy_actors or args.ai_actors or args.ai_director) else None,
        "ai_model": args.ai_model if (args.ai_actors or args.ai_director) else None,
        "ai_api_key_env": args.ai_api_key_env if (args.ai_actors or args.ai_director) else None,
        "publish": args.publish,
        "weekly_report": args.weekly_report,
        "update_dashboard": args.update_dashboard,
        "dashboard_html": args.dashboard_html,
        "session_export_dir": str(session_export_dir) if args.publish else None,
        "briefing": str(briefing_path),
        "command": " ".join(command),
    }

    if args.dry_run:
        print(json.dumps({"dry_run": True, **planning}, indent=2))
        return

    completed = subprocess.run(command, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=False)
    output_text = completed.stdout.strip()

    if completed.returncode != 0:
        print(json.dumps({
            "ok": False,
            **planning,
            "returncode": completed.returncode,
            "stderr": completed.stderr.strip(),
        }, indent=2))
        raise SystemExit(completed.returncode)

    run_output = _parse_json_output(output_text)
    report_path = None
    if args.weekly_report:
        report_root = session_export_dir if args.publish else (paths["root"] / "reports")
        report_path = _write_weekly_report(
            report_root=report_root,
            session_index=next_session_index,
            planning=planning,
            run_output=run_output,
        )

    dashboard = None
    dashboard_html_path = None
    if args.update_dashboard:
        dashboard = build_campaign_dashboard(
            campaign_id=active_campaign_id,
            ledger_dir=args.ledger_dir,
            weekly_outputs_root=args.export_root,
        )
        if args.dashboard_html and isinstance(dashboard, dict):
            html_path = Path(args.ledger_dir) / active_campaign_id / "dashboard.html"
            dashboard_html_path = render_dashboard_html(dashboard, html_path)

    print(json.dumps({
        "ok": True,
        **planning,
        "weekly_report_path": str(report_path) if report_path else None,
        "dashboard_path": dashboard.get("dashboard_path") if isinstance(dashboard, dict) else None,
        "dashboard_html_path": dashboard_html_path,
        "run_output": run_output,
    }, indent=2))


def _write_briefing(ledger_root: Path, next_session_index: int, sessions: list[dict]) -> Path:
    briefings_dir = ledger_root / "briefings"
    briefings_dir.mkdir(parents=True, exist_ok=True)
    briefing_path = briefings_dir / f"session_{next_session_index:04d}_briefing.md"

    if sessions:
        last = sessions[-1]
        summary = (
            f"Last session: {last.get('session_id')} | seed={last.get('seed')} "
            f"| turns={last.get('turns')} | source_profile={last.get('source_profile')}"
        )
        objectives = [
            "Continue unresolved hooks from prior session log.",
            "Advance one major objective and one character-specific arc beat.",
            "End with a cliffhanger or decision point for next week.",
        ]
    else:
        summary = "No prior sessions. This is the campaign kickoff session."
        objectives = [
            "Establish party tone, bonds, and immediate stakes.",
            "Introduce first major threat and a clear short-term objective.",
            "Close with momentum into the next session.",
        ]

    lines = [
        f"# Weekly Briefing - Session {next_session_index}",
        "",
        "## Recap",
        f"- {summary}",
        "",
        "## Objectives",
    ]
    lines.extend(f"- {objective}" for objective in objectives)
    lines.append("")

    briefing_path.write_text("\n".join(lines), encoding="utf-8")
    return briefing_path


def _parse_json_output(text: str) -> dict | str:
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _write_weekly_report(
    report_root: Path,
    session_index: int,
    planning: dict[str, Any],
    run_output: dict | str,
) -> Path:
    report_root.mkdir(parents=True, exist_ok=True)
    report_path = report_root / f"session_{session_index:04d}_weekly_report.md"

    if not isinstance(run_output, dict):
        report_path.write_text(
            "\n".join(
                [
                    f"# Weekly Report - Session {session_index}",
                    "",
                    "Run output was not JSON; raw output follows:",
                    "",
                    str(run_output),
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return report_path

    summary = run_output.get("summary", {})
    analyses = run_output.get("analyses", [])
    analysis = analyses[0] if analyses and isinstance(analyses[0], dict) else {}
    final_state = run_output.get("last_run", {}).get("final_state", {})
    party = final_state.get("party", []) if isinstance(final_state, dict) else []
    log = final_state.get("log", []) if isinstance(final_state, dict) else []

    party_lines = []
    for member in party:
        if not isinstance(member, dict):
            continue
        name = member.get("name", "Unknown")
        hp = member.get("hp", "?")
        role = member.get("role") or "adventurer"
        char_class = member.get("char_class") or "unknown-class"
        party_lines.append(f"- {name}: {hp} HP ({char_class}/{role})")

    recommendations = analysis.get("recommendations", []) if isinstance(analysis, dict) else []
    if not recommendations:
        recommendations = ["No additional risk recommendations generated."]

    recent_log = log[-6:] if isinstance(log, list) else []
    if not recent_log:
        recent_log = ["No session log entries available."]

    next_hooks = [
        "Continue unresolved encounter pressure from last scene.",
        "Push one personal character goal into spotlight.",
        "Force a strategic choice with clear tradeoffs.",
    ]

    lines = [
        f"# Weekly Report - Session {session_index}",
        "",
        "## Run Metadata",
        f"- Campaign: {planning.get('campaign_id')}",
        f"- Seed: {planning.get('next_seed')}",
        f"- Resumed: {planning.get('resume')}",
        f"- Source Profile: {run_output.get('source_profile')}",
        "",
        "## Outcome Summary",
        f"- TPK Rate: {summary.get('tpk_rate', 0)}",
        f"- Avg Final Party HP: {summary.get('avg_final_party_hp', 0)}",
        f"- Avg Stalled Turns: {summary.get('avg_stalled_turns', 0)}",
        f"- Clue Discovered: {analysis.get('clue_discovered', False)}",
        "",
        "## Party Condition",
    ]
    lines.extend(party_lines or ["- No party state available."])
    lines.extend([
        "",
        "## Risk Flags",
    ])
    lines.extend(f"- {item}" for item in recommendations)
    lines.extend([
        "",
        "## Session Recap (Recent Log)",
    ])
    lines.extend(f"- {entry}" for entry in recent_log)
    lines.extend([
        "",
        "## Next Session Hooks",
    ])
    lines.extend(f"- {hook}" for hook in next_hooks)
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    main()
