#!/usr/bin/env python3
"""Generate a Hafiz review Markdown report from a JSONL validation seed."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from tilavet_phonemizer import Phonemizer  # noqa: E402


def load_examples(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def render_report(examples: list[dict]) -> str:
    phonemizer = Phonemizer()
    lines: list[str] = [
        "# Tilavet Phonemizer V1 - Hafiz Validation Report",
        "",
        "> Generated from `data/validation/recovered_seed.jsonl`.",
        "> Mode: Hafs / Asim, wasl candidate, not yet human-verified.",
        "",
        "## Instructions",
        "",
        "For each ayah, compare the Arabic text with the current candidate output.",
        "Only fill the note when there is an error or uncertainty.",
        "",
        "## Ayat",
        "",
    ]

    for example in examples:
        result = phonemizer.phonemize(example["arabic"])
        lines.extend(
            [
                f"### {example['ayah']} - {example.get('label', '')}".rstrip(),
                "",
                "**Arabic:**",
                f"> {example['arabic']}",
                "",
                "**Candidate output:**",
                "```",
                result.text,
                "```",
                "",
                "**Stored candidate:**",
                "```",
                example.get("candidate_v1", ""),
                "```",
                "",
                "**Rule hits:**",
            ]
        )

        for hit in result.rules:
            if hit.symbol:
                lines.append(f"- `{hit.symbol}` -> {hit.rule}")

        lines.extend(
            [
                "",
                "**Hafiz note:**",
                "```text",
                "Accuracy: yes / no / unsure",
                "Location:",
                "Current:",
                "Expected:",
                "Rule:",
                "Note:",
                "```",
                "",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed",
        type=Path,
        default=ROOT / "data" / "validation" / "recovered_seed.jsonl",
        help="JSONL seed file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional Markdown output path. Prints to stdout when omitted.",
    )
    args = parser.parse_args()
    report = render_report(load_examples(args.seed))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
