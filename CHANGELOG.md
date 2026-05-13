# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial V1 rule-based phonemizer core (833 lines)
- 32 unit tests with full coverage
- 35 ayah validation seed
- V1 phoneme symbol convention
- LLM hafiz review infrastructure
- CLI interface (`tilavet-phonemize`)
- Python API with `Phonemizer` class
- Documentation (architecture, phoneme-spec, hafiz-validation)

### Planned
- Waqf/PAUSE variant mode
- Cross-ayah wasl/nun qutni
- Quran-wide export
- CTC class list generation
- Hugging Face publication

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
