# Tilavet Phonemizer Handoff

Bu dosya projeyi yeni bir LLM/gelistirici'ye devretmek icin hazirlandi.
Once bunu oku, sonra ilgili dosyalari incele.

## Kullanici ve Proje Amaci

Kullanici, eski hard disk kaybi sonrasi Tilavet projesini temiz bir sayfadan
yeniden kuruyor.

Eski yon:

```text
Whisper -> Arabic text transcription -> ayah matching
```

Yeni ve tercih edilen yon:

```text
Quran text -> phoneme sequence
Audio -> small streaming CTC phoneme posterior
Decoder -> Quran phoneme map alignment
UI -> word-by-word teleprompter highlight
```

Whisper runtime motoru olarak hedeflenmiyor; olsa olsa debug/teacher olarak
kullanilabilir. Ana hedef offline/iOS icin hafif, Quran-only, fonem tabanli
hizalama.

## Repo Konumu

```text
/Users/baris/Documents/GitHub/Tilavet/Tilavet Phonemizer
```

(Eski handoff'larda `/Users/baris/Documents/GitHub/Tilavet Phonemizer` olarak
yaziliydi; klasor `Tilavet/` altinda toplandi.)

## Mevcut Durum (Mayis 2026)

- Python tabanli V1 phonemizer cekirdegi (`src/tilavet_phonemizer/`) tamamlandi.
- 35 ayetlik validation seed + tum-Kuran sanity tarama yapildi (0 crash).
- 5 LLM hafiz reviewer turu tamamlandi; bulgular synthesis dokumanina islendi.
- 6236 ayetlik full-Quran phoneme index (`data/phoneme_index_full.json`) uretildi.
- CTC class listesi (`data/ctc_classes.{json,txt}`) 50 sinif olarak donduruldu.
- Public API genisletildi: `to_dict()`, `to_alignment_dict()`,
  `phoneme_inventory()`, `phonemize_many()`, CLI `--json`/`--rules-only`/
  `--waqf`/`--cross-ayah`/`--file`/`-`/`--print-inventory` bayraklari.
- `../tilavet-aligner/` altinda ilk MVP paket iskeleti baslatildi
  (contract, posterior adapters, CTC helpers, monotonic Viterbi, word span
  projection, blank-aware CTC mode, confidence metrics, CLI, synthetic E2E demo,
  toy tests).
- Testler yesil: **108 test, 35 subtest, %93 coverage**.

Test komutu:

```bash
PYTHONPATH=src python3 -m pytest tests/ -v
ruff check .
```

Hizli CLI denemesi:

```bash
PYTHONPATH=src python3 -m tilavet_phonemizer.cli "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
PYTHONPATH=src python3 -m tilavet_phonemizer.cli --json --waqf "ٱلرَّحِيمِ ۝"
PYTHONPATH=src python3 -m tilavet_phonemizer.cli --print-inventory
```

## Onemli Dosyalar

- `src/tilavet_phonemizer/phonemizer.py` & `arabic.py`
  Ana Python rule-based phonemizer ve sabitleri.

- `src/tilavet_phonemizer/cli.py`
  CLI entry point. `--json`, `--rules-only`, `--waqf`, `--cross-ayah`, `--file`,
  stdin (`-`) ve `--print-inventory` destegi.

- `ts/src/phonemizer.ts` & `ts/src/arabic.ts`
  TypeScript portu (NPM paketi kaynak kodlari).

- `tests/test_phonemizer.py` & `ts/tests/phonemizer.test.ts`
  Kural bazli unit testler (Python ve TS icin ayri ayri).

- `tests/test_recovered_seed.py`
  35 ayetlik seed'in deterministic kalmasini test eder.

- `tests/test_coverage_branches.py`
  Internal branch coverage; private metodlarin nadir patikalarini ornekler.

- `tests/test_public_api.py`
  `to_dict`, `to_alignment_dict`, `phoneme_inventory`, `phonemize_many`,
  CLI bayraklari.

- `llms.txt`
  LLM'lerin/Agent'larin projeyi ve API'sini dogru anlamasi icin yonergeler.

- `data/validation/recovered_seed.jsonl`
  35 ayetlik current `candidate_v1` seti.

- `data/validation/llm_hafiz_review_full.md`
  Diger LLM hafizlara verilecek tam review prompt + batch.

- `data/phoneme_index_full.json`
  Tum 6236 ayetin wasl + waqf fonem sirasi + word offset'leri.

- `data/ctc_classes.{json,txt}`
  Blank + PAUSE dahil 50 CTC class listesi. `Phonemizer.phoneme_inventory(include_metadata=True)`
  bu listenin blank haric sembolleriyle tutarli.

