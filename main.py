from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path

from src.rpg_sim.agents import HeuristicActor, SimpleDirector
from src.rpg_sim.ai_agents import AIDirector, PolicyDrivenActor, load_policy_profile
from src.rpg_sim.analysis import analyze_session, summarize_analyses
from src.rpg_sim.campaign_loader import campaign_state_from_dict, load_campaign_from_json, load_party_from_json
from src.rpg_sim.exporters import build_episode_package, write_episode_exports
from src.rpg_sim.ledger import ensure_ledger, has_latest_state, load_latest_state_payload, record_session
from src.rpg_sim.media import MediaRenderError, render_episode_media
from src.rpg_sim.pdf_ingest import load_chunk_texts
from src.rpg_sim.rules.generic import GenericD20Ruleset
from src.rpg_sim.srd import SRD2024Director, SRD2024Ruleset, load_srd_content
from src.rpg_sim.session import SessionEngine
from src.rpg_sim.source_profiles import load_source_profiles
from src.rpg_sim.video import VideoAssemblyError, assemble_episode_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an automated RPG simulation session")
    parser.add_argument("--campaign", default="data/campaign_template.json", help="Path to campaign JSON seed (profile may override when left as default)")
    parser.add_argument("--party-json", default="", help="Optional party JSON override")
    parser.add_argument("--use-ledger", action="store_true", help="Enable persistent campaign session checkpoints")
    parser.add_argument("--resume", action="store_true", help="Resume campaign from latest ledger checkpoint")
    parser.add_argument("--campaign-id", default="default", help="Ledger campaign identifier")
    parser.add_argument("--ledger-dir", default="data/ledger", help="Directory for campaign ledger storage")
    parser.add_argument("--source-profile", default="none", help="Named source preset for faster campaign setup")
    parser.add_argument("--source-profiles-json", default="data/source_profiles.json", help="Path to source profile definitions JSON")
    parser.add_argument("--srd-json", default="data/srd/srd_5e_2024_merged.json", help="Path to merged SRD JSON dataset")
    parser.add_argument("--use-srd", action="store_true", help="Activate SRD-backed rules and scene generation")
    parser.add_argument("--source-chunks-json", default="data/sources/srd_5e_2024_chunks.json", help="Path to chunked source text JSON")
    parser.add_argument("--use-source-chunks", action="store_true", help="Include source chunk excerpts in scene generation")
    parser.add_argument("--policy-actors", action=argparse.BooleanOptionalAction, default=True, help="Use per-character policy actor")
    parser.add_argument("--ai-actors", action=argparse.BooleanOptionalAction, default=True, help="Use OpenAI-backed character action decisions")
    parser.add_argument("--ai-director", action=argparse.BooleanOptionalAction, default=True, help="Use OpenAI-backed DM scene generation")
    parser.add_argument("--ai-policy-json", default="data/policies/character_policies.json", help="Path to per-character AI policy JSON")
    parser.add_argument("--ai-model", default="gpt-4o-mini", help="OpenAI chat model for AI director/actors")
    parser.add_argument("--ai-api-key-env", default="OPENAI_API_KEY", help="Environment variable containing OpenAI API key for AI director/actors")
    parser.add_argument("--turns", type=int, default=6, help="Number of turns to simulate")
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic outcomes")
    parser.add_argument("--runs", type=int, default=1, help="How many runs to execute for pitfall analysis")
    parser.add_argument("--export-episodes", action="store_true", help="Export narration and image prompt files")
    parser.add_argument("--export-dir", default="outputs", help="Directory for episode export files")
    parser.add_argument("--render-media", action="store_true", help="Render TTS audio and scene images from episode exports")
    parser.add_argument("--tts-provider", default="openai", help="TTS provider: openai or elevenlabs")
    parser.add_argument("--image-provider", default="openai", help="Image provider: openai or none")
    parser.add_argument("--openai-api-key-env", default="OPENAI_API_KEY", help="Environment variable containing OpenAI API key")
    parser.add_argument("--openai-tts-model", default="gpt-4o-mini-tts", help="OpenAI model for speech generation")
    parser.add_argument("--openai-tts-voice", default="alloy", help="OpenAI voice name")
    parser.add_argument("--openai-image-model", default="gpt-image-1", help="OpenAI model for image generation")
    parser.add_argument("--openai-image-size", default="1024x1024", help="OpenAI image output size")
    parser.add_argument("--elevenlabs-api-key-env", default="ELEVENLABS_API_KEY", help="Environment variable containing ElevenLabs API key")
    parser.add_argument("--elevenlabs-voice-id", default="EXAVITQu4vr4xnSDxMaL", help="ElevenLabs voice id")
    parser.add_argument("--elevenlabs-model-id", default="eleven_multilingual_v2", help="ElevenLabs model id")
    parser.add_argument("--assemble-video", action="store_true", help="Assemble scene media into an MP4 episode per run")
    parser.add_argument("--video-filename", default="episode.mp4", help="Output video filename for each run")
    parser.add_argument("--video-fps", type=int, default=24, help="Video frames per second")
    parser.add_argument("--video-resolution", default="1280x720", help="Video resolution WIDTHxHEIGHT")
    return parser.parse_args()


