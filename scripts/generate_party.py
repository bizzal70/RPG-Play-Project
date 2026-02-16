from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rpg_sim.party_builder import generate_party, save_party_json
from src.rpg_sim.srd import load_srd_content


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a full adventuring party JSON")
    parser.add_argument("--out", default="data/parties/generated_party.json", help="Output path for generated party JSON")
    parser.add_argument("--size", type=int, default=4, help="Number of party members")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation")
    parser.add_argument("--preset", choices=["balanced", "hardcore", "story-heavy", "cos-survival"], default="balanced", help="Party archetype preset")
    parser.add_argument("--srd-json", default="data/srd/srd_5e_2024_merged.json", help="Optional SRD JSON for backgrounds")
    parser.add_argument("--no-srd", action="store_true", help="Generate party without SRD enrichment")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    srd = None
    if not args.no_srd and Path(args.srd_json).exists():
        srd = load_srd_content(args.srd_json)

    party = generate_party(size=args.size, seed=args.seed, srd=srd, preset=args.preset)
    payload = save_party_json(party, args.out)
    summary = {
        "output": args.out,
        "preset": args.preset,
        "party_size": payload["party_size"],
        "names": [member["name"] for member in payload["party"]],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()