# Tilavet Phonemizer Handoff

Bu dosya projeyi yeni bir LLM'e devretmek icin hazirlandi. Once bunu oku,
sonra ilgili dosyalari incele.

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
/Users/baris/Documents/GitHub/Tilavet Phonemizer
```

## Mevcut Durum

- Python tabanli kucuk V1 phonemizer cekirdegi var.
- 35 ayetlik validation seed var.
- LLM hafiz review turlari yapildi.
- Birden fazla false-positive/false-negative sinifi karar kaydina gecirildi.
- Testler yesil: `32 tests OK`.

Test komutu:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Hizli CLI denemesi:

```bash
PYTHONPATH=src python3 -m tilavet_phonemizer.cli "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
```

## Onemli Dosyalar

- `src/tilavet_phonemizer/phonemizer.py`  
  Ana rule-based phonemizer.

- `src/tilavet_phonemizer/arabic.py`  
  Arabic Unicode sabitleri, harf sembol map'i, diacritics.

- `tests/test_phonemizer.py`  
  Kural bazli unit testler.

- `tests/test_recovered_seed.py`  
  35 ayetlik seed'in deterministic kalmasini test eder.

- `data/validation/recovered_seed.jsonl`  
  35 ayetlik current `candidate_v1` seti.

- `data/validation/llm_hafiz_review_full.md`  
  Diger LLM hafizlara verilecek tam review prompt + batch.

- `docs/phoneme-spec.md`  
  V1 fonem sembol sozlesmesi.

- `docs/llm-review-synthesis.md`  
  Kabul edilen/reddedilen LLM hafiz review bulgulari.

- `docs/waqf-pause-decision.md`  
  PAUSE/waqf tasarim karari.

- `docs/v1-backlog.md`  
  Siradaki isler.

## V1 Sembol Sozlesmesi

Temel semboller `docs/phoneme-spec.md` icinde. Kritik noktalar:

- `a i u`: kisa harekeler.
- `aa ii uu`: madd tabii.
- `aa4 ii4 uu4`: madd muttasil/munfasil/silah kubra adayi.
- `aa6 ii6 uu6`: madd lazim adayi.
- `'`: hamza / okunan alif carrier.
- `L`: sadece lafzatullah tafkhim lam.
- `n_g`: nun/tanwin ghunna, ikhfa veya ghunnali idgham ortak sembolu.
- `m_g`: iqlab veya mim ghunna / idgham shafawi.
- `q_qal T_qal b_qal j_qal d_qal`: qalqalah varyantlari.
- `PAUSE`: mushaf durak marker'i; waqf fonetik donusumu degildir.

## Kabul Edilen Ana Duzeltmeler

Bu kararlar koda ve testlere islenmis durumda:

- `إِيَّاكَ`: `y y` shadda korunur, `ii` icine yutulmaz.
- Vokalli `و`/`ي` konsonanttir:
  - `هُوَ` -> `h u w a`
  - `بِيَدِهِ` -> `b i y a d i h i`
  - `كُفُوًا` -> `k u f u w a n`
- Lam shamsiyya/shaddali article lam korunur:
  - `ٱلَّذِينَ` -> `l l a dh...`
- Prefix sonrasi hamzat wasl duser:
  - `وَٱنْحَرْ` -> `w a n H a r`
- Nun sakin/tanwin:
  - `مِن شَرِّ` -> `m i n_g sh...`
  - `يُنفِقُونَ` -> `y u n_g f...`
- Mim sakin + mim:
  - `هُم مُّصِيبَةٌ` -> `h u m_g m...`
- Small alif/dagger alif tek uzun vokal olur:
  - `m a aa` degil `m aa`
- Waw dagger-alif carrier:
  - `ٱلصَّلَوٰةَ` -> `S S a l aa t a`
- Ha kinayah silah:
  - `هُۥ` -> `uu`, hamzadan once `uu4`
  - `هِۦ` -> `ii`, hamzadan once `ii4`
- Tasiyici hamza:
  - `يَـُٔودُهُۥ` -> `y a ' uu d u h uu`
- Iltiqa al-sakinayn:
  - `ٱهْدِنَا ٱلصِّرَٰطَ` -> `... n a S S...`
  - `فِى ٱلْأَرْضِ` -> `f i l ' a r D i`
  - `وَلَا ٱلضَّآلِّينَ` -> `w a l a D D aa6...`

## Bilincli Olarak Reddedilen Review Iddialari