def run_single(
    campaign,
    turns: int,
    seed: int,
    use_srd: bool,
    srd_json: str,
    source_chunks: list[str] | None,
    source_chunks_json: str,
    policy_actors: bool,
    ai_actors: bool,
    ai_director: bool,
    ai_policy_json: str,
    ai_model: str,
    ai_api_key_env: str,
):
    campaign.log = []

    srd_summary = None
    source_chunks_summary = None
    if source_chunks:
        source_chunks_summary = {
            "source_chunks_json": source_chunks_json,
            "loaded_chunks": len(source_chunks),
        }

    if use_srd:
        srd = load_srd_content(srd_json)
        ruleset = SRD2024Ruleset(srd=srd, random_seed=seed)
        base_director = SRD2024Director(srd=srd, random_seed=seed, source_chunks=source_chunks)
        srd_summary = srd.summary
    else:
        ruleset = GenericD20Ruleset(random_seed=seed)
        base_director = SimpleDirector(source_chunks=source_chunks, random_seed=seed)

    campaign_policy: dict[str, object] = {}
    policy_profile = load_policy_profile(ai_policy_json)
    campaign_candidate = policy_profile.get("campaign", {})
    if isinstance(campaign_candidate, dict):
        campaign_policy = campaign_candidate

    director_guidance = campaign_policy.get("director_guidance", "")
    if not isinstance(director_guidance, str):
        director_guidance = ""

    actor_guidance = campaign_policy.get("actor_guidance", "")
    if not isinstance(actor_guidance, str):
        actor_guidance = ""

    director = AIDirector(
        fallback_director=base_director,
        use_ai=ai_director,
        model=ai_model,
        api_key_env=ai_api_key_env,
        director_guidance=director_guidance,
    )

    has_policy = bool(policy_profile.get("campaign") or policy_profile.get("default") or policy_profile.get("characters"))
    use_policy_actors = has_policy or policy_actors or ai_actors
    if use_policy_actors:
        actor = PolicyDrivenActor(
            policy_profile=policy_profile,
            use_ai=ai_actors,
            model=ai_model,
            api_key_env=ai_api_key_env,
            random_seed=seed,
            actor_guidance=actor_guidance,
        )
    else:
        actor = HeuristicActor()

    if srd_summary:
        campaign.flags["srd_summary"] = srd_summary
    if source_chunks_summary:
        campaign.flags["source_chunks_summary"] = source_chunks_summary
    campaign.flags["ai_mode"] = {
        "policy_actors": use_policy_actors,
        "ai_actors": ai_actors,
        "ai_director": ai_director,
        "ai_policy_json": ai_policy_json if (use_policy_actors or ai_director) else None,
        "ai_model": ai_model if (ai_actors or ai_director) else None,
        "ai_api_key_present": bool(os.environ.get(ai_api_key_env, "")) if (ai_actors or ai_director) else False,
    }

    engine = SessionEngine(ruleset=ruleset, director=director, actor=actor)
    return engine.run(campaign=campaign, max_turns=turns)


