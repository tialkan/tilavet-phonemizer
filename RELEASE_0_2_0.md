# Tilavet Phonemizer 0.2.0 — Release & Publication Plan

Bu dosya 0.2.0 surumunun GitHub + PyPI + Hugging Face yayinlama akisini
adim adim tarif eder, ardindan post-release yol haritasini ozetler.

## 0.2.0'da Ne Var

**Onceki sürum:** 0.1.1 (Mayis 2026 baslari) — V1 wasl + waqf_on_pause +
cross_ayah_wasl tum kurallar, 78 test, %91 coverage, 50-class CTC listesi.

**0.2.0 yeniligi (additive, fonem ciktilari aynidir):**

- Public API: `to_dict()`, `to_alignment_dict()`, `clean_symbols`,
  `alignment_symbols()`, `alignment_words()`, `pause_markers()`,
  `word_symbols(k)`, `phoneme_inventory()`, `phonemize_many()`, `WordSpan`
  export, `__version__` export.
- CLI: `--json`, `--rules-only`, `--waqf`, `--cross-ayah`, `--no-pause`,
  `--file`, `-` stdin, `--print-inventory`.
- Yeni doc: `docs/aligner-mvp.md`.
- Sibling paket iskeleti: `../tilavet-aligner/` (contract dogrudan
  `to_alignment_dict()` tukketir).
- Testler: 78 → 108, coverage %91 → %93.

35 ayetlik `recovered_seed.jsonl` reproducibility testi gecmeye devam ediyor —
fonem ciktilarinda byte-level degisiklik yok.

## Yayinlama Adim Adim

### 1. Repo Hazirligi (yerel)

```bash
cd "/Users/baris/Documents/GitHub/Tilavet/Tilavet Phonemizer"

# Lint + test (lokal smoke test):
PYTHONPATH=src python3 -m pytest tests/ -v
PYTHONPATH=src python3 -m pytest tests/ --cov=src/tilavet_phonemizer --cov-report=term

# Wheel + sdist:
rm -rf dist build src/*.egg-info
python3 -m build

# Twine sanity:
python3 -m twine check dist/*
```

Beklenen sonuc:

```
============== 108 passed, 35 subtests passed in ~0.07s
TOTAL  872  71  92%
PASSED   tilavet_phonemizer-0.2.0-py3-none-any.whl
PASSED   tilavet_phonemizer-0.2.0.tar.gz
```

### 2. GitHub Release

```bash
# Commit + push:
git add -A
git commit -m "release: v0.2.0 (public API + aligner contract)"
git push origin main

# Tag + release:
git tag -a v0.2.0 -m "Tilavet Phonemizer 0.2.0"
git push origin v0.2.0

# GitHub release notes icin CHANGELOG'daki [0.2.0] bolumunu kullan:
# https://github.com/tialkan/tilavet-phonemizer/releases/new?tag=v0.2.0
```

Release notlari icin temel cumleler (kopyala):

