# tilavet-aligner MVP Plani

Bu dokuman phonemizer sonrasindaki ilk forced-alignment paketini kucuk,
testlenebilir parcalara boler. Hedef: ses kaydindan serbest metin uretmek
degil, bilinen Quran phoneme hedef dizisine monotonic zaman damgasi vermek.

## Girdi Sozlesmesi

Aligner phonemizer'dan raw `to_dict()` yerine `to_alignment_dict()` ciktisi
alir:

```python
from tilavet_phonemizer import Phonemizer

target = Phonemizer().phonemize("رَيْبَ ۛ فِيهِ").to_alignment_dict()
```

Beklenen sekil:

```json
{
  "symbols": ["r", "a", "y", "b", "a", "f", "ii", "h", "i"],
  "text": "r a y b a f ii h i",
  "words": [
    {"token": "رَيْبَ", "start": 0, "end": 5},
    {"token": "فِيهِ", "start": 5, "end": 9}
  ],
  "pauses": [
    {"raw_index": 5, "target_index": 5, "symbol": "PAUSE"}
  ]
}
```

Notlar:

- `symbols` CTC/monotonic alignment hedefidir; bos elision entry'leri yoktur.
- `PAUSE` varsayilan olarak hedef sembol degil, metadata'dir.
- `words[*].start/end` bu temiz hedef dizisine gore indekslenir.
- `rules` gerekiyorsa `to_alignment_dict(include_rules=True)` ile gelir, ama
  `rule_index_base == "raw_symbols"` olur.

## Cikti Sozlesmesi

Ilk MVP word-level zaman damgasi uretir:

```json
{
  "words": [
    {
      "token": "رَيْبَ",
      "symbol_start": 0,
      "symbol_end": 5,
      "frame_start": 10,
      "frame_end": 32,
      "time_start": 0.40,
      "time_end": 1.28,
      "score": -3.7,
      "scored_frames": 10,
      "mean_log_prob": -0.37,
      "confidence": 0.69
    }
  ],
  "pauses": [
    {"target_index": 5, "frame_hint": 33}
  ]
}
```

Frame varsayimi ilk surumde 25 ms pencere / 40 ms hop olarak sabitlenebilir.

## Paket Iskeleti

Baslatilan yeni paket konumu:

```text
/Users/baris/Documents/GitHub/Tilavet/tilavet-aligner
```

Ilk iskelet:

```text
tilavet-aligner/
  pyproject.toml
  README.md
  src/tilavet_aligner/
    __init__.py
    contract.py       # dataclass / JSON schema helpers
    posterior.py      # sparse/dense/logit/npy posterior adapters
    ctc.py            # vocabulary, log-prob normalization
    viterbi.py        # monotonic + blank-aware CTC target alignment
    word_spans.py     # symbol frames -> word frames
    cli.py            # JSON target + posterior npy/json input
  tests/
    test_contract.py
    test_ctc.py
    test_posterior.py
    test_cli.py
    test_synthetic_e2e.py
    test_viterbi_toy.py
    test_word_spans.py
  examples/
    synthetic_alignment.py  # phonemizer target + synthetic CTC posterior demo
```

## MVP Algoritmasi

1. Vocabulary hazirla:
   - blank = index 0.
   - hedef semboller = `Phonemizer.phoneme_inventory()` veya kayitli class file.
   - MVP'de `PAUSE` target class olarak kullanilmaz.

2. Posterior girisini normalize et:
   - Sparse frame JSON, dense matrix JSON veya `.npy` matrix kabul edilir.
   - Dense girdide class map/vocabulary sembol -> index ile dogrulanir.
   - `--from-logits` ile row-level log-softmax uygulanir.

3. Monotonic / CTC Viterbi:
   - hedef dizisi `symbols`.
   - Basit mod: her frame'de ya ayni sembolde kal, ya bir sonraki sembole gec.
   - CTC mod: expanded state listesi `[blank, s0, blank, s1, ..., blank]`.
   - `--ctc` ile blank frame'leri hedef sembol span'lerini genisletmez.

4. Word timestamp uret:
   - symbol index -> first/last frame map.
   - `words[*].start/end` araligi frame araligina cevrilir.
   - `pauses[*].target_index` yakininda silence/gap hint olarak saklanir.
   - `score`, `mean_log_prob`, `confidence` alanlari UI tarafina verilir.
   - CTC modda `scored_frames` blank olmayan hedef sembol frame sayisidir.

## Ilk Testler

- Contract:
  - `to_alignment_dict()` ciktisinde bos sembol yok.
  - word span'ler `symbols` dizisine gore gecerli.
  - pause metadata target index'i dogru insertion point verir.

- Viterbi toy:
  - 3 sembol, 8 frame, bilerek yuksek olasilikli diagonal path.
  - cikti frame araliklari beklenen sirada monotonic.
  - CTC blank frame'leri word span'e dahil edilmez.
  - Tekrarlanan hedef semboller (`l l`) blank araci state gerektirir.

- Word spans:
  - iki kelimeli hedefte symbol frame map -> word frame map dogru.
  - zero-length word span yok.
  - confidence `exp(mean_log_prob)` ile 0..1 araliginda hesaplanir.

- Synthetic E2E:
  - sibling `tilavet-phonemizer` source mevcutsa gercek Arapca text phonemize edilir.
  - synthetic CTC posterior ile alignment sonucu word timestamp uretir.
  - model dogrulama testi degil; paket-boundary smoke testidir.

## MVP Disi

- Serbest ASR decoding.
- Full streaming UI protokolu.
- Qiraat varyant graflari.
- Model fine-tuning ve dataset pipeline.
