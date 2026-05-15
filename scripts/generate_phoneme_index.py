#!/usr/bin/env python3
"""
Generate phoneme index JSON from gold JSONL.

Produces a structured index mapping surah/ayah/word → phoneme offsets.
Both wasl and waqf variants are included when available.
This file is consumed by the CTC decoder for Quran alignment.

Output format:
  {
    "version": "v1",
    "generated": "2026-05-12",
    "ayah_count": 35,
    "ayahs": [
      {
        "surah": 1, "ayah": 1, "label": "Fatiha 1",
        "arabic": "...",
        "wasl": {
          "symbols": [...],
          "words": [{"token": "...", "start": 0, "end": 5}, ...]
        },
        "waqf": {
          "symbols": [...],
          "words": [{"token": "...", "start": 0, "end": 5}, ...]
        }
      }
    ]
  }

Usage:
  python3 scripts/generate_phoneme_index.py
  python3 scripts/generate_phoneme_index.py \
    --enriched data/validation/recovered_seed_with_validation.jsonl
  python3 scripts/generate_phoneme_index.py --output data/phoneme_index.json
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tilavet_phonemizer.phonemizer import Phonemizer, PhonemizerConfig

_AYAH_END = "۝"

_wasl_phonemizer = Phonemizer(PhonemizerConfig(waqf_on_pause=False))
_waqf_phonemizer = Phonemizer(PhonemizerConfig(waqf_on_pause=True))


def _phonemize_wasl(arabic: str) -> dict:
    r = _wasl_phonemizer.phonemize(arabic)
    return {
        "symbols": r.symbols,
        "words": [{"token": w.token, "start": w.start, "end": w.end} for w in r.words],
    }


def _phonemize_waqf(arabic: str) -> dict:
    text = arabic.strip() + " " + _AYAH_END
    r = _waqf_phonemizer.phonemize(text)
    symbols = r.symbols
    words = r.words
    # Strip trailing PAUSE symbol and any word span that is only PAUSE
    if symbols and symbols[-1] == "PAUSE":
        symbols = symbols[:-1]
    return {
        "symbols": symbols,
        "words": [{"token": w.token, "start": w.start, "end": w.end} for w in words
                  if w.token != _AYAH_END],
    }


def _parse_ayah_id(ayah_id: str) -> tuple[int, int]:
    parts = ayah_id.split(":")
    return int(parts[0]), int(parts[1])


def generate(enriched_path: Path, output_path: Path) -> None:
    ayahs_raw = []
    with open(enriched_path) as f:
        for line in f:
            ayahs_raw.append(json.loads(line))

    # Only include gold_wasl_v1 ayahs
    gold = [a for a in ayahs_raw if a.get("status") == "gold_wasl_v1"]
    gold.sort(key=lambda a: _parse_ayah_id(a["ayah"]))

    entries = []
    for a in gold:
        surah, ayah_num = _parse_ayah_id(a["ayah"])
        arabic = a["arabic"]

        entry = {
            "surah": surah,
            "ayah": ayah_num,
            "label": a.get("label", ""),
            "arabic": arabic,
            "wasl": _phonemize_wasl(arabic),
        }

        if a.get("gold_waqf_on_pause_v1"):
            entry["waqf"] = _phonemize_waqf(arabic)

        entries.append(entry)

    index = {
        "version": "v1",
        "generated": str(date.today()),
        "ayah_count": len(entries),
        "ayahs": entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"✓ Phoneme index written: {output_path}")
    print(f"  Ayahs: {len(entries)}")

    # Symbol inventory
    all_syms = set()
    for e in entries:
        all_syms.update(s for s in e["wasl"]["symbols"] if s and s != "PAUSE")
        if "waqf" in e:
            all_syms.update(s for s in e["waqf"]["symbols"] if s and s != "PAUSE")
    print(f"  Unique symbols (excl. PAUSE): {len(all_syms)}")


def main():
    parser = argparse.ArgumentParser(description="Generate phoneme index JSON")
    parser.add_argument(
        "--enriched",
        default="data/validation/recovered_seed_with_validation.jsonl",
    )
    parser.add_argument("--output", default="data/phoneme_index.json")
    args = parser.parse_args()

    generate(Path(args.enriched), Path(args.output))


if __name__ == "__main__":
    main()
