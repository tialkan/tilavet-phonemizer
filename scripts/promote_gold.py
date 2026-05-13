#!/usr/bin/env python3
"""
Promote ayahs from candidate_v1 to gold_wasl_v1 when consensus conditions are met.

Consensus rules:
  - 2 reviewers: both must be 'correct' (unanimous)
  - 3+ reviewers: majority must be 'correct', no 'error' verdicts allowed
  - Any 'error' verdict blocks promotion regardless of count

Usage:
  python3 scripts/promote_gold.py --enriched data/validation/recovered_seed_with_validation.jsonl
  python3 scripts/promote_gold.py --enriched ... --dry-run
  python3 scripts/promote_gold.py --enriched ... --ayah 1:1 2:2  # specific ayahs only
"""

import argparse
import json
from datetime import date
from pathlib import Path


def is_promotable(ayah: dict) -> tuple[bool, str]:
    reviews = ayah.get("reviews", {})
    verdicts = [v["verdict"] for v in reviews.values() if v.get("verdict")]

    if not verdicts:
        return False, "no verdicts"

    if "error" in verdicts:
        return False, "blocked by error verdict"

    n = len(verdicts)
    n_correct = verdicts.count("correct")
    n_unsure = verdicts.count("unsure")

    if n == 1:
        return False, "need at least 2 reviewers"

    if n == 2:
        if n_correct == 2:
            return True, "unanimous correct (2 reviewers)"
        return False, f"split: {verdicts}"

    # 3+ reviewers: majority correct, no error
    if n_correct > n / 2:
        return True, f"majority correct ({n_correct}/{n})"

    return False, f"no majority: correct={n_correct} unsure={n_unsure} of {n}"


def promote(enriched_path: Path, dry_run: bool, only_ayahs: list[str]) -> None:
    ayahs = []
    with open(enriched_path) as f:
        for line in f:
            ayahs.append(json.loads(line))

    promoted = []
    skipped_already = []
    ineligible = []

    for ayah in ayahs:
        aid = ayah["ayah"]
        if only_ayahs and aid not in only_ayahs:
            continue

        if ayah.get("status") == "gold_wasl_v1":
            skipped_already.append(aid)
            continue

        ok, reason = is_promotable(ayah)
        if ok:
            if not dry_run:
                ayah["status"] = "gold_wasl_v1"
                ayah["gold_wasl_v1"] = ayah.get("candidate_v1", "")
                ayah["promoted_date"] = str(date.today())
            promoted.append((aid, reason))
        else:
            ineligible.append((aid, reason))

    if not dry_run:
        with open(enriched_path, "w") as f:
            for ayah in ayahs:
                f.write(json.dumps(ayah, ensure_ascii=False) + "\n")

    tag = "[DRY RUN] " if dry_run else ""
    print("=" * 60)
    print(f"{tag}PROMOTION REPORT")
    print("=" * 60)
    print(f"\n{'Would promote' if dry_run else 'Promoted'}: {len(promoted)}")
    for aid, reason in promoted:
        print(f"  ✓ {aid}  ({reason})")

    if skipped_already:
        print(f"\nAlready gold: {len(skipped_already)}")
        for aid in skipped_already:
            print(f"  - {aid}")

    print(f"\nIneligible: {len(ineligible)}")
    for aid, reason in ineligible:
        print(f"  ✗ {aid}  ({reason})")

    print("=" * 60)
    if not dry_run and promoted:
        print(f"✓ Saved to: {enriched_path}")


def main():
    parser = argparse.ArgumentParser(description="Promote ayahs to gold_wasl_v1")
    parser.add_argument("--enriched", required=True, help="Path to enriched JSONL")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--ayah", nargs="+", metavar="AYAH", help="Only process these ayah IDs")
    args = parser.parse_args()

    promote(
        enriched_path=Path(args.enriched),
        dry_run=args.dry_run,
        only_ayahs=args.ayah or [],
    )


if __name__ == "__main__":
    main()
