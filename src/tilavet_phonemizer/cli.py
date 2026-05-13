"""Command-line entry point for quick phonemizer checks."""

from __future__ import annotations

import argparse

from .phonemizer import Phonemizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Phonemize Quran Arabic text.")
    parser.add_argument("text", help="Arabic text to phonemize")
    parser.add_argument("--rules", action="store_true", help="Print rule hits after symbols")
    args = parser.parse_args()

    result = Phonemizer().phonemize(args.text)
    print(result.text)

    if args.rules:
        for hit in result.rules:
            print(f"{hit.symbol_index}\t{hit.symbol}\t{hit.rule}\t{hit.source}")


if __name__ == "__main__":
    main()