- `docs/phoneme-spec.md`
  V1 fonem sembol sozlesmesi.

- `docs/llm-review-synthesis.md`
  Kabul edilen/reddedilen LLM hafiz review bulgulari.

- `docs/waqf-pause-decision.md`
  PAUSE/waqf tasarim karari.

- `docs/aligner-mvp.md`
  Sonraki `tilavet-aligner` paketi icin girdi/cikti sozlesmesi ve MVP iskeleti.

- `docs/v1-backlog.md`
  Siradaki isler.

## V1 Sembol Sozlesmesi

Temel semboller `docs/phoneme-spec.md` icinde. Kritik noktalar:

- `a i u`: kisa harekeler.
- `aa ii uu`: madd tabii (2 harakah).
- `aa4 ii4 uu4`: madd muttasil/munfasil/silah kubra (4 harakah).
- `aa6 ii6 uu6`: madd lazim/arıd lis-sukun/farq (6 harakah).
- `'`: hamza / okunan alif carrier.
- `L`: sadece lafzatullah tafkhim lam (fatha/damma onunde).
- `n_g`: nun/tanwin ghunna, ikhfa veya ghunnali idgham ortak sembolu.
- `m_g`: iqlab veya mim ghunna / idgham shafawi.
- `q_qal T_qal b_qal j_qal d_qal`: qalqalah varyantlari.
- `PAUSE`: mushaf durak marker'i; waqf fonetik donusumu degildir.

Kod uzerinden:

```python
from tilavet_phonemizer import Phonemizer
Phonemizer.phoneme_inventory()                    # CTC siniflari (PAUSE haric)
Phonemizer.phoneme_inventory(include_metadata=True)  # PAUSE dahil
```

## Public API ozeti (downstream aligner icin)

```python
from tilavet_phonemizer import Phonemizer, PhonemizerConfig

p = Phonemizer()                        # varsayilan wasl
result = p.phonemize("بِسْمِ ٱللَّهِ")

result.text          # "b i s m i l l aa h i"
result.symbols       # ["b", "i", ...]
result.clean_symbols # bos string entries cikarilmis raw semboller
result.words         # [WordSpan(token=..., start, end), ...]
result.rules         # [RuleHit(symbol_index, symbol, rule, source), ...]

# Aligner / web servisi icin tek satirlik JSON:
result.to_dict()                      # tam (rules dahil)
result.to_dict(include_rules=False)   # hafif raw sequence + words
result.to_alignment_dict()            # CTC hedefi + PAUSE metadata + remap words

# Batch (dataset uretimi, aligner warm-up):
results = p.phonemize_many(["بِسْمِ", "ٱللَّهِ", "هُوَ"])

# Mod degisiklikleri config ile:
Phonemizer(PhonemizerConfig(waqf_on_pause=True))    # waqf transformasyonu
Phonemizer(PhonemizerConfig(cross_ayah_wasl=True))  # ayetler arasi wasl
Phonemizer(PhonemizerConfig(emit_pause=False))      # PAUSE marker'i bastir
```

`PhonemizationResult.to_dict()` raw/debug ciktiyi korur. Forced-alignment
tarafi icin `to_alignment_dict()` kullan: bos elizyon sembolleri cikarilir,
`PAUSE` varsayilan olarak metadata'ya tasinir ve word span'leri hedef sembol
dizisine gore yeniden indekslenir.

## Kabul Edilen Ana Duzeltmeler

Bu kararlar koda ve testlere islenmis durumda:

- `إِيَّاكَ`: `y y` shadda korunur, `ii` icine yutulmaz.
- Vokalli `و`/`ي` konsonanttir:
  - `هُوَ` -> `h u w a`
  - `بِيَدِهِ` -> `b i y a d i h i`
  - `كُفُوًا` -> `k u f u w a n`
- Lam shamsiyya/shaddali article lam korunur:
  - `ٱلَّذِينَ` -> `l l a dh...`
- Prefix sonrasi hamzat wasl duser:
  - `وَٱنْحَرْ` -> `w a n H a r`
- Nun sakin/tanwin:
  - `مِن شَرِّ` -> `m i n_g sh...`
  - `يُنفِقُونَ` -> `y u n_g f...`
- Mim sakin + mim:
  - `هُم مُّصِيبَةٌ` -> `h u m_g m...`
- Small alif/dagger alif tek uzun vokal olur:
  - `m a aa` degil `m aa`
- Waw dagger-alif carrier:
  - `ٱلصَّلَوٰةَ` -> `S S a l aa t a`
- Ha kinayah silah:
  - `هُۥ` -> `uu`, hamzadan once `uu4`
  - `هِۦ` -> `ii`, hamzadan once `ii4`
