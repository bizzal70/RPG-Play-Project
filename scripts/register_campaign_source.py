from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rpg_sim.pdf_ingest import ingest_pdf_to_chunks
from src.rpg_sim.source_profiles import load_source_profiles, save_source_profiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register campaign source material as a reusable source profile")
    parser.add_argument("--profile", required=True, help="Profile name to create/update (for --source-profile)")
    parser.add_argument("--pdf", required=True, help="Path to campaign PDF")
    parser.add_argument("--chunks-out", required=True, help="Output path for chunk JSON")
    parser.add_argument("--source-profiles-json", default="data/source_profiles.json", help="Path to source profiles JSON")
    parser.add_argument("--campaign-json", default="data/campaign_template.json", help="Campaign JSON seed path to pair with this profile")
    parser.add_argument("--campaign-id", default="", help="Optional default weekly campaign id for scheduler")
    parser.add_argument("--party-json", default="", help="Optional default party JSON path for scheduler/main")
    parser.add_argument("--ai-policy-json", default="", help="Optional campaign-specific AI policy JSON path to attach to profile")
    parser.add_argument("--srd-json", default="data/srd/srd_5e_2024_merged.json", help="Path to SRD JSON to pair with profile")
    parser.add_argument("--chunk-words", type=int, default=220, help="Words per source chunk")
    parser.add_argument("--chunk-overlap", type=int, default=40, help="Overlapping words between chunks")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip PDF ingest and only update source profile")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    chunk_count = None
    if not args.skip_ingest:
        payload = ingest_pdf_to_chunks(
            pdf_path=args.pdf,
            output_path=args.chunks_out,
            chunk_words=args.chunk_words,
            chunk_overlap_words=args.chunk_overlap,
        )
        chunk_count = payload.get("chunk_count")

    profiles = load_source_profiles(args.source_profiles_json)
    profile_payload = {
        "campaign_json": args.campaign_json,
        "use_srd": True,
        "srd_json": args.srd_json,
        "use_source_chunks": True,
        "source_chunks_json": args.chunks_out,
    }
    if args.campaign_id:
        profile_payload["campaign_id"] = args.campaign_id
    if args.party_json:
        profile_payload["party_json"] = args.party_json
    if args.ai_policy_json:
        profile_payload["ai_policy_json"] = args.ai_policy_json

    profiles[args.profile] = profile_payload
    save_source_profiles(args.source_profiles_json, profiles)

    summary = {
        "profile": args.profile,
        "source_profiles_json": args.source_profiles_json,
        "campaign_json": args.campaign_json,
        "campaign_id": args.campaign_id or None,
        "party_json": args.party_json or None,
        "ai_policy_json": args.ai_policy_json or None,
        "chunks_out": args.chunks_out,
        "chunk_count": chunk_count,
        "run_with": f"python main.py --campaign data/campaign_template.json --source-profile {args.profile} --turns 8 --seed 7",
        "tune_with": (
            f"python scripts/generate_campaign_tuning.py --source-profile {args.profile} --apply-profile"
        ),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()