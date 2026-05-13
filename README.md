# Tilavet Phonemizer

**Rule-based Quranic Arabic phonemizer for the Hafs an Asim recitation.**

*This project is a core component of the broader [Tilavet AI ecosystem](https://github.com/tialkan/Tilavet).*

Converts fully-vowelled Uthmani-script Quran text into a deterministic phoneme sequence that respects tajwid rules. Designed as a "golden label" for training acoustic speech models, aligning audio recitations to text, and building Quran-only ASR / teleprompter applications.

[![Tests](https://img.shields.io/badge/tests-78%20passing-green)](.) [![Quran coverage](https://img.shields.io/badge/Quran-6236%20ayahs-blue)](.) [![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## What it does

```
بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
                 │
                 ▼
   b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

Two output modes:

| Mode | Use case | Example (الرحيم) |
|---|---|---|
| **Wasl** (connected) | Within an ayah, normal flow | `r r a H ii m i` |
| **Waqf** (stop) | At end-of-ayah, with tajwid transformations applied | `r r a H ii6 m` |

Waqf mode applies: tanwin drop, taa-marbuta `t` → `h`, madd-i arıd lis-sukun (6 harakah), qalqalah kubra on final ق ط ب ج د.

---

## Why this project

Quran applications need to align speech recordings to Quran text at the **word** (and even **letter**) level — for teleprompter highlight, hafız training, tajwid analysis. The standard approach is to train a CTC acoustic model that emits phoneme posteriors, then decode against a known Quran phoneme map.

For Quranic Arabic specifically, this phoneme map needs to encode tajwid rules (ikhfa, idgham, qalqalah, madd lengths, lafzatullah tafhim/tarqiq, …) — not just letter identity. There is no open-source tool that does this end-to-end for the full Hafs an Asim Mushaf. This project fills that gap.

**Free, open source, no commercial intent.** Intended as an ummah service.

---

## Install

```bash
# From PyPI (planned)
pip install tilavet-phonemizer

# From source
git clone https://github.com/tilavet/tilavet-phonemizer
cd tilavet-phonemizer
pip install -e .
```

Requires Python 3.9+. No runtime dependencies.

---

## Usage

### Command line

```bash
tilavet-phonemize "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
# → b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

### Python API

```python
from tilavet_phonemizer import Phonemizer, PhonemizerConfig

# Wasl (default)
p = Phonemizer()
result = p.phonemize("بِسْمِ ٱللَّهِ")
print(result.text)
# b i s m i l l aa h i

# Per-word offsets (for alignment / highlighting)
for word in result.words:
    syms = result.symbols[word.start:word.end]
    print(f"{word.token:20} → {' '.join(syms)}")
# بِسْمِ              → b i s m i
# ٱللَّهِ              → l l aa h i

# Waqf (end-of-ayah)
p_waqf = Phonemizer(PhonemizerConfig(waqf_on_pause=True))
print(p_waqf.phonemize("ٱلرَّحِيمِ ۝").text)
# r r a H ii6 m PAUSE

# Cross-ayah connected (nun qutni)
p_cross = Phonemizer(PhonemizerConfig(cross_ayah_wasl=True))
```

### Inspecting tajwid rules per phoneme

```python
result = p.phonemize("هُم مُّصِيبَةٌۭ")
for hit in result.rules:
    print(f"  {result.symbols[hit.symbol_index]}  ← {hit.rule}")
# m_g  ← idgham_shafawi
# m    ← shadda
# u    ← vowel
# ...
```

---

## Symbol convention

### Consonants

| Sym | Letter | Sym | Letter | Sym | Letter | Sym | Letter |
|---|---|---|---|---|---|---|---|
| `'` | ء (hamza) | `b` | ب | `t` | ت | `th` | ث |
| `j` | ج | `H` | ح | `kh` | خ | `d` | د |
| `dh` | ذ | `r` | ر | `z` | ز | `s` | س |
| `sh` | ش | `S` | ص | `D` | ض | `T` | ط |
| `Z` | ظ | `3` | ع | `gh` | غ | `f` | ف |
| `q` | ق | `k` | ك | `l` | ل (tarqiq) | `L` | **lafzatullah tafhim** |
| `m` | م | `n` | ن | `h` | ه | `w` | و (cons.) |
| `y` | ي (cons.) | | | | | | |

### Vowels & madd

| Symbol | Meaning |
|---|---|
| `a` `i` `u` | Short vowels (fatha, kasra, damma) |
| `aa` `ii` `uu` | Madd-i tabii (2 harakah) |
| `aa4` `ii4` `uu4` | 4-harakah madd (muttasil, munfasil, silah-kubra) |
| `aa6` `ii6` `uu6` | 6-harakah madd (lazim, arıd lis-sukun, farq) |

### Tajwid variants

| Symbol | Meaning |
|---|---|
| `n_g` | Nun/tanwin ihfa OR idgham ma'al-ghunna |
| `m_g` | Mim idgham shafawi, iqlab, or ihfa shafawi |
| `q_qal` `T_qal` `b_qal` `j_qal` `d_qal` | Qalqalah on sakin ق ط ب ج د |
| `PAUSE` | Mushaf optional-stop marker (advisory, does not break wasl rules) |

### Design rules

- `L` only for lafzatullah tafhim. After kasra it becomes tarqiq → `l`. (`بِسْمِ ٱللَّهِ` → `l l aa h i`, `تَٱللَّهِ` → `L L aa h i`.)
- Tanwin + lam/ra idgham bila ghunna: the `n` elides (`هُدًى لِّلْمُتَّقِينَ` → `h u d a l l ...`).
- Dagger alif / small alif is a single long vowel `aa` (not `a aa`).
- Hamza-i kat' is always pronounced; never dropped by wasl.
- `كُفُوًا` is rendered with waw, not hamza: `k u f u w a n`.
- Muqattaat letters apply inter-letter ihfa/idgham: `كهيعص` → `... 3 aa6 y n_g S aa6 d`, `الم` → `... l aa6 m_g m ii6 m`.
- Mushaf optional-pause markers (ۖ ۚ ۛ ۗ) emit `PAUSE` but **do not** block cross-word ikhfa/idgham/iqlab in wasl mode.
- In waqf mode: tanwin drops, taa-marbuta `t` → `h`, sakin qalqalah harf gets `_qal`, final tabii madd becomes 6-harakah arıd.

Full specification: [docs/phoneme-spec.md](docs/phoneme-spec.md).

---

## What the symbols do **not** capture (V1 scope)

- **Ra tafhim/tarqiq** (no `R`/`r` split — rule available in `result.rules` metadata only)
- **Imala, ishmam, sakta** (rare in Hafs; flagged via U+06EA as plain `i` for the `مَجْر۪ىٰهَا` case)
- **Idgham naqis vs kamil** (always rendered as complete assimilation)
- **PAUSE typing** (lazim ۚ vs jaiz ۖ vs mutekarrir ۛ — distinction in metadata, single `PAUSE` symbol in output)

These are intentional simplifications for V1 to keep the CTC class set compact (50 classes incl. blank + PAUSE). All decisions documented in [docs/v1-backlog.md](docs/v1-backlog.md).

---

## Validation

The V1 release was reviewed by **5 independent hafız reviewers** (3 LLM-based, 2 human-style detailed audits) over 60+ ayet samples. All flagged bugs have been fixed; their feedback is preserved in [docs/llm-review-synthesis.md](docs/llm-review-synthesis.md).

A 35-ayah gold dataset (`gold_wasl_v1` + `gold_waqf_on_pause_v1`) lives at `data/validation/recovered_seed_with_validation.jsonl`. Each ayet has multi-reviewer verdicts and aggregate consensus.

Full-Quran sanity scan (6236 ayet):

```
Crashes:       0
Empty output:  0
4+ consecutive consonant runs:  0
3-consonant runs:               4  (all are correct: muqattaat ikhfa + rare orthography)
```

---

## Pre-computed outputs

`data/phoneme_index_full.json` (≈14 MB): every ayet of the Quran processed by V1, with both wasl and waqf phoneme sequences and per-word offsets. Ready to drop into a decoder.

```json
{
  "version": "v1.0",
  "source": "alquran.cloud/quran-uthmani",
  "ayah_count": 6236,
  "ayahs": [
    {
      "surah": 1, "ayah": 1,
      "arabic": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
      "wasl": {
        "symbols": ["b","i","s","m","i","l","l","aa","h","i", ...],
        "words":   [{"token":"بِسْمِ","start":0,"end":5}, ...]
      },
      "waqf": { ... }
    }
  ]
}
```

CTC class file (`data/ctc_classes.json`) lists the 50 phonemes (incl. blank and PAUSE) in fixed order for acoustic-model training.

---

## Testing

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
# Ran 78 tests in 0.012s
# OK
```

For development:

```bash
pip install -e ".[dev]"
pytest tests/ -v --cov=src/tilavet_phonemizer
```

---

## Scope and disclaimers

- **Riwāyat:** Hafs an Asim only (`الرواية`). Other turuq (Shâtibî, Tayyibe, …) are not supported by this V1.
- **Religious authority:** This tool is a computational representation, not a tajwid teacher. Phoneme symbols are engineering tokens, **not** a replacement for traditional learning under a qualified teacher. Latin transliteration is not displayed to end-users by design.
- **Source text:** Uthmani Mushaf (via `alquran.cloud`). Variant orthography is normalized to standard Unicode forms.

---

## Roadmap (post-V1)

- Râ tafhim/tarqiq as a metadata layer
- Variant-graph output for PAUSE branches (wasl vs waqf paths)
- **Multilingual Support:** Documentation and usage guides will be expanded to Arabic, English, Urdu, Indonesian, Turkish, and French across all platforms (GitHub, Hugging Face, PyPI).
- Acoustic model integration example (wav2vec2 / Whisper fine-tune)
- Extension hooks for Shâtibî / Tayyibe rules

See [docs/v1-backlog.md](docs/v1-backlog.md) for the complete backlog.

---

## License

[MIT](LICENSE). Free for commercial and personal use, attribution required.

---

## Citation

```bibtex
@software{tilavet_phonemizer_2026,
  title  = {Tilavet Phonemizer: Open-source Quran phonemizer for Hafs an Asim},
  year   = {2026},
  url    = {https://github.com/tilavet/tilavet-phonemizer}
}
```

---

## Acknowledgments

Built with the guidance of multiple hafız reviewers who took the time to read every output sample and challenge every architectural decision. May Allah accept their effort.