- Tasiyici hamza:
  - `يَـُٔودُهُۥ` -> `y a ' uu d u h uu`
- Iltiqa al-sakinayn:
  - `ٱهْدِنَا ٱلصِّرَٰطَ` -> `... n a S S...`
  - `فِى ٱلْأَرْضِ` -> `f i l ' a r D i`
  - `وَلَا ٱلضَّآلِّينَ` -> `w a l a D D aa6...`

## Bilincli Olarak Reddedilen Review Iddialari

Yeni LLM bunlari tekrar "hata" diye gorurse dikkatli ol:

- `بِسْمِ ٱللَّهِ` veya `لِلَّهِ` icin mutlaka `L` kullanilmali iddiasi
  reddedildi. Kasradan sonra lafzatullah lam'i tarqiq olur; `l` dogru.

- `يُنفِقُونَ` icinde nun sakin yok iddiasi reddedildi. `n_g` dogru.

- `أَتَجْعَلُ` hamzasi dusmeli iddiasi reddedildi. Hamza qat' korunur.
  Ayrica `جْ` sakin oldugu icin `j_qal` dogru.

- `ٱلضَّآلِّينَ` icin `aa6` yerine `aa` olmali iddiasi reddedildi.
  Madd lazim kalimi muthaqqal olarak `aa6` dogru.

- `ٱلْأَرْضِ` icindeki hamzanin dusmesi gerektigi iddiasi reddedildi.
  Kok hamzasi/hamzat qat' korunur.

- `كُفُوًا` hamzali okunmali iddiasi reddedildi. Bu rasmda waw ile temsil
  ediliyor: `k u f u w a n`.

- `هُدًى لِّلْمُتَّقِينَ` icinde tanwin `n` mutlaka gorunmeli iddiasi
  reddedildi. Tanwin + lam idgham bila ghunna ile `h u d a l l...` dogru.

- `ٱلْعَٰلَمِينَ` sonu `n i` olmali iddiasi reddedildi. V1 seed'de
  `... m ii n a` dogru kabul edildi.

## PAUSE / Waqf Karari

Detay: `docs/waqf-pause-decision.md`

Alinan karar:

```text
V1 seed = wasl phoneme sequence + PAUSE metadata marker
```

Yani `PAUSE` su anda fonetik waqf donusumu degil. Ornek mevcut V1:

```text
r a y b a PAUSE f ii h i
kh a l ii f a t a n PAUSE q aa l uu4
n a w m u n PAUSE l l a h uu
```

Bu dogrudan "kari kesin burada waqf yapti" anlamina gelmez. Runtime decoder
bu boundary'de optional silence/gap prior kullanabilir.

Roadmap (Option C):

```text
wasl_candidate
waqf_on_pause      <- PhonemizerConfig(waqf_on_pause=True) ile aktif
cross_ayah_wasl    <- PhonemizerConfig(cross_ayah_wasl=True) ile aktif
```

Yani Option A V1 seed icin canli; Option C runtime variant graph alaninda.

## Su Anda Degistirilmemesi Gerekenler

- `PAUSE`'u hemen fonetik waqf'a cevirmeyin (default modda).
- `candidate_v1` alanlarini dogrudan `gold_v1` diye rename etmeyin.
- Huroof muqatta'at madd uzunluklarini tek reviewer itiraziyla degistirmeyin.
- `n_g` / `m_g` sembol sozlesmesini daraltmayin; bunlar bilerek ortak
  ghunna sembolleri olarak kullaniliyor.
- `Phonemizer.phoneme_inventory()` sirasi CTC class indekslerine bagimli;
  yeniden siralamayin (sona ekleyin).

## Aligner Entegrasyonu (sonraki paket: tilavet-aligner)

Tilavet phonemizer'in tukettigi cikti dogrudan forced alignment paketine
beslenir. Onerilen sekil:

```python
from tilavet_phonemizer import Phonemizer, PhonemizerConfig

# Ayet bazli, wasl modu, PAUSE metadata kalsin:
p = Phonemizer(PhonemizerConfig(emit_pause=True))
text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
ayah = p.phonemize(text).to_alignment_dict()
# ayah = {
#   "symbols": [...],
#   "text":    "b i s m i l l aa h i ...",
#   "words":   [{"token": "بِسْمِ", "start": 0, "end": 5}, ...]
# }
```

Aligner tarafindaki sozlesme:

- Wav2Vec2 model: `facebook/wav2vec2-xlsr-arabic-960h` (veya benzeri).
- CTC class listesi: `Phonemizer.phoneme_inventory()` (blank prepend edilir).
  PAUSE bir CTC sinifi degil; metadata olarak word offset'i ile birlikte
  alignment ipucu olarak gecirilir.
