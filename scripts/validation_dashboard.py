#!/usr/bin/env python3
"""Generate a validation status dashboard from enriched seed.

Shows:
- Validation status distribution (candidate_v1, gold_wasl_v1, etc.)
- Reviewer coverage
- Agreement metrics
- Quality indicators
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


def load_enriched_seed(path: Path) -> list[dict]:
    """Load enriched JSONL."""
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def generate_dashboard_markdown(enriched: list[dict]) -> str:
    """Generate a markdown dashboard."""
    lines = [
        "# Tilavet Phonemizer - Validation Dashboard",
        "",
        f"Generated: {__import__('datetime').datetime.now().isoformat()}",
        "",
    ]

    # Basic stats
    lines.extend([
        "## Overview",
        "",
        f"Total ayahs: {len(enriched)}",
        "",
    ])

    # Status distribution
    status_counts = Counter(a.get("status", "unknown") for a in enriched)
    lines.extend([
        "## Validation Status",
        "",
    ])
    for status, count in sorted(status_counts.items()):
        percent = round((count / len(enriched)) * 100, 1)
        lines.append(f"- {status}: {count} ({percent}%)")

    # Reviewer coverage
    lines.extend([
        "",
        "## Reviewer Coverage",
        "",
    ])
    all_reviewers = set()
    for ayah in enriched:
        all_reviewers.update(ayah.get("reviews", {}).keys())

    if all_reviewers:
        for reviewer in sorted(all_reviewers):
            coverage = sum(
                1 for a in enriched if reviewer in a.get("reviews", {})
            )
            percent = round((coverage / len(enriched)) * 100, 1)
            lines.append(f"- {reviewer}: {coverage} / {len(enriched)} ({percent}%)")
    else:
        lines.append("- No reviewers have voted yet")

    # Verdict distribution (if any)
    all_verdicts = []
    for ayah in enriched:
        for review in ayah.get("reviews", {}).values():
            if review.get("verdict"):
                all_verdicts.append(review["verdict"])

    if all_verdicts:
        lines.extend([
            "",
            "## Verdict Distribution",
            "",
        ])
        verdict_counts = Counter(all_verdicts)
        for verdict, count in sorted(verdict_counts.items()):
            percent = round((count / len(all_verdicts)) * 100, 1)
            lines.append(f"- {verdict}: {count} ({percent}%)")

    # Agreement metrics
    lines.extend([
        "",
        "## Agreement Metrics",
        "",
    ])

    ayahs_with_consensus = sum(
        1 for a in enriched
        if a.get("agreement", {}).get("consensus", 0) > 1
    )
    lines.append(f"- Ayahs with multi-reviewer consensus: {ayahs_with_consensus} / {len(enriched)}")

    # Agreement percentages
    consensus_percents = [
        a.get("agreement", {}).get("percent", 0)
        for a in enriched
        if a.get("reviews", {})
    ]
    if consensus_percents:
        avg_agreement = round(sum(consensus_percents) / len(consensus_percents), 1)
        lines.append(f"- Average agreement level: {avg_agreement}%")

    # Error detection
    lines.extend([
        "",
        "## Issues",
        "",
    ])

    errors_found = sum(1 for a in enriched if any(
        r.get("verdict") == "error"
        for r in a.get("reviews", {}).values()
    ))

    unsure_found = sum(1 for a in enriched if any(
        r.get("verdict") == "unsure"
        for r in a.get("reviews", {}).values()
    ))

    lines.append(f"- Errors detected: {errors_found}")
    lines.append(f"- Unsure verdicts: {unsure_found}")
    lines.append(f"- Clean verdicts (correct): {len(all_verdicts) - errors_found - unsure_found}")

    # Next steps
    lines.extend([
        "",
        "## Next Steps",
        "",
    ])

    if not all_reviewers:
        lines.append("1. **Send review batch to LLM hafiz reviewers**")
        lines.append("   - Use `data/validation/llm_hafiz_review_full.md` as template")
        lines.append("   - Recommended reviewers: GPT-4, Claude, Gemini, Qwen")
    elif ayahs_with_consensus < len(enriched) * 0.9:
        lines.append("1. **Resolve low-consensus ayahs**")
        lines.append("   - Send disputed cases to additional senior reviewer")
    else:
        lines.append("1. **Promote `candidate_v1` to `gold_wasl_v1`**")
        lines.append("   - Run: `python3 scripts/promote_status.py --status gold_wasl_v1`")

    lines.append("")
    return "\n".join(lines)


def print_dashboard_table(enriched: list[dict]) -> None:
    """Print a compact ASCII table of validation status."""
    print("\n" + "="*80)
    print("VALIDATION STATUS TABLE")
    print("="*80)
    print(f"{'Ayah':<10} {'Label':<30} {'Status':<20} {'Reviews':<10}")
    print("-"*80)

    for ayah in enriched[:35]:  # Show all 35
        label = ayah.get("label", "")[:28]
        status = ayah.get("status", "unknown")
        reviews = ", ".join(ayah.get("reviews", {}).keys()) or "none"
        print(f"{ayah.get('ayah'):<10} {label:<30} {status:<20} {reviews:<10}")

    print("="*80 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate validation status dashboard"
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
        help="Optional markdown output path",
    )
    parser.add_argument(
        "--table",
        action="store_true",
        help="Also print ASCII table",
    )
    args = parser.parse_args()

    enriched = load_enriched_seed(args.enriched)
    dashboard = generate_dashboard_markdown(enriched)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dashboard + "\n", encoding="utf-8")
        print(f"✓ Dashboard saved to: {args.output}")
    else:
        print(dashboard)

    if args.table:
        print_dashboard_table(enriched)


if __name__ == "__main__":
    main()
