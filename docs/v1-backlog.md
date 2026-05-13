# V1 Backlog

Bu liste 35 ayetlik candidate batch uretildikten sonra gorulen ilk
iyilestirme alanlaridir.

## P0 - Dogruluk (full-Quran review fixes)

- [done] **Multi-prefix + alif-wasla**: `وَبِٱللَّهِ`, `تَٱللَّهِ`,
  `أَبِٱلْكِتَابِ` artik dogru islerleniyor. Mid-token alif-wasla
  `_emit_cluster` icinde dispatch ediliyor.
- [done] **Li-prefix + bare article lam** (alif dusmus formlar):
  `لِلنَّاسِ`, `وَلِلرِّجَالِ`, `فَلِلذَّكَرِ` dogru. Bare-lam-after-vowel-lam
  mid-token detector eklendi.
- [done] **Madd muttasil tum hamza-letters**: ء, أ, إ, ؤ, ئ ile baslayan
  cluster icin alif-madda → aa4. Ornekler: `الطَّآئِفِينَ`, `مَلَٰٓئِكَةً`.
- [done] **Alif-madda mid-word**: orthografik ligature, gereksiz hamza
  emit edilmiyor. `إِنَّآ` → `' i n n aa` (eski: `' i n n a ' aa`).
- [done] **Cross-token madd munfasil**: kelime sonu tabii madd (aa/ii/uu)
  sonraki kelime hamzasi ile karsilastiginda otomatik aa4/ii4/uu4.
- [done] **Within-word idgham**: mutamathilain (ك+ك, د+د, ه+ه), mutajansayn
  (د+ت, ت+ط, ث+ذ vs.), mutaqaribayn (ق+ك, ل+ر). `أَرَدتُّمْ` → `t t`.
- [done] **Tatweel-hamza orthografisi**: `يَسْتَـْٔذِنُكَ`, `ٱلْمَـَٔابِ`,
  `سَيِّـَٔاتِكُمْ` dogru. `_emit_carrier_hamza` mark-order tabanli yeniden
  yazildi.
- [done] **Muqattaat seam idgham/ikhfa**: `كٓهيعٓصٓ` `3 aa6 y n_g S`,
  `الٓمٓ` `l aa6 m_g m`. `عسق` standalone tanindi.