def main() -> None:
    args = parse_args()
    runs = max(1, args.runs)

    profiles = load_source_profiles(args.source_profiles_json)
    profile = profiles.get(args.source_profile)
    if profile is None:
        available = ", ".join(sorted(profiles.keys()))
        raise ValueError(f"Unknown source profile '{args.source_profile}'. Available: {available}")

    default_srd_json = "data/srd/srd_5e_2024_merged.json"
    default_source_chunks_json = "data/sources/srd_5e_2024_chunks.json"
    default_campaign_json = "data/campaign_template.json"
    default_ai_policy_json = "data/policies/character_policies.json"

    active_campaign_json = args.campaign
    if args.campaign == default_campaign_json and isinstance(profile.get("campaign_json"), str):
        active_campaign_json = str(profile["campaign_json"])

    active_ai_policy_json = args.ai_policy_json
    if args.ai_policy_json == default_ai_policy_json and isinstance(profile.get("ai_policy_json"), str):
        active_ai_policy_json = str(profile["ai_policy_json"])

    active_srd_json = args.srd_json
    if args.srd_json == default_srd_json and isinstance(profile.get("srd_json"), str):
        active_srd_json = str(profile["srd_json"])

    active_source_chunks_json = args.source_chunks_json
    if args.source_chunks_json == default_source_chunks_json and isinstance(profile.get("source_chunks_json"), str):
        active_source_chunks_json = str(profile["source_chunks_json"])

    profile_use_srd = profile.get("use_srd")
    profile_use_source_chunks = profile.get("use_source_chunks")

    if isinstance(profile_use_srd, bool):
        use_srd = args.use_srd or profile_use_srd
    else:
        use_srd = args.use_srd or Path(active_srd_json).exists()

    if isinstance(profile_use_source_chunks, bool):
        use_source_chunks = args.use_source_chunks or profile_use_source_chunks
    else:
        use_source_chunks = args.use_source_chunks or Path(active_source_chunks_json).exists()
    source_chunks = load_chunk_texts(active_source_chunks_json) if use_source_chunks else []

    ledger_paths = None
    campaign_base = None
    resumed_from_checkpoint = False
    if args.use_ledger:
        ledger_paths = ensure_ledger(args.ledger_dir, args.campaign_id)
        if args.resume and has_latest_state(ledger_paths):
            latest_state_payload = load_latest_state_payload(ledger_paths)
            campaign_base = campaign_state_from_dict(latest_state_payload)
            resumed_from_checkpoint = True
        else:
            campaign_base = load_campaign_from_json(active_campaign_json)
    else:
        campaign_base = load_campaign_from_json(active_campaign_json)

    if args.party_json:
        campaign_base.party = load_party_from_json(args.party_json)

    results = []
    analyses = []
    exports: list[dict[str, str]] = []
    media: list[dict[str, object]] = []
    videos: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []

    campaign_current = copy.deepcopy(campaign_base)
    for run_index in range(runs):
        run_seed = args.seed + run_index
        run_campaign = campaign_current if args.use_ledger else copy.deepcopy(campaign_base)

        result = run_single(
            run_campaign,
            args.turns,
            run_seed,
            use_srd=use_srd,
            srd_json=active_srd_json,
            source_chunks=source_chunks,
            source_chunks_json=active_source_chunks_json,
            policy_actors=args.policy_actors,
            ai_actors=args.ai_actors,
            ai_director=args.ai_director,
            ai_policy_json=active_ai_policy_json,
            ai_model=args.ai_model,
            ai_api_key_env=args.ai_api_key_env,
        )
        results.append(result)
        analyses.append(analyze_session(result))
        campaign_current = result.final_state

        if args.use_ledger and ledger_paths is not None:
            checkpoint = record_session(
                paths=ledger_paths,
                result=result,
                run_seed=run_seed,
                turns=args.turns,
                source_profile=args.source_profile,
            )
            checkpoints.append(checkpoint)

        if args.export_episodes:
            package = build_episode_package(result, seed=run_seed)
            run_dir = Path(args.export_dir) / f"run_{run_index + 1}_seed_{run_seed}"
            export_paths = write_episode_exports(package, run_dir)
            exports.append(export_paths)

            if args.render_media:
                try:
                    media_paths = render_episode_media(
                        package=package,
                        output_dir=run_dir,
                        tts_provider=args.tts_provider,
                        image_provider=args.image_provider,
                        openai_api_key_env=args.openai_api_key_env,
                        tts_model=args.openai_tts_model,
                        tts_voice=args.openai_tts_voice,
                        image_model=args.openai_image_model,
                        image_size=args.openai_image_size,
                        elevenlabs_api_key_env=args.elevenlabs_api_key_env,
                        elevenlabs_voice_id=args.elevenlabs_voice_id,
                        elevenlabs_model_id=args.elevenlabs_model_id,
                    )
                    media.append(
                        {
                            "run": run_index + 1,
                            "status": "ok",
                            "paths": media_paths,
                        }
                    )
                except MediaRenderError as error:
                    media.append(
                        {
                            "run": run_index + 1,
                            "status": "failed",
                            "reason": str(error),
                        }
                    )

            if args.assemble_video:
                try:
                    video_result = assemble_episode_video(
                        run_dir=run_dir,
                        output_filename=args.video_filename,
                        fps=args.video_fps,
                        resolution=args.video_resolution,
                    )
                    videos.append(
                        {
                            "run": run_index + 1,
                            "status": "ok",
                            "video_path": video_result.video_path,
                            "clip_count": video_result.clip_count,
                        }
                    )
                except VideoAssemblyError as error:
                    videos.append(
                        {
                            "run": run_index + 1,
                            "status": "failed",
                            "reason": str(error),
                        }
                    )

    payload = {
        "run_count": runs,
        "use_ledger": args.use_ledger,
        "campaign_id": args.campaign_id if args.use_ledger else None,
        "ledger_dir": args.ledger_dir if args.use_ledger else None,
        "resumed_from_checkpoint": resumed_from_checkpoint,
        "source_profile": args.source_profile,
        "source_profiles_json": args.source_profiles_json,
        "campaign_json": active_campaign_json,
        "party_json": args.party_json or None,
        "active_content_source": "5e_srd_2024" if use_srd else "campaign_only",
        "srd_json": active_srd_json if use_srd else None,
        "source_chunks_json": active_source_chunks_json if source_chunks else None,
        "source_chunks_loaded": len(source_chunks),
        "ai_mode": {
            "policy_actors": args.policy_actors or args.ai_actors,
            "ai_actors": args.ai_actors,
            "ai_director": args.ai_director,
            "ai_policy_json": active_ai_policy_json if (args.policy_actors or args.ai_actors or args.ai_director) else None,
            "ai_model": args.ai_model if (args.ai_actors or args.ai_director) else None,
            "ai_api_key_present": bool(os.environ.get(args.ai_api_key_env, "")) if (args.ai_actors or args.ai_director) else False,
            "ai_api_key_env": args.ai_api_key_env if (args.ai_actors or args.ai_director) else None,
        },
        "summary": summarize_analyses(analyses),
        "analyses": [analysis.to_dict() for analysis in analyses],
        "last_run": results[-1].to_dict(),
    }
    if exports:
        payload["exports"] = exports
    if media:
        payload["media"] = media
    if videos:
        payload["videos"] = videos
    if checkpoints:
        payload["checkpoints"] = checkpoints

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()