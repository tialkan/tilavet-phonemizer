#!/usr/bin/env python3
"""Initialize validation status model for recovered_seed.jsonl.

This script:
1. Reads recovered_seed.jsonl
2. Enriches each ayah with:
   - status: "candidate_v1" (vs future gold_wasl_v1, gold_waqf_on_pause_v1)
   - reviews: {} (to be filled by LLM hafiz reviews)
   - agreement: {total: 0, consensus: 0, percent: 0}
3. Outputs an enhanced JSONL with validation tracking structure
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


class ReviewDict(TypedDict, total=False):
    """Single reviewer's verdict on an ayah."""
    verdict: str  # "correct" | "error" | "unsure"
    date: str
    notes: str


class AgreementDict(TypedDict):
    """Agreement metrics across reviewers."""
    total_reviewers: int
    consensus: int  # number of reviewers who agree
    percent: float  # consensus / total_reviewers * 100


class EnrichedAyah(TypedDict, total=False):
    """Enriched ayah structure with validation metadata."""
    ayah: str
    label: str
    arabic: str
    mode: str
    candidate_v1: str
    source: str

    # NEW FIELDS
    status: str  # "candidate_v1" | "gold_wasl_v1" | "gold_waqf_on_pause_v1"
    reviews: dict[str, ReviewDict]
    agreement: AgreementDict


def load_seed(path: Path) -> list[dict]:
    """Load JSONL seed file."""
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def enrich_ayah(original: dict) -> EnrichedAyah:
    """Add validation status model fields to an ayah."""
    enriched: EnrichedAyah = {
        **original,
        "status": "candidate_v1",
        "reviews": {},
        "agreement": {
            "total_reviewers": 0,
            "consensus": 0,
            "percent": 0.0,
        },
    }
    return enriched


def save_enriched_seed(enriched: list[EnrichedAyah], path: Path) -> None:
    """Save enriched seed to JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for ayah in enriched:
            handle.write(json.dumps(ayah, ensure_ascii=False) + "\n")


def generate_summary(enriched: list[EnrichedAyah]) -> str:
    """Generate a summary of the enriched seed."""
    lines = [
        "# Validation Model Initialization Summary",
        "",
        f"Total ayahs: {len(enriched)}",
        "",
        "## Status Distribution",
        "",
    ]

    status_counts = {}
    for ayah in enriched:
        status = ayah.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend([
        "",
        "## Review Status",
        "",
        "- Reviewers who have voted: 0 (seed state)",
        f"- Agreement consensus: 0 / {len(enriched)} ayahs",
        "- Ready for LLM hafiz review: ✓",
        "",
        "## Fields Added",
        "",
        "Each ayah now has:",
        "",
        "- `status`: Current validation state (candidate_v1)",
        "- `reviews`: Dict for LLM hafiz verdicts {reviewer_name: {verdict, date, notes}}",
        "- `agreement`: Metrics {total_reviewers, consensus, percent}",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize validation status model for recovered_seed.jsonl"
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=ROOT / "data" / "validation" / "recovered_seed.jsonl",
        help="Input JSONL seed file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "validation" / "recovered_seed_with_validation.jsonl",
        help="Output JSONL file with validation model",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="Optional summary output path",
    )
    args = parser.parse_args()

    # Load, enrich, save
    original_seed = load_seed(args.seed)
    enriched_seed = [enrich_ayah(ayah) for ayah in original_seed]
    save_enriched_seed(enriched_seed, args.output)

    print(f"✓ Enriched {len(enriched_seed)} ayahs")
    print(f"✓ Saved to: {args.output}")

    if args.summary:
        summary = generate_summary(enriched_seed)
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(summary + "\n", encoding="utf-8")
        print(f"✓ Summary saved to: {args.summary}")
    else:
        summary = generate_summary(enriched_seed)
        print("\n" + summary)


if __name__ == "__main__":
    main()