- [done] **Hafiz review V2 (5 reviewer) sonrasi fixleri**:
  - **`طه` (20:1) muqattaat**: `T h` yerine `T aa h aa`. `_try_muqattaat` artik
    MADDAH zorunlulugu olmadan curated skeleton listesinden eslesiyor.
  - **`وَيَنْـَٔوْنَ` (6:26)**: tatweel-hamza sakin nun sonrasi izhar.
    `_emit_trailing_hamza` helper'i ile sakin noon/mim sonrasi hamza emit.
  - **`ءَآلذَّكَرَيْنِ` (6:143) + `ءَآللَّهُ` (10:59/27:59)**: istifham hemzesi +
    alif-madda + article lam = medd-i farq (6 hareke) + lam shamsiyya elision.
    Hem ALEF_MADDA hem `_emit_vowel_and_madd` icin tespit eklendi.
  - **`ءَآلْـَٰٔنَ` (10:51, 10:91)**: medd-i lazim kalimi mukhaffaf — alif-madda
    + sakin lam → 6 hareke.
  - **U+06EA `مَجْر۪ىٰهَا` (11:41)**: kucuk kesra artik `i` emit ediyor (imale
    degil, Hafs'ta normal kesra).
  - **Tatweel-hemze + tenvin (`مَلْجَـًٔا` 9:57)**: `_emit_carrier_hamza`
    FATHATAN/DAMMATAN/KASRATAN destegi ile tanwin emit ediyor.
  - **Lafzatullah tafhim aa4/aa6 onlu**: `_allah_lam_symbol` artik aa4/aa6/uu4/uu6
    de fatha/damma family olarak taniyor.

- [done] **Hafiz review V1 (4 reviewer) sonrasi fixleri**:
  - **Allah (dagger alif `aa`) prefix sonrasi**: `بِٱللَّهِ` artik `b i l l aa h i`
    (eski: `b i l l a h i`). `_emit_article` Allah-formunu algilayip
    `_emit_allah_core`'a deferliyor.
  - **Lafzatullah tafhim/tarqiq prefix sonrasi**: `تَٱللَّهِ` `t a L L aa h i`,
    `وَٱللَّهُ` `w a L L aa h u`. Onceki vokal fatha/damma ise L.
  - **Vakf qalqalah kubra**: ayet sonu sakin qalqalah harfi (د ب ج ط ق)
    artik `_qal` aliyor. `أَحَدٌ ۝` → `' a H a d_qal`.
  - **Cross-PAUSE assimilation (advisory mushaf pause)**: `ۖ ۚ ۛ ۗ` markerleri
    artik wasl modunda nun/tanwin/mim asimilasyonunu engellemiyor.
    `خَلِيفَةًۭ ۖ قَالُوٓا۟` `... a n_g PAUSE q aa l...`. `_coalesce_leading_geminate_after`
    PAUSE marker'lari atliyor.

Full-Quran taramasi (6236 ayet): 0 crash, 0 bos kelime. Yalnizca 9 nadir
edge-case 3-ardisik-unsuz vakasi kaldi (small marks U+06EA/06DF,
interrogative-hamza+Allah, tanwin-on-hamza vs.).

## P0 - Dogruluk (eski - tamamlandi)

- [done] Shaddali long-vowel tasiyicilari: `إِيَّاكَ` gibi orneklerde ya hem
  konsonant hem madd parcasi olabiliyor.
- [done] Huroof muqatta'at: Dinamik harf ismi tablosu eklendi. Harf isimleri
  madd tabii (aa, ii, uu) içeriyor, maddah varsa madd lazim'e (aa6, ii6, uu6)
  yükseliyor. Testler: Alif-Lam-Mim, Ya-Sin, Kaf-Ha-Ya-Ayn-Sad, Ha-Mim.
- [done] Madd işaretleri: shadda oncesi madd lazim `aa6`, small-alif
  birlesimi, silah (`uu`/`ii`, `uu4`/`ii4`), munfasil (`aa4`/`ii4`/`uu4`),
  badl (`aa`), ve final waw/yah munfasil isaretleri eklendi. Testler:
  madd_lazim, madd_munfasil, madd_badl, madd_silah.
- [done] Wasla/prefix edge case'leri: `وَٱنْحَرْ`, `وَهُوَ`, `بِيَدِهِ`,
  `يُوَسْوِسُ`, `كُفُوًا` testlendi. Prefix sonrasi hamzat wasl dusuyor,
  vokalli waw/ya konsonant olarak isaretleniyor.
- [done] Nun sakin/tanwin ihfa: `مِن شَرِّ`, `يُنفِقُونَ` testlendi.
- [done] Mim sakin + mim: `هُم مُّصِيبَةٌ` uc mim uretmiyor.
- [done] Alef maqsura: `شَىْءٍ`, `ٱلْحَىُّ`, `ٱلْعَلِىُّ` gibi orneklerde
  baglama gore ya/madd ayrimi yapiliyor.
- [done] Waw dagger-alif carrier: `ٱلصَّلَوٰةَ` gibi orneklerde konsonant
  `w` uretilmiyor.
- [done] Iltiqa al-sakinayn: `ٱهْدِنَا ٱلصِّرَٰطَ`, `فِى ٱلْأَرْضِ`,
  `وَلَا ٱلضَّآلِّينَ` gibi hamzat-wasl baglamlarinda uzun vokal kisa
  vokale dusuruluyor.
- [done] Tasiyici hamza: `يَـُٔودُهُۥ` gibi yazimlarda hamza `y uu` icine
  yutulmuyor, `y a ' uu` olarak temsil ediliyor.
- [done] Waqf/PAUSE varyant modu: `waqf_on_pause` modu implement edildi.
  Final hareke dusmesi, tanwin kaldirma, taa marbuta `t` -> `h` donusumu,
  madd arid lis-sukun uzatma ve pause sonrasi idgham kesilmesi kurallari eklendi.
  Testler: `WaqfOnPauseTests` (6 test).
- [done] Ayetler arasi wasl/nun qutni: `cross_ayah_wasl` modu implement edildi.
  Ayet sinirlarinda PAUSE eklenmez, nun sakin/tanwin idgham ve mim sakin idgham
  cross-ayah olarak uygulanir. Testler: `CrossAyahWaslTests` (4 test).

## P1 - Validation

- [done] Waqf/PAUSE tasarim karari kayda alindi: V1 seed `wasl + PAUSE
  metadata`, runtime roadmap ise variant graph. Detay:
  [waqf-pause-decision.md](waqf-pause-decision.md)
- Hafiz notlari geldikce `candidate_v1` alanlari dogrulanmis `gold_v1`
  alanina cevrilecek.
- Her duzeltme icin ayet bazli unit test eklenecek.
- Rapor sadece hatali/kararsiz yerleri daha kolay isaretleyecek sekilde
  kisaltilabilir.

## P2 - Runtime

- [done] Her kelime icin fonem offset ciktisi: `generate_phoneme_index.py`
  ile `data/phoneme_index.json` uretildi. Wasl + waqf varyantlari,
  word-level start/end offset'leri iceriyor.
- [done] Quran-only decoder icin sure/ayet/kelime/fonem index: ayni dosya.
- [done] CTC sinif listesi: `data/ctc_classes.json` + `data/ctc_classes.txt`
  uretildi. 50 class: blank(0), 29 konsonant, 12 vokal, 8 varyant, PAUSE(49).
  Gold data'dan turetildi; T_qal gibi spec'te olan ama henuz seed'de
  gorulmeyen siniflar da eklendi.
