# LLM Hafiz Review Synthesis

Bu dokuman Gemini, Qwen, Cursor, Windsurf ve X geri bildirimlerinden
cikarilan teknik kararlari ozetler.

## Kabul edilen yuksek-guven bulgular

- `إِيَّاكَ`: shaddali ya `y y` olarak korunmali, `ii` icine yutulmamali.
- Vokalli `و` ve `ي` konsonanttir: `هُوَ`, `بِيَدِهِ`, `يُوَسْوِسُ`,
  `كُفُوًا` gibi orneklerde otomatik madd harfine cevrilmemeli.
- `ٱلَّذِينَ`, `ٱلَّذِى`: lam uzerindeki shadda telaffuz edilir; mevcut
  article logic bu lam'i hatali dusuruyordu.
- `وَٱنْحَرْ`: prefix sonrasi hamzat wasl wasl modunda okunmaz.
- Nun sakin/tanwin ihfa: `مِن شَرِّ`, `يُنفِقُونَ` gibi orneklerde `n_g`
  gerekir.
- Mim sakin + mim: `هُم مُّصِيبَةٌ` gibi orneklerde uc mim uretmek yerine
  `m_g m` benzeri tek ghunna isareti gerekir.
- Huroof muqatta'at yalin harf olarak degil, harf isimleriyle temsil edilmeli.
- `شَىْءٍ`: alef maqsura sukunlu ya konsonanti gibi davranir; `sh aa` degil
  `sh a y`.
- `ٱلْحَىُّ`, `كُرْسِيُّهُ`, `ٱلْعَلِىُّ`: shaddali alef maqsura/ya `y y`
  olarak temsil edilmeli.
- `ٱلضَّآلِّينَ`: maddah alif sonrasi shaddali lam geldigi icin `aa6`
  madd lazim olarak isaretlenmeli.
- Small alif/dagger alif `a aa` olarak iki parca degil, tek uzun vokal
  (`aa`, gerekirse `aa4`) olarak temsil edilmeli.
- `ٱلصَّلَوٰةَ` gibi yazimlarda waw, alif tasiyici ise konsonant `w` olarak
  okunmamali.
- Ha kinayah isaretleri (`هُۥ`, `هِۦ`) silah maddi uretmeli; hamzadan once
  kubra (`uu4`/`ii4`), normal wasl ortaminda sughra (`uu`/`ii`).
- `قَالُوٓا أَ...` gibi madd harfi sonrasi sonraki kelime hamza ise munfasil
  olarak `uu4` uretilebilir.
- `يَـُٔودُهُۥ`: ya tasiyicisi uzerindeki hamza ayri `y a ' uu` akisi
  uretmeli; hamza `y uu` icine yutulmamali.
- Iltiqa al-sakinayn: uzun vokalden sonra hamzat-wasl ile baslayan kelime
  geldiginde madd harfi wasl akista kisa vokale duser (`ٱهْدِنَا ٱلصِّرَٰطَ`
  -> `n a S S...`, `فِى ٱلْأَرْضِ` -> `f i l...`).

## Reddedilen veya ertelenen bulgular

- "Lafzatullah her yerde `L` olmali" iddiasi reddedildi. Kasradan sonra
  lafzatullah lam'i tarqiq olur; `بِسْمِ ٱللَّهِ` ve `لِلَّهِ` icin kucuk `l`
  sembolu bilincli olarak dogru kabul edildi.
- Madd uzunlugu kararlarini tek reviewer ile kilitlemedik. `aa4`, `aa6`,
  madd lazim, madd munfasil ve madd silah ayrimi ikinci validation turunda
  ayrica ele alinacak.
- "`لَآ` ve `شَآءَ` mutlaka `aa` olmali" itirazi simdilik reddedildi:
  hamza baglaminda munfasil/muttasil adayi olduklari icin V1 sembol
  sozlesmesinde `aa4` kalabilir.
- "`يُنفِقُونَ` icinde nun sakin yok" itirazi reddedildi; yazida sukun
  isareti gorunmese bile fonetik olarak nun sakin + fa ihfa ornegidir.
- "`أَتَجْعَلُ` wasl halinde hamzasiz okunmali" itirazi reddedildi; buradaki
  hamza qat' oldugu icin korunur. `جْ` sakin oldugu icin `j_qal` de korunur.
- "`مَن ذَا` ve `عِندَهُۥ` icindeki nun sakin degil" itirazi reddedildi;
  bu orneklerde nun sakin ihfa baglamindadir.
