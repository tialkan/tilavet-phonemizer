---
license: mit
library_name: tilavet
pipeline_tag: text2text-generation
language:
- ar
tags:
- quran
- phonemizer
- tajwid
- arabic
- phonetics
- speech-recognition
- forced-alignment
- audio-alignment
- ctc
- rule-based
inference: false
widget:
- text: "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
  example_title: Basmala
- text: "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ"
  example_title: Fatiha 2
- text: "قُلْ هُوَ ٱللَّهُ أَحَدٌ"
  example_title: Ikhlas 1
---

<!--
This file is uploaded as README.md to the Hugging Face Hub repository.
The YAML frontmatter above conforms to:
  https://huggingface.co/docs/hub/model-cards#model-card-metadata
The GitHub-flavored README is uploaded under GITHUB_README.md.
-->

# Tilavet Phonemizer v0.2.0

## Model description

*This project is a core component of the broader [Tilavet AI ecosystem](https://github.com/tialkan/Tilavet).*

Tilavet Phonemizer is a **rule-based** (not neural) Quranic Arabic phonemizer for the **Hafs an Asim** recitation. It converts fully-vowelled Uthmani-script Quran text into a deterministic phoneme sequence that respects tajwid rules. Intended use cases:

- Offline Quran audio alignment (CTC-based ASR systems).
- Word-by-word teleprompter highlight in mobile apps.
- Tajwid analysis and visualization.
- Generating "golden labels" for training acoustic models on Quranic speech.

## Method

Deterministic Python implementation walking the Arabic character stream, clustering letters + diacritics, and emitting phonemes per Hafs tajwid rules. No machine learning. ~1000 LOC, 108 unit tests (93% line coverage).

Tajwid coverage:

- Lâm shamsiyya / qamariyya / lafzatullah (tafhim/tarqiq via `L`/`l`).
- Nûn sakin / tanwin: ihfa, idgham (with and without ghunna), iqlab (combined into `n_g`/`m_g`).
- Mîm sakin: izhar, ihfa-i shafawi, idgham shafawi.
- Madd: tabii (2), muttasil/munfasil/silah-kubra (4), lazim/arıd/farq (6).
- Qalqalah: sughra (mid-word) and kubra (waqf) on ق ط ب ج د.
- Iltikā-ı sakîneyn (long vowel shortening before sakin).
- Idgham mutamathilain, mutajansayn, mutaqaribayn (within-word and cross-word).
- Hurûf-ı mukatta'a with inter-letter ikhfa/idgham seams.
- Multi-prefix vasla (`وَبِٱللَّهِ`, `أَبِٱلْكِتَابِ` etc.).
- Madd-i farq, madd-i lazim kalimi mukhaffaf (rare istifham + Allah / article forms).
- Hâ-i silah suğra/kubra cross-word upgrade.
- Tatweel-hamza orthography (`يَسْتَـْٔذِنُكَ`, `مَلْجَـًٔا` …).
- Vasl + Waqf as separate output modes; mushaf optional-pause markers are advisory.

Out of scope (V1):

- Râ tafhim/tarqiq (rule-level metadata only, no `R`/`r` split).
- Imâle, ishmâm, sekte (rare in Hafs; not encoded as separate phonemes).
- Idgham nâqıs vs kâmil mertebeleri.
- Riwāyat other than Hafs.

## Phoneme inventory

50 CTC classes total (incl. blank and PAUSE):

- 29 consonants (`'`, `b`, `t`, `th`, `j`, `H`, `kh`, `d`, `dh`, `r`, `z`, `s`, `sh`, `S`, `D`, `T`, `Z`, `3`, `gh`, `f`, `q`, `k`, `l`, `L`, `m`, `n`, `h`, `w`, `y`)
- 12 vowels (`a`, `i`, `u`, `aa`, `ii`, `uu`, `aa4`, `ii4`, `uu4`, `aa6`, `ii6`, `uu6`)
- 5 qalqalah variants (`b_qal`, `d_qal`, `j_qal`, `q_qal`, `T_qal`)
- 2 ghunna variants (`n_g`, `m_g`)
- `PAUSE`

Complete list in `data/ctc_classes.json`.

## Validation

- **108 unit tests** covering individual tajwid rules, public API surface, and CLI flags.
- **35-ayah gold seed** with multi-reviewer (GPT-4 + Claude + Gemini + 5 hafiz audits) verdicts.
- **Full-Quran sanity scan** (6236 ayet): 0 crashes, 0 empty word outputs, 0 four-consonant runs.
- All bugs identified by 5 independent hafız reviewers in the V1 audit have been fixed and re-verified.

## Limitations and risks

1. **Riwāyat scope.** This is Hafs an Asim. Other turuq will produce systematic mismatches.
2. **Pedagogical caveat.** Phoneme symbols are engineering tokens. They are **not** suitable as a reading aid for new learners — they are not transliteration and not a substitute for learning Arabic from a qualified teacher.
3. **Rule simplifications.** The merged `n_g` / `m_g` symbols treat ihfa, idgham-ma'al-ghunna, and iqlab as one acoustic family. ASR models will converge; rule-aware teaching tools should consult the rule metadata in `result.rules`.
4. **Religious sensitivity.** This tool does not pronounce or render Quran in any audible form. It produces engineering tokens for downstream acoustic systems. End-user applications must not present these tokens as a recitation aid.

## How to use

```python
from tilavet_phonemizer import Phonemizer
result = Phonemizer().phonemize("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ")
print(result.text)
# b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

See [README.md](README.md) for the full API.

## License

MIT. Free for commercial and personal use, attribution required. The phoneme convention itself is in the public domain — fork and extend.

## Citation

```bibtex
@software{tilavet_phonemizer_2026,
  title  = {Tilavet Phonemizer: Rule-based Quranic Arabic phonemizer (Hafs an Asim)},
  year   = {2026},
  version = {1.0},
  url    = {https://github.com/tialkan/tilavet-phonemizer}
}
```

## Acknowledgments

This release reflects the patient feedback of 5 independent hafız reviewers who challenged every architectural decision. Errors that remain are ours.