- Frame alignment: 25 ms pencere, 40 ms hop.
- Decoder: monotonic Viterbi + Quran fonem trie/suffix index.
- Streaming protokol: JSON ayet (yukaridaki sekil) `posterior` frame'leri ile
  hizalama yapar; output frame_start/frame_end per WordSpan.

Bu sozlesmeyi degistirecek bir sey yapmaniz gerekirse, **once** aligner
paketi tarafinda tuketim koduna bakin (ileride bu repo disinda olacak).

## Sıradaki En Mantikli Isler

1. **Forced Alignment (Zaman Damgasi) Araci**
   - Fonemleri (`tilavet-phonemizer`) akustik bir ses modeliyle
     (Hugging Face Wav2Vec2 / Whisper) eslestirerek kelime kelime veya harf
     harf zaman damgasi veren Python kütüphanesinin (`tilavet-aligner`)
     gelistirilmesi.
   - Bu modulun girdisi `Phonemizer().phonemize(...).to_alignment_dict()` ciktisidir.

2. **Web / Mobil Gelistirici Rehberleri**
   - TypeScript paketi (`npm install tilavet-phonemizer`) kullanilarak
     React Native veya Flutter ile "karaoke" tarzinda bir Kur'an teleprompter
     yapimini gosteren `examples/` klasorlerinin veya blog yazilarinin
     eklenmesi.

3. **Waqf variant export tasarimi**
   - `waqf_on_pause` modu Python portuna eklendi (Mayis 2026). TS portuna ve
     genis capli regression testlerine genisletilmesi gerekli.

4. **Cross-ayah wasl tasarimi**
   - `cross_ayah_wasl` modu Python portuna eklendi. Tum platformlara entegre
     edilmesi ve daha genis test setiyle dogrulanmasi gerekli.

5. **Diger Kıraatlerin Desteklenmesi (Örn: Warsh, Qalun)**
   - Algoritmayi modulerlestirerek Hafs disindaki kural setlerinin de
     parametre (`riwayat="warsh"`) olarak fonemizere eklenebilmesi.

6. **Quran-wide export ek dosyalari**
   - `data/phoneme_index_full.json` mevcut; trie/suffix index runtime icin
     uretilebilir (`generate_phoneme_index.py` zaten var).

## Calisma Kurallari

- Kod degistirince test calistir:

```bash
PYTHONPATH=src python3 -m pytest tests/ -v
ruff check .
```

- Coverage gormek icin:

```bash
PYTHONPATH=src python3 -m pytest tests/ --cov=src/tilavet_phonemizer --cov-report=term-missing
```

- Validation report yeniden uretmek icin:

```bash
python3 scripts/make_validation_report.py --output data/validation/hafiz_validation_report.md
```

- Diger LLM hafizlara verilecek dosya:

```text
data/validation/llm_hafiz_review_full.md
```

Bu dosya prompt + ayet batch'ini birlikte icerir.

## Son Bilinen Test Durumu

```text
108 passed, 35 subtests passed in ~0.07s
Coverage: 93% (arabic.py %100, __init__.py %100, cli.py %100, phonemizer.py %92)
```

## Yeni LLM Icin Kisa Talimat

Bu projede amac "mukemmel dini/tecvid otoritesi" iddiasinda bulunmak degil,
offline Quran audio alignment icin testlenebilir ve review ile iyilesen bir
fonem sozlesmesi kurmaktir. Tartismali kararlar koda rastgele yansitilmamali;
once `docs/llm-review-synthesis.md`, `docs/phoneme-spec.md` ve
`docs/waqf-pause-decision.md` kontrol edilmeli, sonra test eklenmelidir.

Yeni bir kural ekleyeceksen:

1. Test-first: ayet/ayetler icin failing test yaz.
2. Synthesis dokumanlarinda referans ara; yoksa kararlar dosyasina ekle.
3. Sembol setine yeni sembol eklemekten kacin; varsa sebebini yaz.
4. `recovered_seed.jsonl` regression'i bozulduysa, degisikligi seed
   yenilemesiyle birlikte sun.

Onerilen yardimci komutlar:

```bash
# Coverage'i gormek
PYTHONPATH=src python3 -m pytest tests/ --cov=src/tilavet_phonemizer --cov-report=term-missing

# CTC sinif listesini regenerate etmek
PYTHONPATH=src python3 -m tilavet_phonemizer.cli --print-inventory

# Tek bir ayeti JSON olarak gormek
PYTHONPATH=src python3 -m tilavet_phonemizer.cli --json --rules "بِسْمِ ٱللَّهِ"

# Sadece rule trace'i gormek
PYTHONPATH=src python3 -m tilavet_phonemizer.cli --rules-only "بِسْمِ"
```