- `ٱلْأَرْضِ` icindeki hamza temsili konusunda reviewer'lar net consensus
  vermedi; hamzat qat' kok harfi oldugu icin simdilik korunuyor.
- "`كُفُوًا أَحَدٌ` icindeki hamza wasla gibi dusmeli" itirazi reddedildi;
  `أَحَدٌ` hamzat qat' ile baslar ve tanwin oncesinde izhar baglamidir.
- "`كُفُوًا` hamzali okunmali" itirazi reddedildi; bu kelime V1 seed'deki
  rasmda waw ile gelir ve wasl akista `k u f u w a n` olarak temsil edilir.
- "`ٱلْعَٰلَمِينَ` sonu `n i` olmali" itirazi reddedildi; Hafs metnindeki
  son nun fatha ile okunur, candidate `... m ii n a` dogrudur.
- "`هُدًى لِّلْمُتَّقِينَ` icinde tanwin n mutlaka gorunmeli" itirazi
  reddedildi; tanwin + lam idgham bila ghunna oldugu icin fonetik akista
  `h u d a l l...` beklenir.
- `PAUSE` isaretlerinin final hareke/tanwin dusurmesi gerektirdigi yorumlari
  V1 icin dogrudan hata sayilmadi. Bu batch'te `PAUSE` mushaf durak
  isaretini koruyan marker'dir; tam waqf fonetik varyanti ayri mod olacaktir.
- Ayetler arasi wasl/nun qutni (`أَحَدٌ ٱللَّهُ` gibi) bu 35 orneklik
  ayet-yerel seed'in disinda tutuldu; sure/akış decoder varyantinda ele
  alinacak.

## Son review turu karari

- En az bir reviewer tum 35 ayeti `Accuracy: yes` olarak onayladi.
- Kalan `no` cevaplarin ana kismi yukaridaki reddedilen false-negative
  siniflarina giriyor: huroof muqatta'at madd/ghunna, `يُنفِقُونَ` ihfa,
  `أَتَجْعَلُ` qalqalah, `ٱلْأَرْضِ` hamzasi, `أَحَدٌ` hamzasi,
  `ٱلْعَٰلَمِينَ` final harekesi, `هُدًى لِّلْمُتَّقِينَ` idgham bila ghunna
  ve `كُفُوًا` waw temsili.
- Kalan gercek urun karari `PAUSE`/waqf varyantlari ve ayetler-arasi wasl
  varyantlaridir. Bunlar `candidate_v1` icin bloklayici hata degil, ama
  `gold_v1`e gecmeden once ayri export modu olarak tasarlanacak.
- Waqf/PAUSE tasarim turunda karar su sekilde netlesti: V1 icin Option A
  korunacak (`wasl_candidate + PAUSE metadata`), fakat runtime/export roadmap'i
  Option C'ye acik olacak (`wasl_candidate`, `waqf_on_pause`,
  `cross_ayah_wasl`). Ayrinti: [waqf-pause-decision.md](waqf-pause-decision.md).

## Bu turda koda giren degisiklikler

- Long-vowel detection artik shadda/vokal tasiyan `و`/`ي` harflerini yutmuyor.
- Hamzat wasl prefix sonrasi dusuruluyor.
- Shaddali article lam'i korunuyor.
- Nun sakin/tanwin ve mim sakin icin ilk assimilation kurallari eklendi.
- `الٓمٓ`, `يسٓ`, `كٓهيعٓصٓ` icin ilk huroof muqatta'at tablosu eklendi.
- Alef maqsura hem madd tasiyici hem ya konsonanti olarak baglama gore ayrildi.
- Maddah alif sonrasi shadda geldiginde `aa6` madd lazim uretiliyor.
- Dagger alif onceki fatha ile birleserek tek `aa` uretiyor.
- Waw dagger-alif carrier icin `ٱلصَّلَوٰةَ` -> `S S a l aa t a`.
- Ha kinayah icin `هُۥ`/`هِۦ` silah maddi eklendi.
- Maddah tasiyan final waw/yah + sonraki hamza icin `uu4`/`ii4` uretimi
  eklendi.
- Tasiyici harf uzerindeki hamza isareti icin `يَـُٔودُهُۥ` gibi orneklerde
  hamza + madd akisi eklendi.
- Hamzat-wasl ile baslayan sonraki kelimeden once iltiqa al-sakinayn madd
  dusmesi eklendi.
