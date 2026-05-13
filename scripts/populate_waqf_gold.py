#!/usr/bin/env python3
"""
Populate gold_waqf_on_pause_v1 field for gold_wasl_v1 ayahs.

Appends an ayah-end marker (۝) to each Arabic text, runs the phonemizer
with waqf_on_pause=True, strips the trailing PAUSE token, and stores the
result in gold_waqf_on_pause_v1.

Known V1 limitation: madd arid lis-sukun is only extended when the madd is
the final symbol (e.g. هُدًى ۝). Mid-word madd before waqf-final consonant
(e.g. الرحيم, قدير) keeps tabii length. This is tracked in v1-backlog.md.

Usage:
  python3 scripts/populate_waqf_gold.py --enriched data/validation/recovered_seed_with_validation.jsonl
  python3 scripts/populate_waqf_gold.py --enriched ... --dry-run
  python3 scripts/populate_waqf_gold.py --enriched ... --ayah 1:1 2:2
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tilavet_phonemizer.phonemizer import Phonemizer, PhonemizerConfig

AYAH_END = "۝"

_waqf_phonemizer = Phonemizer(PhonemizerConfig(waqf_on_pause=True))


def waqf_phonemize(arabic: str) -> str:
    text = arabic.strip() + " " + AYAH_END
    result = _waqf_phonemizer.phonemize(text)
    symbols = result.symbols
    # Strip trailing PAUSE
    if symbols and symbols[-1] == "PAUSE":
        symbols = symbols[:-1]
    return " ".join(s for s in symbols if s)


def populate(enriched_path: Path, dry_run: bool, only_ayahs: list[str]) -> None:
    ayahs = []
    with open(enriched_path) as f:
        for line in f:
            ayahs.append(json.loads(line))

    updated = []
    skipped = []
    ineligible = []

    for ayah in ayahs:
        aid = ayah["ayah"]
        if only_ayahs and aid not in only_ayahs:
            continue

        if ayah.get("status") != "gold_wasl_v1":
            ineligible.append((aid, ayah.get("status", "unknown")))
            continue

        if ayah.get("gold_waqf_on_pause_v1") and not only_ayahs:
            skipped.append(aid)
            continue

        arabic = ayah.get("arabic", "")
        waqf_seq = waqf_phonemize(arabic)

        if not dry_run:
            ayah["gold_waqf_on_pause_v1"] = waqf_seq

        updated.append((aid, waqf_seq))

    if not dry_run:
        with open(enriched_path, "w") as f:
            for ayah in ayahs:
                f.write(json.dumps(ayah, ensure_ascii=False) + "\n")

    tag = "[DRY RUN] " if dry_run else ""
    print("=" * 60)
    print(f"{tag}WAQF GOLD POPULATION REPORT")
    print("=" * 60)
    print(f"\n{'Would populate' if dry_run else 'Populated'}: {len(updated)}")
    for aid, seq in updated:
        print(f"  {aid}: {seq}")

    if skipped:
        print(f"\nSkipped (already populated): {len(skipped)}")

    if ineligible:
        print(f"\nIneligible (not gold_wasl_v1): {len(ineligible)}")
        for aid, status in ineligible:
            print(f"  {aid}: {status}")

    print("=" * 60)
    if not dry_run and updated:
        print(f"✓ Saved to: {enriched_path}")


def main():
    parser = argparse.ArgumentParser(description="Populate gold_waqf_on_pause_v1")
    parser.add_argument("--enriched", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ayah", nargs="+", metavar="AYAH")
    args = parser.parse_args()

    populate(
        enriched_path=Path(args.enriched),
        dry_run=args.dry_run,
        only_ayahs=args.ayah or [],
    )


if __name__ == "__main__":
    main()