> **0.2.0 — Public API + Aligner Contract** (Mayis 2026)
>
> Bu surum fonem davranisini koruyarak downstream araclara `tilavet-aligner`
> ve teleprompter UI'lari icin temiz bir public API ekler.
>
> ### Highlights
> - `PhonemizationResult.to_alignment_dict()` — CTC hedef sekansi + PAUSE
>   metadata + remap word offsets. Forced alignment paketi `tilavet-aligner`
>   bu kontrati tuketir.
> - `Phonemizer.phoneme_inventory()` — stable CTC class listesi.
> - `Phonemizer.phonemize_many()` — batch helper.
> - CLI `--json`, `--rules-only`, `--waqf`, `--cross-ayah`, `--no-pause`,
>   `--file`, stdin `-`, `--print-inventory`.
> - 108 test (78'den), %93 coverage. 35-ayet seed reproducibility korunuyor.
>
> **Backwards compatible.** Eski API'ler aynen calisiyor; eklenenler ek.

### 3. PyPI Yayini

```bash
# Test PyPI'de smoke (onerilir):
python3 -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ tilavet-phonemizer==0.2.0
tilavet-phonemize "بِسْمِ ٱللَّهِ"

# Production PyPI:
python3 -m twine upload dist/*
```

Kimlik dogrulama icin `~/.pypirc` veya `TWINE_USERNAME=__token__` +
`TWINE_PASSWORD=pypi-...` cevre degiskenleri kullanilabilir.

Yayindan sonra:

```bash
pip install --upgrade tilavet-phonemizer
python3 -c "import tilavet_phonemizer; print(tilavet_phonemizer.__version__)"
# 0.2.0
```

### 4. Hugging Face Hub

```bash
# Login (eger HF_TOKEN env var set degilse):
huggingface-cli login

# Yukleme scripti zaten var:
python3 scripts/upload_to_hf.py --repo-id baristiran/tilavet-phonemizer
```

`scripts/upload_to_hf.py` zaten su dosyalari aktariyor:
`MODEL_CARD.md`, `README.md`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`,
`docs/phoneme-spec.md`, `docs/waqf-pause-decision.md`, `data/ctc_classes.txt`,
`src/`, `tests/`.

Model card (`MODEL_CARD.md`) 0.2.0 metriklerine guncellendi (108 test,
%93 coverage).

### 5. NPM (TypeScript Port)

TS portu `ts/` altinda; ayri bir publish akisi:

```bash
cd ts
npm version 0.2.0
npm test
npm publish --access public
```

**Onemli:** TS port'a henuz `to_alignment_dict()`, `--rules-only`,
`phoneme_inventory()` eklenmedi. NPM 0.2.0'i publish etmeden once feature
parity istemiyorsak `ts/package.json`'i 0.1.x serisinde tutmak en temizi.
Aksi takdirde Python ve TS portlarinin API'leri ayrismaya baslar.

## Post-0.2.0 Yol Haritasi

### Yakin Vade (sonraki 1-2 hafta) — tilavet-aligner MVP

Bagimsiz repo: `/Users/baris/Documents/GitHub/Tilavet/tilavet-aligner`

Mevcut iskelet (`docs/aligner-mvp.md`'de detayli):

```
src/tilavet_aligner/
  contract.py     ✅ to_alignment_dict() payload dogrulama
  posterior.py    ✅ sparse/dense/.npy adapters
  ctc.py          ✅ vocabulary, log-prob normalization
  viterbi.py      ✅ monotonic + CTC blank-aware
  word_spans.py   ✅ symbol frames → word frames
  cli.py          ✅ JSON target + posterior input
tests/            ✅ 35 test, hepsi gecer
examples/
  synthetic_alignment.py  ✅ phonemizer + synthetic CTC demo
```

Sonraki adimlar:

1. **Gercek bir Wav2Vec2 modeliyle smoke test**
   - `facebook/wav2vec2-xlsr-arabic-960h` indir.
   - Hafiz okumasi olan kisa bir ses dosyasi al (FaceTime/iPhone kayit yeterli).
   - `tilavet-phonemizer` → ayah JSON → `tilavet-aligner` → word timestamps.
   - Sonuc kalitesini elle dogrula.
2. **Toy CTC modeli + sentetik veri**
   - 5-10 ayetlik mikro dataset (sen kaydet, ben hizalayim).
   - Toy CTC head egit, alignment ciktisini gold ile karsilastir.
3. **`tilavet-aligner` PyPI 0.1.0 release**
   - Aligner kendi pyproject ile bagimsiz olarak yayinlanabilir.
   - Bagimliliklar: `tilavet-phonemizer>=0.2.0`, `numpy`, opsiyonel `torch`.

### Orta Vade (3-6 hafta) — iOS Teleprompter MVP

Bu noktada elimizde olacak:
- Python phonemizer ✅ (offline-ready algoritma)
- TypeScript port ✅ (gerekirse RN/Web kullanimi icin)
- Aligner MVP ✅ (Python prototype)

iOS hedefi:

1. **CoreML CTC model**
   - Wav2Vec2'yi fine-tune et veya kucuk bir conformer-CTC bastan egit.
   - 50 sinif (blank + 49 Tilavet fonem). `data/ctc_classes.txt` direkt
     vocabulary olarak kullanilabilir.
   - CoreML'e export. iPhone 11+ uzerinde streaming inference smoke test.
2. **Swift aligner**
   - Python `tilavet-aligner` algoritmasini Swift'e port et.
   - Veya Python algoritmasini ONNX/CoreML olarak embed et (Viterbi runtime
     hafif oldugu icin saf Swift muhtemelen yeterli).
3. **Teleprompter UI**
   - Yukari kaydirma + aktif kelime highlight.
   - `data/phoneme_index_full.json` bundle olarak embed (yaklasik 14 MB,
     gzip sonrasi 3-4 MB). Tum Kuran offline.
4. **Hafiz hata modu**
   - Substitution / deletion / insertion detection: aligner skoru +
     `result.rules` ile gerekce gosterilebilir.

### Uzun Vade (3+ ay) — V2 Surumler

- **Râ tafhim/tarqiq metadata layer** (yeni sinif degil, `rules` katmaninda).
- **Variant graph** PAUSE branchleri (wasl / waqf / cross-ayah hep ayni
  encoded structurde).
- **Diger riwāyat** (Warsh, Qalun) icin parametrik rule set: `Phonemizer(
  riwayat="warsh")`.
- **TR/AR/EN/UR/ID/FR dokumantasyon** (orkestra.md'deki cok dilli plan).
- **Tajwid coaching modu**: ihfa/idgham/qalqalah'in dogru/yanlis karari +
  gerekce gosterimi.
- **Public benchmark suite**: 35 ayet → 200 ayet → tum 6236, hafiz panel
  oylamasi ile gold quality skoru.

### Tonage / Sirketsel

- Yayinlandiktan sonra **HuggingFace Spaces** uzerinde kucuk demo aciklayicisi
  (Gradio: Arapca yapistir → fonem akisi).
- **Blog yazisi**: "Quran teleprompter icin rule-based phonemizer neden
  Whisper'dan iyi (ve nerede degil)."
- **Akademik atif sayfasi**: AYBÜ Avesis profili ile baglanti.

## Kontroller / Pre-Publish Checklist

```
- [ ] git status temiz, tum degisiklikler commit + push edilmis
- [ ] CHANGELOG.md [0.2.0] bolumu doldurulmus + tarih: 2026-05-15
- [ ] pyproject.toml version = "0.2.0"
- [ ] src/tilavet_phonemizer/__init__.py __version__ = "0.2.0"
- [ ] MODEL_CARD.md baslik + test sayisi guncel
- [ ] README.md badge sayilari guncel (108 test, %93 coverage)
- [ ] python -m build basariyla calisti
- [ ] twine check dist/* PASSED
- [ ] pytest 108 passed, 0 failed
- [ ] git tag v0.2.0 hazir
- [ ] PyPI token / HF token erisilebilir
- [ ] tilavet-aligner ayri repo olarak push edilebilir (gerekirse henuz degil)
```

## Olasi Riskler / Onlemler

| Risk | Etki | Onlem |
|------|------|-------|
| Test PyPI'de calismayan dosya yolu | Yayin gecikme | `pip install --index-url ... testpypi` ile smoke; production'a sonra |
| Hugging Face token expire | Upload fail | `huggingface-cli login` veya HF_TOKEN env yeniden set |
| TS port API uyumsuzlugu | NPM ve PyPI versionlari ayrisir | NPM'i 0.1.x serisinde tut, parity tamamlaninca 0.2.0'a gec |
| Aligner repo henuz yayinda degil | Phonemizer'in `docs/aligner-mvp.md`'de bahsettigi paket bulunamaz | Once phonemizer publish, sonra aligner ayri repo + ayri release |
| `data/phoneme_index_full.json` ~14 MB | sdist sismesi | MANIFEST.in'de zaten dahil; PyPI bunu kabul eder (200 MB limit altinda) |

## Sonraki Tek Komut

Tum kontroller yesil ise publish icin:

```bash
cd "/Users/baris/Documents/GitHub/Tilavet/Tilavet Phonemizer"
git add -A && git commit -m "release: v0.2.0" && git push
git tag -a v0.2.0 -m "Tilavet Phonemizer 0.2.0" && git push origin v0.2.0
rm -rf dist build src/*.egg-info && python3 -m build
python3 -m twine check dist/*
python3 -m twine upload dist/*
python3 scripts/upload_to_hf.py --repo-id baristiran/tilavet-phonemizer
```

Bu komutlarin her birini elle calistirip ciktiyi gozeterek yapmak en
guvenlisi — ozellikle ilk PyPI yukleme adimi.
