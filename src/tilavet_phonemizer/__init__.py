"""Tilavet Quran phonemizer seed package.

Public API surface:

    Phonemizer            — main entry point. Construct once, call .phonemize().
    PhonemizerConfig      — flags controlling wasl/waqf/cross-ayah behavior.
    PhonemizationResult   — per-call output: symbols, words, rules.
    WordSpan              — per-token offsets into the phoneme stream.
    RuleHit               — single rule firing record (debugging/inspection).

See docs/phoneme-spec.md for the canonical phoneme inventory. The
`Phonemizer.phoneme_inventory()` classmethod returns the same list in code.
"""

from .phonemizer import (
    PhonemizationResult,
    Phonemizer,
    PhonemizerConfig,
    RuleHit,
    WordSpan,
)

__version__ = "0.2.0"

__all__ = [
    "PhonemizationResult",
    "Phonemizer",
    "PhonemizerConfig",
    "RuleHit",
    "WordSpan",
    "__version__",
]
