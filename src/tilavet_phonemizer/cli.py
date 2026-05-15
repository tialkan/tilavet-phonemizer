"""Command-line entry point for quick phonemizer checks.

Examples:
    tilavet-phonemize "بِسْمِ ٱللَّهِ"
    tilavet-phonemize --rules "بِسْمِ ٱللَّهِ"
    tilavet-phonemize --rules-only "بِسْمِ ٱللَّهِ"
    tilavet-phonemize --json "بِسْمِ ٱللَّهِ"
    tilavet-phonemize --file input.txt
    echo "بِسْمِ" | tilavet-phonemize -
    tilavet-phonemize --waqf "ٱلرَّحِيمِ ۝"
    tilavet-phonemize --print-inventory
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from .phonemizer import Phonemizer, PhonemizerConfig


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tilavet-phonemize",
        description="Phonemize Quran Arabic text using the V1 Hafs ruleset.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Arabic text to phonemize. Pass '-' to read from stdin.",
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Read input from a file (UTF-8). One ayah per line.",
    )
    parser.add_argument(
        "--rules",
        action="store_true",
        help="After the phoneme line, print the rule trace.",
    )
    parser.add_argument(
        "--rules-only",
        action="store_true",
        help="Print only the rule trace (no phoneme line).",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit a JSON object per input instead of the plain phoneme line.",
    )
    parser.add_argument(
        "--waqf",
        action="store_true",
        help="Enable waqf_on_pause: apply waqf transformations at PAUSE marks.",
    )
    parser.add_argument(
        "--cross-ayah",
        action="store_true",
        help="Enable cross_ayah_wasl: suppress PAUSE and continue assimilation.",
    )
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Suppress the PAUSE marker even when stop signs are present.",
    )
    parser.add_argument(
        "--print-inventory",
        action="store_true",
        help="Print the canonical V1 phoneme inventory and exit.",
    )
    return parser


def _read_inputs(args: argparse.Namespace) -> list[str]:
    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            return [line.rstrip("\n") for line in handle if line.strip()]
    if args.text == "-":
        return [line.rstrip("\n") for line in sys.stdin if line.strip()]
    if args.text is None:
        raise SystemExit(
            "tilavet-phonemize: no input. Pass text positionally, --file PATH, or '-' for stdin."
        )
    return [args.text]


def _emit(phonemizer: Phonemizer, text: str, args: argparse.Namespace) -> None:
    result = phonemizer.phonemize(text)
    if args.as_json:
        data = result.to_dict(include_rules=args.rules or args.rules_only)
        if args.rules_only:
            data = {"rules": data["rules"]}
        print(json.dumps(data, ensure_ascii=False))
        return
    if not args.rules_only:
        print(result.text)
    if args.rules or args.rules_only:
        for hit in result.rules:
            print(f"{hit.symbol_index}\t{hit.symbol}\t{hit.rule}\t{hit.source}")


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.print_inventory:
        for sym in Phonemizer.phoneme_inventory(include_metadata=True):
            print(sym)
        return

    config = PhonemizerConfig(
        waqf_on_pause=args.waqf,
        cross_ayah_wasl=args.cross_ayah,
        emit_pause=not args.no_pause,
    )
    phonemizer = Phonemizer(config)
    for text in _read_inputs(args):
        _emit(phonemizer, text, args)


if __name__ == "__main__":
    main()
