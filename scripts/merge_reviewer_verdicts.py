#!/usr/bin/env python3
"""Merge reviewer verdicts into validation model.

This script takes reviewer verdicts (e.g., from CSV or structured data)
and integrates them into recovered_seed_with_validation.jsonl.

Example usage:
    python3 merge_reviewer_verdicts.py \
        --verdicts data/verdicts_gpt4.csv \
        --reviewer gpt4 \
        --enriched data/validation/recovered_seed_with_validation.jsonl \
        --output data/validation/recovered_seed_with_validation.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


class ReviewerVerdict(TypedDict, total=False):
    """Single reviewer verdict on an ayah."""
    verdict: str  # "correct" | "error" | "unsure"
    date: str
    notes: str


def load_enriched_seed(path: Path) -> list[dict]:
    """Load enriched JSONL."""
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_verdicts_from_csv(path: Path) -> dict[str, ReviewerVerdict]:
    """Load verdicts from CSV.

    Expected columns: Ayah, Verdict, Notes (optional)
    Example:
        Ayah,Verdict,Notes
        1:1,correct,
        1:2,error,Wrong madd
        1:3,unsure,Cross-ayah wasl case
    """
    verdicts = {}
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ayah = row.get("Ayah", "").strip()
            if not ayah:
                continue
            verdict: ReviewerVerdict = {
                "verdict": row.get("Verdict", "unsure").lower(),
                "date": row.get("Date", datetime.now().isoformat()[:10]),
            }
            if row.get("Notes", "").strip():
                verdict["notes"] = row["Notes"]
            verdicts[ayah] = verdict
    return verdicts


def update_agreement_metrics(
    enriched: list[dict],
) -> list[dict]:
    """Recalculate agreement metrics for each ayah."""
    for ayah in enriched:
        reviews = ayah.get("reviews", {})
        if not reviews:
            ayah["agreement"] = {
                "total_reviewers": 0,
                "consensus": 0,
                "percent": 0.0,
            }
            continue

        # Count verdicts
        verdicts = [r.get("verdict") for r in reviews.values() if r.get("verdict")]
        if not verdicts:
            ayah["agreement"] = {
                "total_reviewers": len(reviews),
                "consensus": 0,
                "percent": 0.0,
            }
            continue

        # Find consensus (most common verdict)
        from collections import Counter
        verdict_counts = Counter(verdicts)
        consensus_verdict, consensus_count = verdict_counts.most_common(1)[0]

        ayah["agreement"] = {
            "total_reviewers": len(verdicts),
            "consensus": consensus_count,
            "percent": round((consensus_count / len(verdicts)) * 100, 1),
            "consensus_verdict": consensus_verdict,
        }

    return enriched


def merge_verdicts(
    enriched: list[dict],
    reviewer_name: str,
    verdicts: dict[str, ReviewerVerdict],
) -> list[dict]:
    """Merge reviewer verdicts into enriched seed."""
    for ayah in enriched:
        ayah_ref = ayah.get("ayah", "")
        if ayah_ref not in verdicts:
            continue

        if "reviews" not in ayah:
            ayah["reviews"] = {}

        ayah["reviews"][reviewer_name] = verdicts[ayah_ref]

    return enriched


def save_enriched_seed(enriched: list[dict], path: Path) -> None:
    """Save enriched seed to JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for ayah in enriched:
            handle.write(json.dumps(ayah, ensure_ascii=False) + "\n")


def print_merge_summary(
    enriched: list[dict],
    reviewer_name: str,
) -> None:
    """Print summary of merge operation."""
    total_ayahs = len(enriched)
    ayahs_with_review = sum(
        1 for a in enriched if reviewer_name in a.get("reviews", {})
    )

    print(f"\n{'='*60}")
    print(f"Merged verdicts from: {reviewer_name}")
    print(f"Total ayahs: {total_ayahs}")
    print(f"Ayahs with verdict: {ayahs_with_review}")
    print(f"Coverage: {round((ayahs_with_review/total_ayahs)*100, 1)}%")

    # Verdict distribution
    verdicts = []
    for ayah in enriched:
        if reviewer_name in ayah.get("reviews", {}):
            v = ayah["reviews"][reviewer_name].get("verdict", "unknown")
            verdicts.append(v)

    from collections import Counter
    verdict_counts = Counter(verdicts)
    print("\nVerdict distribution:")
    for verdict, count in sorted(verdict_counts.items()):
        print(f"  {verdict}: {count}")

    # Agreement after merge
    agreeing = sum(
        1 for a in enriched
        if a.get("agreement", {}).get("consensus") > 1
    )
    print(f"\nAyahs with multi-reviewer agreement: {agreeing} / {total_ayahs}")
    print(f"{'='*60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge reviewer verdicts into validation model"
    )
    parser.add_argument(
        "--verdicts",
        type=Path,
        required=True,
        help="CSV file with verdicts (Ayah, Verdict, Notes)",
    )
    parser.add_argument(
        "--reviewer",
        type=str,
        required=True,
        help="Reviewer name (e.g., gpt4, claude, gemini)",
    )
    parser.add_argument(
        "--enriched",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data"
        / "validation"
        / "recovered_seed_with_validation.jsonl",
        help="Enriched seed JSONL file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path (default: overwrite input enriched file)",
    )
    args = parser.parse_args()

    # Load and merge
    enriched = load_enriched_seed(args.enriched)
    verdicts = load_verdicts_from_csv(args.verdicts)
    enriched = merge_verdicts(enriched, args.reviewer, verdicts)
    enriched = update_agreement_metrics(enriched)

    # Save
    output_path = args.output or args.enriched
    save_enriched_seed(enriched, output_path)

    print_merge_summary(enriched, args.reviewer)
    print(f"✓ Saved to: {output_path}")


if __name__ == "__main__":
    main()
