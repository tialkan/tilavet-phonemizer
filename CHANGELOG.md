# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-15

### Added
- `PhonemizationResult.to_dict(include_rules=True)` for JSON-serializable
  output suitable for the downstream `tilavet-aligner` package.
- `PhonemizationResult.clean_symbols` property: phoneme list with silent
  (empty-string) entries removed.
- `PhonemizationResult.alignment_symbols()`, `alignment_words()`,
  `pause_markers()`, and `to_alignment_dict()` for the first downstream
  forced-alignment contract.
- `PhonemizationResult.word_symbols(k)` convenience slicer.
- `RuleHit.to_dict()` and `WordSpan.to_dict()` serializers.
- `Phonemizer.phoneme_inventory(include_metadata=False)` classmethod
  returning the canonical V1 CTC class list in stable order. Kept in sync
  with `data/ctc_classes.txt`.
- `Phonemizer.phonemize_many(iterable)` batch helper.
- `WordSpan` now exported from the package root.
- `__version__` exported from the package root.
- CLI flags:
  - `--json` — emit one JSON object per input.
  - `--rules-only` — emit just the rule trace.
  - `--waqf` — enable `waqf_on_pause`.
  - `--cross-ayah` — enable `cross_ayah_wasl`.
  - `--no-pause` — suppress PAUSE markers.
  - `--file PATH` — read inputs from a file (one ayah per line).
  - `-` positional — read inputs from stdin (one ayah per line).
  - `--print-inventory` — print the canonical phoneme inventory.
- `docs/aligner-mvp.md` documenting the first `tilavet-aligner` package
  contract and module breakdown.
- 30 new tests covering serialization, aligner target export, inventory,
  batch helper, and CLI flags.

### Changed
- Improved docstrings on `Phonemizer`, `PhonemizerConfig`, `PhonemizationResult`,
  `RuleHit`, `WordSpan` with attribute-level documentation.
- CLI rewritten for clarity; the original positional / `--rules` interface
  remains backwards-compatible.

### Notes
- Phoneme symbol set unchanged. Phoneme outputs for all existing inputs are
  byte-identical to the previous release; the 35-ayah recovered-seed
  reproducibility test still passes.
- Coverage 91% → 93%, tests 78 → 108.

## [0.1.1] - 2026-05-13 (prior unreleased work, now captured)
- Waqf/PAUSE variant mode (`waqf_on_pause`).
- Cross-ayah wasl/nun qutni (`cross_ayah_wasl`).
- Full-Quran phoneme index (`data/phoneme_index_full.json`).
- CTC class list (`data/ctc_classes.{json,txt}`).
- 35-ayah seed `gold_wasl_v1` + `gold_waqf_on_pause_v1` validation.

## [0.1.0] - 2026-05-09

### Added
- Initial release
- Rule-based Quran phonemizer
- Basic tajwid rules implementation
- Shadda handling
- Nun sakin/tanwin rules
- Mim sakin rules
- Lam shamsiyya/qamariyya handling
- Hamzat wasl handling
- Iltiqa al-sakinayn rules
- Qalqalah variants
- Madd variants (tabii, muttasil, munfasil, lazim)
- Ha kinayah silah rules
- Waw dagger-alif carrier handling
- Alef maqsura handling
- Huroof muqatta'at support
- PAUSE marker support
