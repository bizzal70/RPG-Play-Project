from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rpg_sim.pdf_ingest import ingest_pdf_to_chunks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a PDF into chunked JSON source material")
    parser.add_argument("--pdf", required=True, help="Path to source PDF")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--chunk-words", type=int, default=220, help="Words per chunk")
    parser.add_argument("--chunk-overlap", type=int, default=40, help="Overlap words between chunks")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = ingest_pdf_to_chunks(
        pdf_path=args.pdf,
        output_path=args.out,
        chunk_words=args.chunk_words,
        chunk_overlap_words=args.chunk_overlap,
    )
    print(json.dumps({
        "output": args.out,
        "total_pages": payload["total_pages"],
        "pages_with_text": payload["pages_with_text"],
        "chunk_count": payload["chunk_count"],
    }, indent=2))


if __name__ == "__main__":
    main()