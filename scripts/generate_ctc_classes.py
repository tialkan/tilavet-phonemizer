#!/usr/bin/env python3
"""
Generate CTC class list from phoneme-spec.md

This script reads the phoneme specification and generates a CTC class list
for use in speech recognition models.
"""

import re
from pathlib import Path


def parse_phoneme_spec(spec_path: Path) -> dict[str, list[str]]:
    """Parse phoneme-spec.md and extract phoneme classes."""
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()

    classes = {
        "consonants": [],
        "vowels": [],
        "variants": [],
    }

    current_section = None

    for line in content.split("\n"):
        line = line.strip()

        if line == "## Konsonantlar":
            current_section = "consonants"
        elif line == "## Vokaller":
            current_section = "vowels"
        elif line == "## Varyantlar":
            current_section = "variants"
        elif line.startswith("##"):
            current_section = None
        elif current_section:
            if current_section == "consonants" and line.startswith("| "):
                # Parse table rows
                parts = line.split("|")
                if len(parts) >= 3:
                    symbol = parts[1].strip()
                    if symbol and symbol != "Symbol":
                        classes["consonants"].append(symbol)
            elif current_section == "vowels" and line.startswith("- "):
                # Parse list items like "- `a`, `i`, `u`: kisa hareke"
                matches = re.findall(r"`([^`]+)`", line)
                for match in matches:
                    symbols = match.split(", ")
                    classes["vowels"].extend([s.strip() for s in symbols])
            elif current_section == "variants" and line.startswith("- "):
                # Parse list items like "- `n_g`: nun/tanwin ghunna"
                matches = re.findall(r"`([^`]+)`", line)
                for match in matches:
                    classes["variants"].append(match)

    return classes


def generate_ctc_classes(classes: dict[str, list[str]]) -> list[str]:
    """Generate complete CTC class list.
    
    Note: PAUSE is NOT included as a CTC class per phoneme-spec.md:
    "PAUSE ana CTC fonem sinif listesine zorunlu fonem olarak dahil edilmez."
    """
    ctc_classes = []

    # Add consonants
    ctc_classes.extend(sorted(classes["consonants"]))

    # Add vowels
    ctc_classes.extend(sorted(classes["vowels"]))

    # Add variants (exclude PAUSE and BREATH as they are metadata)
    for variant in sorted(classes["variants"]):
        if variant not in ["PAUSE", "BREATH"]:
            ctc_classes.append(variant)

    return ctc_classes


def main():
    spec_path = Path(__file__).parent.parent / "docs" / "phoneme-spec.md"
    output_path = Path(__file__).parent.parent / "data" / "ctc_classes.txt"

    classes = parse_phoneme_spec(spec_path)
    ctc_classes = generate_ctc_classes(classes)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# CTC Class List for Tilavet Phonemizer\n")
        f.write("# Generated from docs/phoneme-spec.md\n")
        f.write("# Note: PAUSE is not included as a CTC class (metadata only)\n\n")
        for i, cls in enumerate(ctc_classes):
            f.write(f"{i}\t{cls}\n")

    print(f"CTC class list generated: {output_path}")
    print(f"Total classes: {len(ctc_classes)}")
    print("\nClasses:")
    for cls in ctc_classes:
        print(f"  {cls}")


if __name__ == "__main__":
    main()
