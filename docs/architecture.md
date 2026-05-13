# Tilavet V1 Architecture

## Karar

MVP icin Whisper ana motor degil. Whisper ancak debug/teacher olarak tutulur.
Ana hat:

1. Quran text -> phoneme map
2. Audio -> small streaming CTC phoneme posterior
3. Quran-only decoder -> active ayah and phoneme position
4. Word offsets -> teleprompter highlight

Bu karar iOS/offline/hedef gecikme icin kritik. Serbest metin ASR yerine
onceden bilinen Quran fonem akisi hizalaniyor.

## Veri sozlesmesi

Phonemizer her ayet icin sunlari uretmeli:

- `symbols`: fonem sembolleri
- `rules`: hangi sembolun hangi kuralla uretildigi
- `words`: her kelimenin fonem baslangic/bitis offset'i

Runtime tarafinda model kelime timestamp'i uretmez. Aktif fonem pozisyonu,
onceden hesaplanan `words` offset'inden aktif kelimeye cevrilir.

## V1 kapsam

- Hafs/Asim ana okuma icin sembolik kural motoru
- alif wasla, lam shamsiyya/qamariyya
- lafzatullah lam tarqiq/tafkhim
- shadda, sukun, temel madd tabii
- tanwin/nun sakin icin temel izhar/ikhfa/idgham/iqlab
- qalqalah
- taa marbuta wasl modu

## V1 disi

- Tum waqf/ibtida varyantlari
- Tum huroof muqatta'at uzunluklari ve madd lazim ayrintilari
- Reciter-specific tempo/makam/nefes modelleme
- Audio model egitimi
- CoreML export

Bu basliklar V2+ isleri. V1 once dogru ve denetlenebilir etiket uretmeli.

## Model hedefi

CTC model siniflari yaklasik:

- 28 Arapca konsonant sembolu
- emphatic/ghunna/qalqalah varyantlari
- kisa/uzun vokal sembolleri
- blank

Decoder serbest metin uretmez. Fonem posteriorlarini Quran fonem trie/suffix
index icinde arar.