Yeni LLM bunlari tekrar "hata" diye gorurse dikkatli ol:

- `بِسْمِ ٱللَّهِ` veya `لِلَّهِ` icin mutlaka `L` kullanilmali iddiasi
  reddedildi. Kasradan sonra lafzatullah lam'i tarqiq olur; `l` dogru.

- `يُنفِقُونَ` icinde nun sakin yok iddiasi reddedildi. `n_g` dogru.

- `أَتَجْعَلُ` hamzasi dusmeli iddiasi reddedildi. Hamza qat' korunur.
  Ayrica `جْ` sakin oldugu icin `j_qal` dogru.

- `ٱلضَّآلِّينَ` icin `aa6` yerine `aa` olmali iddiasi reddedildi.
  Madd lazim kalimi muthaqqal olarak `aa6` dogru.

- `ٱلْأَرْضِ` icindeki hamzanin dusmesi gerektigi iddiasi reddedildi.
  Kok hamzasi/hamzat qat' korunur.

- `كُفُوًا` hamzali okunmali iddiasi reddedildi. Bu rasmda waw ile temsil
  ediliyor: `k u f u w a n`.

- `هُدًى لِّلْمُتَّقِينَ` icinde tanwin `n` mutlaka gorunmeli iddiasi
  reddedildi. Tanwin + lam idgham bila ghunna ile `h u d a l l...` dogru.

- `ٱلْعَٰلَمِينَ` sonu `n i` olmali iddiasi reddedildi. V1 seed'de
  `... m ii n a` dogru kabul edildi.

## PAUSE / Waqf Karari

Detay: `docs/waqf-pause-decision.md`

Alinan karar:

```text
V1 seed = wasl phoneme sequence + PAUSE metadata marker
```

Yani `PAUSE` su anda fonetik waqf donusumu degil.

Ornek mevcut V1:

```text
r a y b a PAUSE f ii h i
kh a l ii f a t a n PAUSE q aa l uu4
n a w m u n PAUSE l l a h uu
```

Bu dogrudan "kari kesin burada waqf yapti" anlamina gelmez. Runtime decoder
bu boundary'de optional silence/gap prior kullanabilir.

Roadmap:

```text
wasl_candidate
waqf_on_pause
cross_ayah_wasl
```

Yani uzun vadede Option C/variant graph tasarlanacak; V1 seed icin Option A
korunacak.

## Su Anda Degistirilmemesi Gerekenler

- `PAUSE`'u hemen fonetik waqf'a cevirmeyin.
- `candidate_v1` alanlarini dogrudan `gold_v1` diye rename etmeyin.
- Huroof muqatta'at madd uzunluklarini tek reviewer itiraziyla degistirmeyin.
- `n_g` / `m_g` sembol sozlesmesini daraltmayin; bunlar bilerek ortak
  ghunna sembolleri olarak kullaniliyor.

## Sıradaki En Mantikli Isler

1. **Waqf variant export tasarimi**
   - `waqf_on_pause` modu icin final hareke dusmesi, tanwin, taa marbuta,
     madd arid lis-sukun ve pause sonrasi idgham kesilmesi kurallari.

2. **Cross-ayah wasl tasarimi**
   - `أَحَدٌ ٱللَّهُ` gibi ayetler arasi nun-qutni / wasl variantlari.

3. **Validation status modeli**
   - `candidate_v1`
   - `gold_wasl_v1`
   - ileride `gold_waqf_on_pause_v1`
   - reviewer provenance / agreement count.

4. **Quran-wide export**
   - sure/ayet/kelime/fonem offset map.
   - pause boundary metadata.
   - decoder icin trie/suffix index input.

5. **CTC class listesi**
   - `docs/phoneme-spec.md` ile birebir kilitlenmis sinif listesi.
   - `PAUSE` ana phoneme class degil, metadata/optional gap olarak
     degerlendirilecek.

## Calisma Kurallari

- Kod degistirince test calistir:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
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
Ran 32 tests in ~0.01s
OK
```

## Yeni LLM Icin Kisa Talimat

Bu projede amac "mukemmel dini/tecvid otoritesi" iddiasinda bulunmak degil,
offline Quran audio alignment icin testlenebilir ve review ile iyilesen bir
fonem sozlesmesi kurmaktir. Tartismali kararlar koda rastgele yansitilmemeli;
once `docs/llm-review-synthesis.md`, `docs/phoneme-spec.md` ve
`docs/waqf-pause-decision.md` kontrol edilmeli, sonra test eklenmelidir.
