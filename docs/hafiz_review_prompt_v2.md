# Tilavet Phonemizer — Kapsamlı Hafız Denetim Promptu (V2)

Selamünaleyküm muhterem hocam,

Bu döküman, bir **açık kaynak Kuran-ı Kerim fonem ayrıştırıcısının** dünya çapında yayınlanmadan önce bağımsız hafız denetimine sunulan halidir. Aşağıda projenin amacını, mimari kararlarını, bilinen eksikliklerini ve denetlemenizi istediğimiz 60+ ayet/parçayı bulacaksınız.

**Önemli not:** Sistem nihayetinde ücretsiz, açık kaynaklı, dünya genelinde Müslümanların kullanımına sunulacaktır (iOS uygulaması, eğitim araçları, ASR/TTS modelleri). Bu yüzden **sert, eleştirel ve titiz** bir okuma istiyoruz. "İyi olmuş" yerine "şu açıdan eksik", "şu kararı sorgularım", "şu kelimede Hafs altında farklı olur" tarzı yorumlar bizim için **çok daha değerli**.

Bu dökümana 30-90 dakika ayırmanızı rica ediyoruz. Tüm örnekleri bitiremezseniz dahi, önemli gördüklerinizi işaretlemeniz yeterlidir; özellikle **mimari kararlar (bölüm 4)** ve **bilinen eksiklikler (bölüm 5)** kısımları sizin ilminizden çok faydalanacak.

---

## 1) Projenin Amacı ve Yayın Politikası

### Ne yapıyoruz?

İslâmî bilgisayar bilimleri alanında bir boşluğu kapatmaya çalışıyoruz: **Kuran-ı Kerim tilâvetini, tecvid kurallarına uyumlu, sembolik bir fonem dizisine çeviren açık kaynaklı bir araç.**

Şu an: Arapça mushaf metni → fonem dizisi.

Hedef pipeline:

```
Kuran metni  ─►  [Tilavet Phonemizer]  ─►  fonem dizisi (altın etiket)
Ses kaydı    ─►  [akustik model (CTC)] ─►  fonem olasılıkları
                                        ─►  [decoder] hizalama
                                        ─►  iOS UI: kelime-kelime takip
```

### Neden bu çıktı kritik?

Bu fonem dizisi, yapay zekâ modellerinin eğitim verisidir. Yani:

- Bir tecvid hatası → akustik model **yanlış** öğrenir.
- Bir tutarsızlık → tilâvet takibinde **kayma** olur.
- Bir sembol ayrımı eksik → model **bilemediği** kuralı tahmin edemez.

Sizin uyarılarınız doğrudan **mushaf doğruluğuna** dönüşüyor. Ses tanıma değil; bizzat Kuran tilâveti.

### Yayın politikası

- **Lisans:** MIT (sınırsız ticari/şahsi kullanım, atıf yeterli).
- **Dağıtım:** PyPI, GitHub, dökümantasyon. Türkçe + İngilizce.
- **Hedef kitle:** iOS/Android tilâvet uygulaması yazan müslüman geliştiriciler; hafızlık öğrencileri için ses takibi yapan eğitim araçları; ASR/TTS araştırmacıları; tecvid analiz araçları.
- **Kâr amacı yok.** Sponsor/reklam yok. Tamamen ümmet hizmeti.

---

## 2) Sizden İstediğimiz

Aşağıdaki türden geri bildirimleri ÇOK istiyoruz:

1. **Açık tecvid hataları** — bu fonem dizisi bu kuralı uygulamamış, şöyle olmalı.
2. **Tutarsızlıklar** — bu kelimede A yapmış, başka yerde B yapmış, biri yanlış.
3. **Mimari eleştiri** — bu sembol ayrımı yetersiz, şu kategoriyi de eklemeniz lazım.
4. **Hafs okuluna özel istisnalar** — imâle, işmâm, sekte, vakf-ı kâfî/lâzım/mutlak/münzile farkları.
5. **Kıraat farkları** — Bu Hafs için doğru ama Şube/Şâtıbî/Tayyibe altında farklı olur.
6. **Eksik kelimeler/formlar** — Sembol setinizle şu kelimeyi temsil edemezsiniz.
7. **Eğitim/öğretim açısından** — Hafızlık öğrencilerine yardımcı olacaksa şunu da eklemeli.

**Lütfen yapmayın:**
- Genel olarak güzel olmuş gibi yumuşatıcı yorumlar yerine **somut eleştiri** verin.
- Emin değilseniz "unsure" (kararsız) işaretleyin, bilmediğinizi söylemekten çekinmeyin.
- Türkçe / Arapça / İngilizce — hangisinde rahatsanız onunla yazın.

---

## 3) Çıktı Yapısı ve Sözleşme

Her ayet/parça için iki çıktı veriyoruz:

- **Vasl** — kelimeler bağlı okunur (ayet ortasındaki normal akış).
- **Vakf** — ayet sonunda durulmuş varsayılır (tenvîn düşer, taa-marbuta → `h`, sakin qalqalah harfi → `_qal`, son tabii medd → arıd 6 hareke).

Mushaftaki opsiyonel durak işaretleri (ۖ ۚ ۛ ۗ) çıktıda `PAUSE` olarak görünür. **Bu mecburi vakf değildir** — sistem bu noktalarda vasl yorumunu kullanır (yani nun/tenvîn idğâmı PAUSE üzerinden devam eder).

### Fonem Sembolleri — Sessizler

| Sembol | Harf | | Sembol | Harf | | Sembol | Harf |
|---|---|---|---|---|---|---|---|
| `'` | ء (hemze) | | `b` | ب | | `t` | ت |
| `th` | ث | | `j` | ج | | `H` | ح |
| `kh` | خ | | `d` | د | | `dh` | ذ |
| `r` | ر | | `z` | ز | | `s` | س |
| `sh` | ش | | `S` | ص | | `D` | ض |
| `T` | ط | | `Z` | ظ | | `3` | ع |
| `gh` | غ | | `f` | ف | | `q` | ق |
| `k` | ك | | `l` | ل (tarqîq) | | `L` | **lafzatullah** tafhîm |
| `m` | م | | `n` | ن | | `h` | ه |
| `w` | و konsonant | | `y` | ي konsonant | | | |

### Sesliler & Medd

| Sembol | Anlam |
|---|---|
| `a` `i` `u` | Kısa harekeler |
| `aa` `ii` `uu` | **Medd-i tabii** (2 hareke) |
| `aa4` `ii4` `uu4` | **4 hareke** medd (muttasıl/munfasıl/sıla-kübra) |
| `aa6` `ii6` `uu6` | **6 hareke** medd (lâzım/arıd) |

### Tecvid Varyantları

| Sembol | Anlam |
|---|---|
| `n_g` | Nûn/tenvîn **ihfâ** veya **idgâm ma`al-ğunne** |
| `m_g` | Mîm **idgâm-ı şefevî**, **iklâb**, **ihfâ-ı şefevî** |
| `q_qal` `T_qal` `b_qal` `j_qal` `d_qal` | **Kalkale** |
| `PAUSE` | Mushaf durak işareti (advisory) |

### Tasarım Kuralları

- `L` yalnızca lafzatullah tafhîm. Kesra sonrası `l`.
- Tenvîn + lâm/râ idgâm-ı bilâ-ğunnede `n` düşer.
- Küçük (hançer) elif tek uzun sesli: `m aa`.
- Hemze-i kat`ı her zaman okunur.
- `كُفُوًا` rasimde vâv ile: `k u f u w a n`.
- Mukatta`a harfleri arası ihfâ/idğâm uygulanır.

---

## 4) Sorguladığımız Mimari Kararlar

Lütfen her başlığa bir cevap verin: **onaylama / ret / alternatif öneri**.

### 4.1 PAUSE işaretleri (ۖ ۚ ۛ ۗ) opsiyonel mi, zorunlu mu?

**Mevcut karar:** Opsiyonel (advisory). Vasl modunda nûn/tenvîn ihfâsı PAUSE üzerinden devam eder.
**Argüman:** Mushaf bu işaretleri tercih bildirimi olarak koyar; tilâvet eden durmazsa idğam fire eder.

**Soru:** Bu doğru mu? Yoksa belirli işaretler (ۚ vs ۖ vs ۛ) farklı yorumlanmalı mı?

Cevabınız: ___________________________________________________________

### 4.2 Medd uzunlukları yalnızca 2/4/6

**Mevcut karar:** Tabii (2), muttasıl/munfasıl/sıla-kübra (4), lâzım/arıd (6). Lîn meddi için ayrı sembol yok.

**Soru:** Bu yeterli mi? Lîn meddi, medd-i ıvaz, medd-i tamkîn, medd-i farq için ayrı sembol gerekli mi?

Cevabınız: ___________________________________________________________

### 4.3 Lafzatullah tafhîm/tarqîq → `L`/`l`

**Mevcut karar:** Sadece lafzatullah için ayrım. Diğer harfler için (özellikle râ) yok.

**Soru:** Râ tafhîm/tarqîq için `R`/`r` ayrımı eklemeli miyiz? Hafs altında râ'nın mertebeleri için ayrı sembol mi?

Cevabınız: ___________________________________________________________

### 4.4 `n_g` birleşik sembolü

**Mevcut karar:** İhfâ ve idğam-ı ma`al-ğunne aynı sembolde (`n_g`). Süre/mertebe ayrımı yok.

**Soru:** Ses tanıma için bu ayrım gerekir mi? Yoksa fonetik olarak çok yakın olduğundan tek sembol yeterli mi?

Cevabınız: ___________________________________________________________

### 4.5 Kalkale tek mertebe

**Mevcut karar:** `b_qal`, `d_qal`, `j_qal`, `q_qal`, `T_qal` — tek sembol, suğra/kübra ayrımı yok.

**Soru:** Kalkale-i suğra (kelime ortası) ve kübra (vakf) ayrı sembol almalı mı (`_qal_s` vs `_qal_k`)?

Cevabınız: ___________________________________________________________

### 4.6 İmâle, işmâm, sekte temsili

**Mevcut karar:** Bu özel kıraat kuralları sembol setinde YOK. Örn. `مَجْر۪ىٰهَا` ses olarak farklı okunur ama bunu işaretlemiyoruz.

**Soru:** Bu durumlar için ayrı sembol (örn. `aa_imala`, `_ishm`, `_sakt`)? Yoksa Hafs altında yeterince nadir mi?

Cevabınız: ___________________________________________________________

### 4.7 Vakf modunda arıd lis-sukûn hareke

**Mevcut karar:** Her zaman 6 hareke (`ii6`, `uu6`, `aa6`).

**Soru:** 2/4/6 seçimi reciter tercihi olduğundan, etiket tek değer mi yoksa neutral tag (örn. `ii_arid`) mı?

Cevabınız: ___________________________________________________________

---

## 5) Bilinen Eksiklikler (tarafımızca tespit edilen)

Aşağıdaki konuları zaten **eksik/yanlış** olarak biliyoruz; teyit veya alternatif önerinizi rica ederiz:

1. **`ءَآلذَّكَرَيْنِ` (6:143)** — istifham hemzesi + Allah-formu/şemsiyye. Şu an `aa4 l dh dh` üretiyor; doğrusu `aa6 dh dh` (medd-i farq + lâm sus) olabilir.
2. **Tenvîn-on-hemze (`مَلْجَـًٔا`)** — tatweel-hemze üzerindeki tenvîn doğru işlenmiyor.
3. **Küçük kesra U+06EA (`مَجْر۪ىٰهَا`)** — Hafs altında imâle kuralı var, şu an plain çıktı.
4. **`بِأَيْي۟دٍۢ`, `بِأَييِّكُمُ`** — nadir orthografi.
5. **İdğam-ı nâkıs vs kâmil ayrımı** — örn. `نَخْلُقكُّم`'da Hafs altında ق izi bırakabilir; biz tam absorpsiyon yapıyoruz.
6. **Hâ-i sıla cross-PAUSE** — silah suğra/kübra geçişlerinde PAUSE markerinin etkisi tam test edilmedi.

Bu listede **olmayan** ama olduğunu düşündüğünüz başka eksik:

___________________________________________________________________

---

## 6) Ayet İncelemeleri

Her örnek için aşağıdaki şablonu doldurun (boş bırakabilirsiniz):

```text
Doğruluk: doğru / hatalı / kararsız
Hata yeri:
Mevcut:
Olması gereken:
Kural:
Not / eleştiri / öneri:
```

Vasl ve Vakf farklı yorumlanıyorsa **her ikisi için** ayrı blok ekleyebilirsiniz.

### A. Besmele ve Fâtiha (temel)

#### 1:1

**Odak:** Besmele · lafzatullah tarqîq (kesra sonrası) · lâm şemsiyye

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 1:2

**Odak:** Lâm qameriyye (الحمد) · لِلَّهِ özel formu

**Arapça:** ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ

**Vasl:**

```
' a l H a m d u l i l l aa h i r a b b i l 3 aa l a m ii n a
```

**Vakf:**

```
' a l H a m d u l i l l aa h i r a b b i l 3 aa l a m ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 1:5

**Odak:** Şedde + medd (إِيَّاكَ) iki kez

**Arapça:** إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ

**Vasl:**

```
' i y y aa k a n a 3 b u d u w a ' i y y aa k a n a s t a 3 ii n u
```

**Vakf:**

```
' i y y aa k a n a 3 b u d u w a ' i y y aa k a n a s t a 3 ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 1:6

**Odak:** İltikā-ı sakîneyn (ٱهْدِنَا ٱلصِّرَٰطَ)

**Arapça:** ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ

**Vasl:**

```
' i h d i n a S S i r aa T a l m u s t a q ii m a
```

**Vakf:**

```
' i h d i n a S S i r aa T a l m u s t a q ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 1:7

**Odak:** İzhâr halqī (نْعَ) · medd-i lâzım kalimi muthaqqal (الضَّآلِّينَ)

**Arapça:** صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ

**Vasl:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii n a
```

**Vakf:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### B. Lafzatullah varyasyonları

#### 2:255

**Odak:** Cümle başı (ٱللَّهُ → L L tafhîm) · sıla (هُۥ silah)

**Arapça:** ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ ۚ لَا تَأْخُذُهُۥ سِنَةٌۭ وَلَا نَوْمٌۭ ۚ لَّهُۥ مَا فِى ٱلسَّمَٰوَٰتِ وَمَا فِى ٱلْأَرْضِ ۗ مَن ذَا ٱلَّذِى يَشْفَعُ عِندَهُۥٓ إِلَّا بِإِذْنِهِۦ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَىْءٍۢ مِّنْ عِلْمِهِۦٓ إِلَّا بِمَا شَآءَ ۚ وَسِعَ كُرْسِيُّهُ ٱلسَّمَٰوَٰتِ وَٱلْأَرْضَ ۖ وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ

**Vasl:**

```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu m u PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m u PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D i PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' a PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D a PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii m u
```

**Vakf:**

```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu6 m PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii6 PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa6 PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 112:1

**Odak:** Cümle ortasında tafhîm (هُوَ ٱللَّهُ)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ هُوَ ٱللَّهُ أَحَدٌ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d u n
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 112:2

**Odak:** Cümle başı vasla (ٱللَّهُ ٱلصَّمَدُ)

**Arapça:** ٱللَّهُ ٱلصَّمَدُ

**Vasl:**

```
' a L L aa h u S S a m a d u
```

**Vakf:**

```
' a L L aa h u S S a m a d_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 5:18

**Odak:** Prefix vâv + ٱللَّهُ → tafhîm (وَٱللَّهُ)

**Arapça:** وَقَالَتِ ٱلْيَهُودُ وَٱلنَّصَٰرَىٰ نَحْنُ أَبْنَٰٓؤُا۟ ٱللَّهِ وَأَحِبَّٰٓؤُهُۥ ۚ قُلْ فَلِمَ يُعَذِّبُكُم بِذُنُوبِكُم ۖ بَلْ أَنتُم بَشَرٌۭ مِّمَّنْ خَلَقَ ۚ يَغْفِرُ لِمَن يَشَآءُ وَيُعَذِّبُ مَن يَشَآءُ ۚ وَلِلَّهِ مُلْكُ ٱلسَّمَٰوَٰتِ وَٱلْأَرْضِ وَمَا بَيْنَهُمَا ۖ وَإِلَيْهِ ٱلْمَصِيرُ

**Vasl:**

```
w a q aa l a t i l y a h uu d u w a n n a S aa r aa n a H n u ' a b_qal n aa4 ' u L L aa h i w a ' a H i b b aa4 ' u h uu PAUSE q u l f a l i m a y u 3 a dh dh i b u k u m b i dh u n uu b i k u m PAUSE b a l ' a n_g t u m b a sh a r u m_g m i m m a n kh a l a q a PAUSE y a gh f i r u l i m a n_g y a sh aa4 ' u w a y u 3 a dh dh i b u m a n_g y a sh aa4 ' u PAUSE w a l i l l a h i m u l k u s s a m aa w aa t i w a l ' a r D i w a m aa b a y n a h u m aa PAUSE w a ' i l a y h i l m a S ii r u
```

**Vakf:**

```
w a q aa l a t i l y a h uu d u w a n n a S aa r aa n a H n u ' a b_qal n aa4 ' u L L aa h i w a ' a H i b b aa4 ' u h uu PAUSE q u l f a l i m a y u 3 a dh dh i b u k u m b i dh u n uu b i k u m PAUSE b a l ' a n_g t u m b a sh a r u m_g m i m m a n kh a l a q_qal PAUSE y a gh f i r u l i m a n_g y a sh aa4 ' u w a y u 3 a dh dh i b u m a n_g y a sh aa4 ' PAUSE w a l i l l a h i m u l k u s s a m aa w aa t i w a l ' a r D i w a m aa b a y n a h u m aa6 PAUSE w a ' i l a y h i l m a S ii6 r
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 9:65

**Odak:** Çift prefix أَبِ + ٱللَّهِ → tarqîq

**Arapça:** وَلَئِن سَأَلْتَهُمْ لَيَقُولُنَّ إِنَّمَا كُنَّا نَخُوضُ وَنَلْعَبُ ۚ قُلْ أَبِٱللَّهِ وَءَايَٰتِهِۦ وَرَسُولِهِۦ كُنتُمْ تَسْتَهْزِءُونَ

**Vasl:**

```
w a l a ' i n_g s a ' a l t a h u m l a y a q uu l u n n a ' i n n a m aa k u n n aa n a kh uu D u w a n a l 3 a b u PAUSE q u l ' a b i l l aa h i w a ' aa y aa t i h ii w a r a s uu l i h ii k u n_g t u m t a s t a h z i ' uu n a
```

**Vakf:**

```
w a l a ' i n_g s a ' a l t a h u m l a y a q uu l u n n a ' i n n a m aa k u n n aa n a kh uu D u w a n a l 3 a b_qal PAUSE q u l ' a b i l l aa h i w a ' aa y aa t i h ii w a r a s uu l i h ii k u n_g t u m t a s t a h z i ' uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 12:73

**Odak:** Yemin prefix ت + ٱللَّهِ → tafhîm (kritik)

**Arapça:** قَالُوا۟ تَٱللَّهِ لَقَدْ عَلِمْتُم مَّا جِئْنَا لِنُفْسِدَ فِى ٱلْأَرْضِ وَمَا كُنَّا سَٰرِقِينَ

**Vasl:**

```
q aa l uu t a L L aa h i l a q a d_qal 3 a l i m t u m_g m aa j i ' n aa l i n u f s i d a f i l ' a r D i w a m aa k u n n aa s aa r i q ii n a
```

**Vakf:**

```
q aa l uu t a L L aa h i l a q a d_qal 3 a l i m t u m_g m aa j i ' n aa l i n u f s i d a f i l ' a r D i w a m aa k u n n aa s aa r i q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 10:59

**Odak:** ءَآللَّهُ — istifham hemzesi + Allah

**Arapça:** قُلْ أَرَءَيْتُم مَّآ أَنزَلَ ٱللَّهُ لَكُم مِّن رِّزْقٍۢ فَجَعَلْتُم مِّنْهُ حَرَامًۭا وَحَلَٰلًۭا قُلْ ءَآللَّهُ أَذِنَ لَكُمْ ۖ أَمْ عَلَى ٱللَّهِ تَفْتَرُونَ

**Vasl:**

```
q u l ' a r a ' a y t u m_g m aa4 ' a n_g z a l a L L aa h u l a k u m_g m i r r i z q i n_g f a j a 3 a l t u m_g m i n h u H a r aa m a n_g w a H a l aa l a n_g q u l ' aa4 l l a h u ' a dh i n a l a k u m PAUSE ' a m 3 a l a L L aa h i t a f t a r uu n a
```

**Vakf:**

```
q u l ' a r a ' a y t u m_g m aa4 ' a n_g z a l a L L aa h u l a k u m_g m i r r i z q i n_g f a j a 3 a l t u m_g m i n h u H a r aa m a n_g w a H a l aa l a n_g q u l ' aa4 l l a h u ' a dh i n a l a k u m PAUSE ' a m 3 a l a L L aa h i t a f t a r uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### C. Medd türleri

#### 2:30

**Odak:** Medd-i muttasıl (لِلْمَلَٰٓئِكَةِ)

**Arapça:** وَإِذْ قَالَ رَبُّكَ لِلْمَلَٰٓئِكَةِ إِنِّى جَاعِلٌۭ فِى ٱلْأَرْضِ خَلِيفَةًۭ ۖ قَالُوٓا۟ أَتَجْعَلُ فِيهَا مَن يُفْسِدُ فِيهَا وَيَسْفِكُ ٱلدِّمَآءَ وَنَحْنُ نُسَبِّحُ بِحَمْدِكَ وَنُقَدِّسُ لَكَ ۖ قَالَ إِنِّىٓ أَعْلَمُ مَا لَا تَعْلَمُونَ

**Vasl:**

```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a t a n_g PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k a PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu n a
```

**Vakf:**

```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a h PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 2:156

**Odak:** Medd-i munfasıl cross-word (وَإِنَّآ إِلَيْهِ)

**Arapça:** ٱلَّذِينَ إِذَآ أَصَٰبَتْهُم مُّصِيبَةٌۭ قَالُوٓا۟ إِنَّا لِلَّهِ وَإِنَّآ إِلَيْهِ رَٰجِعُونَ

**Vasl:**

```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu n a
```

**Vakf:**

```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 108:1

**Odak:** Medd-i munfasıl (إِنَّآ أَعْطَيْنَٰكَ)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ إِنَّآ أَعْطَيْنَٰكَ ٱلْكَوْثَرَ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' i n n aa4 ' a 3 T a y n aa k a l k a w th a r a
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' i n n aa4 ' a 3 T a y n aa k a l k a w th a r
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 1:7

**Odak:** Medd-i lâzım kalimi muthaqqal (ٱلضَّآلِّينَ)

**Arapça:** صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ

**Vasl:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii n a
```

**Vakf:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 2:1

**Odak:** Medd-i lâzım harfî muthaqqal (الٓمٓ — lâm-mîm)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ الٓمٓ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 36:1

**Odak:** Medd-i lâzım harfî mukhaffaf (يسٓ)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ يسٓ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i y aa s ii6 n
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i y aa s ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 78:1

**Odak:** Medd-i muttasıl (عَمَّ يَتَسَآءَلُونَ)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ عَمَّ يَتَسَآءَلُونَ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i 3 a m m a y a t a s aa4 ' a l uu n a
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i 3 a m m a y a t a s aa4 ' a l uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 106:1

**Odak:** Medd-i lîn (قُرَيْشٍ)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ لِإِيلَٰفِ قُرَيْشٍ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i l i ' ii l aa f i q u r a y sh i n
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i l i ' ii l aa f i q u r a y sh
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### D. Nûn sâkin / tenvîn kuralları

#### 1:7

**Odak:** İzhâr: نْ + ع halqī

**Arapça:** صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ

**Vasl:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii n a
```

**Vakf:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 113:2

**Odak:** İhfâ: مِن شَرِّ (ن + ش)

**Arapça:** مِن شَرِّ مَا خَلَقَ

**Vasl:**

```
m i n_g sh a r r i m aa kh a l a q a
```

**Vakf:**

```
m i n_g sh a r r i m aa kh a l a q_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 113:3

**Odak:** Tenvîn + hemze izhâr

**Arapça:** وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ

**Vasl:**

```
w a m i n_g sh a r r i gh aa s i q i n ' i dh aa w a q a b a
```

**Vakf:**

```
w a m i n_g sh a r r i gh aa s i q i n ' i dh aa w a q a b_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 2:5

**Odak:** İdgâm/bila ğunne karışık

**Arapça:** أُو۟لَٰٓئِكَ عَلَىٰ هُدًۭى مِّن رَّبِّهِمْ ۖ وَأُو۟لَٰٓئِكَ هُمُ ٱلْمُفْلِحُونَ

**Vasl:**

```
' uu l aa4 ' i k a 3 a l aa h u d a m_g m i r r a b b i h i m PAUSE w a ' uu l aa4 ' i k a h u m u l m u f l i H uu n a
```

**Vakf:**

```
' uu l aa4 ' i k a 3 a l aa h u d a m_g m i r r a b b i h i m PAUSE w a ' uu l aa4 ' i k a h u m u l m u f l i H uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 112:4

**Odak:** İdgâm bilâ ğunne: يَكُن لَّهُۥ (ن + ل)

**Arapça:** وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ

**Vasl:**

```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d u n
```

**Vakf:**

```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 2:18

**Odak:** İklâb: سَمِيعٌۢ بَصِيرٌ

**Arapça:** صُمٌّۢ بُكْمٌ عُمْىٌۭ فَهُمْ لَا يَرْجِعُونَ

**Vasl:**

```
S u m m u m_g b u k m u n 3 u m y u n_g f a h u m l aa y a r j i 3 uu n a
```

**Vakf:**

```
S u m m u m_g b u k m u n 3 u m y u n_g f a h u m l aa y a r j i 3 uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### E. Mîm sâkin kuralları

#### 2:3

**Odak:** İzhâr şefevî (هُمْ يُنفِقُونَ)

**Arapça:** ٱلَّذِينَ يُؤْمِنُونَ بِٱلْغَيْبِ وَيُقِيمُونَ ٱلصَّلَوٰةَ وَمِمَّا رَزَقْنَٰهُمْ يُنفِقُونَ

**Vasl:**

```
' a l l a dh ii n a y u ' m i n uu n a b i l gh a y b i w a y u q ii m uu n a S S a l aa t a w a m i m m aa r a z a q_qal n aa h u m y u n_g f i q uu n a
```

**Vakf:**

```
' a l l a dh ii n a y u ' m i n uu n a b i l gh a y b i w a y u q ii m uu n a S S a l aa t a w a m i m m aa r a z a q_qal n aa h u m y u n_g f i q uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 2:156

**Odak:** İdgâm şefevî (هُم مُّصِيبَةٌ)

**Arapça:** ٱلَّذِينَ إِذَآ أَصَٰبَتْهُم مُّصِيبَةٌۭ قَالُوٓا۟ إِنَّا لِلَّهِ وَإِنَّآ إِلَيْهِ رَٰجِعُونَ

**Vasl:**

```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu n a
```

**Vakf:**

```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 1:7

**Odak:** Mîm sâkin sonrası (عَلَيْهِمْ غَيْرِ)

**Arapça:** صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ

**Vasl:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii n a
```

**Vakf:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### F. Kalkale

#### 2:3

**Odak:** Kalkale-i suğra: رَزَقْنَٰهُمْ (ق mid-word)

**Arapça:** ٱلَّذِينَ يُؤْمِنُونَ بِٱلْغَيْبِ وَيُقِيمُونَ ٱلصَّلَوٰةَ وَمِمَّا رَزَقْنَٰهُمْ يُنفِقُونَ

**Vasl:**

```
' a l l a dh ii n a y u ' m i n uu n a b i l gh a y b i w a y u q ii m uu n a S S a l aa t a w a m i m m aa r a z a q_qal n aa h u m y u n_g f i q uu n a
```

**Vakf:**

```
' a l l a dh ii n a y u ' m i n uu n a b i l gh a y b i w a y u q ii m uu n a S S a l aa t a w a m i m m aa r a z a q_qal n aa h u m y u n_g f i q uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 112:3

**Odak:** Kalkale-i suğra: يَلِدْ / يُولَدْ (د)

**Arapça:** لَمْ يَلِدْ وَلَمْ يُولَدْ

**Vasl:**

```
l a m y a l i d_qal w a l a m y uu l a d_qal
```

**Vakf:**

```
l a m y a l i d_qal w a l a m y uu l a d_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 108:3

**Odak:** Kalkale + kameriyye: ٱلْأَبْتَرُ (ب)

**Arapça:** إِنَّ شَانِئَكَ هُوَ ٱلْأَبْتَرُ

**Vasl:**

```
' i n n a sh aa n i ' a k a h u w a l ' a b_qal t a r u
```

**Vakf:**

```
' i n n a sh aa n i ' a k a h u w a l ' a b_qal t a r
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 113:1

**Odak:** Vakf qalqalah kubra: ٱلْفَلَقِ → q_qal

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i l f a l a q i
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i l f a l a q_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### G. İdgâm (kelime-içi ve sınırlar)

#### 2:233

**Odak:** Mütecânis: أَرَدتُّمْ (د+ت)

**Arapça:** ۞ وَٱلْوَٰلِدَٰتُ يُرْضِعْنَ أَوْلَٰدَهُنَّ حَوْلَيْنِ كَامِلَيْنِ ۖ لِمَنْ أَرَادَ أَن يُتِمَّ ٱلرَّضَاعَةَ ۚ وَعَلَى ٱلْمَوْلُودِ لَهُۥ رِزْقُهُنَّ وَكِسْوَتُهُنَّ بِٱلْمَعْرُوفِ ۚ لَا تُكَلَّفُ نَفْسٌ إِلَّا وُسْعَهَا ۚ لَا تُضَآرَّ وَٰلِدَةٌۢ بِوَلَدِهَا وَلَا مَوْلُودٌۭ لَّهُۥ بِوَلَدِهِۦ ۚ وَعَلَى ٱلْوَارِثِ مِثْلُ ذَٰلِكَ ۗ فَإِنْ أَرَادَا فِصَالًا عَن تَرَاضٍۢ مِّنْهُمَا وَتَشَاوُرٍۢ فَلَا جُنَاحَ عَلَيْهِمَا ۗ وَإِنْ أَرَدتُّمْ أَن تَسْتَرْضِعُوٓا۟ أَوْلَٰدَكُمْ فَلَا جُنَاحَ عَلَيْكُمْ إِذَا سَلَّمْتُم مَّآ ءَاتَيْتُم بِٱلْمَعْرُوفِ ۗ وَٱتَّقُوا۟ ٱللَّهَ وَٱعْلَمُوٓا۟ أَنَّ ٱللَّهَ بِمَا تَعْمَلُونَ بَصِيرٌۭ

**Vasl:**

```
PAUSE w a l w aa l i d aa t u y u r D i 3 n a ' a w l aa d a h u n n a H a w l a y n i k aa m i l a y n i PAUSE l i m a n ' a r aa d a ' a n_g y u t i m m a r r a D aa 3 a t a PAUSE w a 3 a l a l m a w l uu d i l a h uu r i z q u h u n n a w a k i s w a t u h u n n a b i l m a 3 r uu f i PAUSE l aa t u k a l l a f u n a f s u n ' i l l aa w u s 3 a h aa PAUSE l aa t u D aa6 r r a w aa l i d a t u m_g b i w a l a d i h aa w a l aa m a w l uu d u l l a h uu b i w a l a d i h ii PAUSE w a 3 a l a l w aa r i th i m i th l u dh aa l i k a PAUSE f a ' i n ' a r aa d aa f i S aa l a n 3 a n_g t a r aa D i m_g m i n_g h u m aa w a t a sh aa w u r i n_g f a l aa j u n aa H a 3 a l a y h i m aa PAUSE w a ' i n ' a r a t t u m ' a n_g t a s t a r D i 3 uu4 ' a w l aa d a k u m f a l aa j u n aa H a 3 a l a y k u m ' i dh aa s a l l a m t u m_g m aa4 ' aa t a y t u m b i l m a 3 r uu f i PAUSE w a t t a q u L L aa h a w a 3 l a m uu4 ' a n n a L L aa h a b i m aa t a 3 m a l uu n a b a S ii r u n
```

**Vakf:**

```
PAUSE w a l w aa l i d aa t u y u r D i 3 n a ' a w l aa d a h u n n a H a w l a y n i k aa m i l a y n PAUSE l i m a n ' a r aa d a ' a n_g y u t i m m a r r a D aa 3 a h PAUSE w a 3 a l a l m a w l uu d i l a h uu r i z q u h u n n a w a k i s w a t u h u n n a b i l m a 3 r uu6 f PAUSE l aa t u k a l l a f u n a f s u n ' i l l aa w u s 3 a h aa6 PAUSE l aa t u D aa6 r r a w aa l i d a t u m_g b i w a l a d i h aa w a l aa m a w l uu d u l l a h uu b i w a l a d i h ii6 PAUSE w a 3 a l a l w aa r i th i m i th l u dh aa l i k PAUSE f a ' i n ' a r aa d aa f i S aa l a n 3 a n_g t a r aa D i m_g m i n_g h u m aa w a t a sh aa w u r i n_g f a l aa j u n aa H a 3 a l a y h i m aa6 PAUSE w a ' i n ' a r a t t u m ' a n_g t a s t a r D i 3 uu4 ' a w l aa d a k u m f a l aa j u n aa H a 3 a l a y k u m ' i dh aa s a l l a m t u m_g m aa4 ' aa t a y t u m b i l m a 3 r uu6 f PAUSE w a t t a q u L L aa h a w a 3 l a m uu4 ' a n n a L L aa h a b i m aa t a 3 m a l uu n a b a S ii6 r
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 77:20

**Odak:** Mütekārib: نَخْلُقكُّم (ق+ك)

**Arapça:** أَلَمْ نَخْلُقكُّم مِّن مَّآءٍۢ مَّهِينٍۢ

**Vasl:**

```
' a l a m n a kh l u k k u m_g m i m_g m aa4 ' i m_g m a h ii n i n
```

**Vakf:**

```
' a l a m n a kh l u k k u m_g m i m_g m aa4 ' i m_g m a h ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 4:78

**Odak:** Mütemâsil: يُدْرِككُّمُ (ك+ك)

**Arapça:** أَيْنَمَا تَكُونُوا۟ يُدْرِككُّمُ ٱلْمَوْتُ وَلَوْ كُنتُمْ فِى بُرُوجٍۢ مُّشَيَّدَةٍۢ ۗ وَإِن تُصِبْهُمْ حَسَنَةٌۭ يَقُولُوا۟ هَٰذِهِۦ مِنْ عِندِ ٱللَّهِ ۖ وَإِن تُصِبْهُمْ سَيِّئَةٌۭ يَقُولُوا۟ هَٰذِهِۦ مِنْ عِندِكَ ۚ قُلْ كُلٌّۭ مِّنْ عِندِ ٱللَّهِ ۖ فَمَالِ هَٰٓؤُلَآءِ ٱلْقَوْمِ لَا يَكَادُونَ يَفْقَهُونَ حَدِيثًۭا

**Vasl:**

```
' a y n a m aa t a k uu n uu y u d_qal r i k k u m u l m a w t u w a l a w k u n_g t u m f ii b u r uu j i m_g m u sh a y y a d a t i n_g PAUSE w a ' i n_g t u S i b_qal h u m H a s a n a t u n_g y a q uu l uu h aa dh i h ii m i n 3 i n_g d i l l aa h i PAUSE w a ' i n_g t u S i b_qal h u m s a y y i ' a t u n_g y a q uu l uu h aa dh i h ii m i n 3 i n_g d i k a PAUSE q u l k u l l u m_g m i n 3 i n_g d i l l aa h i PAUSE f a m aa l i h aa4 ' u l aa4 ' i l q a w m i l aa y a k aa d uu n a y a f q a h uu n a H a d ii th a n
```

**Vakf:**

```
' a y n a m aa t a k uu n uu y u d_qal r i k k u m u l m a w t u w a l a w k u n_g t u m f ii b u r uu j i m_g m u sh a y y a d a h PAUSE w a ' i n_g t u S i b_qal h u m H a s a n a t u n_g y a q uu l uu h aa dh i h ii m i n 3 i n_g d i l l aa6 h PAUSE w a ' i n_g t u S i b_qal h u m s a y y i ' a t u n_g y a q uu l uu h aa dh i h ii m i n 3 i n_g d i k PAUSE q u l k u l l u m_g m i n 3 i n_g d i l l aa6 h PAUSE f a m aa l i h aa4 ' u l aa4 ' i l q a w m i l aa y a k aa d uu n a y a f q a h uu n a H a d ii6 th
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 11:42

**Odak:** Cross-PAUSE mîm idgâmı (ٱرْكَب مَّعَنَا)

**Arapça:** وَهِىَ تَجْرِى بِهِمْ فِى مَوْجٍۢ كَٱلْجِبَالِ وَنَادَىٰ نُوحٌ ٱبْنَهُۥ وَكَانَ فِى مَعْزِلٍۢ يَٰبُنَىَّ ٱرْكَب مَّعَنَا وَلَا تَكُن مَّعَ ٱلْكَٰفِرِينَ

**Vasl:**

```
w a h i y a t a j_qal r ii b i h i m f ii m a w j i n_g k a l j i b aa l i w a n aa d aa n uu H u m_g b_qal n a h uu w a k aa n a f ii m a 3 z i l i n_g y aa b u n a y y a r k a b m m a 3 a n aa w a l aa t a k u m_g m a 3 a l k aa f i r ii n a
```

**Vakf:**

```
w a h i y a t a j_qal r ii b i h i m f ii m a w j i n_g k a l j i b aa l i w a n aa d aa n uu H u m_g b_qal n a h uu w a k aa n a f ii m a 3 z i l i n_g y aa b u n a y y a r k a b m m a 3 a n aa w a l aa t a k u m_g m a 3 a l k aa f i r ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### H. Hurûf-ı mukatta‘a

#### 2:1

**Odak:** الٓمٓ — 3 harf

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ الٓمٓ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 19:1

**Odak:** كٓهيعٓصٓ — 5 harf

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ كٓهيعٓصٓ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i k aa6 f h aa y aa 3 aa6 y n_g S aa6 d
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i k aa6 f h aa y aa 3 aa6 y n_g S aa6 d_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 36:1

**Odak:** يسٓ — 2 harf

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ يسٓ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i y aa s ii6 n
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i y aa s ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 42:2

**Odak:** عسٓقٓ — 3 harf standalone

**Arapça:** عٓسٓقٓ

**Vasl:**

```
3 aa6 y n_g s ii6 n_g q aa6 f
```

**Vakf:**

```
3 aa6 y n_g s ii6 n_g q aa6 f
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 40:1

**Odak:** حمٓ — 2 harf

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ حمٓ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i H aa m ii6 m
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i H aa m ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 20:1

**Odak:** طه — 2 harf, medd-i tabii

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ طه

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i T h
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i T h
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### I. Çoklu prefix ve vasla

#### 16:16

**Odak:** وَبِٱلنَّجْمِ — multi-prefix + şemsiyye

**Arapça:** وَعَلَٰمَٰتٍۢ ۚ وَبِٱلنَّجْمِ هُمْ يَهْتَدُونَ

**Vasl:**

```
w a 3 a l aa m aa t i n_g PAUSE w a b i n n a j_qal m i h u m y a h t a d uu n a
```

**Vakf:**

```
w a 3 a l aa m aa6 t PAUSE w a b i n n a j_qal m i h u m y a h t a d uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 24:47

**Odak:** وَبِٱلرَّسُولِ — şemsiyye râ

**Arapça:** وَيَقُولُونَ ءَامَنَّا بِٱللَّهِ وَبِٱلرَّسُولِ وَأَطَعْنَا ثُمَّ يَتَوَلَّىٰ فَرِيقٌۭ مِّنْهُم مِّنۢ بَعْدِ ذَٰلِكَ ۚ وَمَآ أُو۟لَٰٓئِكَ بِٱلْمُؤْمِنِينَ

**Vasl:**

```
w a y a q uu l uu n a ' aa m a n n aa b i l l aa h i w a b i r r a s uu l i w a ' a T a 3 n aa th u m m a y a t a w a l l aa f a r ii q u m_g m i m_g h u m_g m i m_g b a 3 d i dh aa l i k a PAUSE w a m aa4 ' uu l aa4 ' i k a b i l m u ' m i n ii n a
```

**Vakf:**

```
w a y a q uu l uu n a ' aa m a n n aa b i l l aa h i w a b i r r a s uu l i w a ' a T a 3 n aa th u m m a y a t a w a l l aa f a r ii q u m_g m i m_g h u m_g m i m_g b a 3 d i dh aa l i k PAUSE w a m aa4 ' uu l aa4 ' i k a b i l m u ' m i n ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 35:25

**Odak:** وَبِٱلزُّبُرِ — şemsiyye zây

**Arapça:** وَإِن يُكَذِّبُوكَ فَقَدْ كَذَّبَ ٱلَّذِينَ مِن قَبْلِهِمْ جَآءَتْهُمْ رُسُلُهُم بِٱلْبَيِّنَٰتِ وَبِٱلزُّبُرِ وَبِٱلْكِتَٰبِ ٱلْمُنِيرِ

**Vasl:**

```
w a ' i n_g y u k a dh dh i b uu k a f a q a d_qal k a dh dh a b a l l a dh ii n a m i n_g q a b_qal l i h i m j aa4 ' a t h u m r u s u l u h u m b i l b a y y i n aa t i w a b i z z u b u r i w a b i l k i t aa b i l m u n ii r i
```

**Vakf:**

```
w a ' i n_g y u k a dh dh i b uu k a f a q a d_qal k a dh dh a b a l l a dh ii n a m i n_g q a b_qal l i h i m j aa4 ' a t h u m r u s u l u h u m b i l b a y y i n aa t i w a b i z z u b u r i w a b i l k i t aa b i l m u n ii6 r
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### J. Li-prefix bare article

#### 2:83

**Odak:** لِلنَّاسِ

**Arapça:** وَإِذْ أَخَذْنَا مِيثَٰقَ بَنِىٓ إِسْرَٰٓءِيلَ لَا تَعْبُدُونَ إِلَّا ٱللَّهَ وَبِٱلْوَٰلِدَيْنِ إِحْسَانًۭا وَذِى ٱلْقُرْبَىٰ وَٱلْيَتَٰمَىٰ وَٱلْمَسَٰكِينِ وَقُولُوا۟ لِلنَّاسِ حُسْنًۭا وَأَقِيمُوا۟ ٱلصَّلَوٰةَ وَءَاتُوا۟ ٱلزَّكَوٰةَ ثُمَّ تَوَلَّيْتُمْ إِلَّا قَلِيلًۭا مِّنكُمْ وَأَنتُم مُّعْرِضُونَ

**Vasl:**

```
w a ' i dh ' a kh a dh n aa m ii th aa q a b a n ii4 ' i s r aa4 ' ii l a l aa t a 3 b u d uu n a ' i l l a L L aa h a w a b i l w aa l i d a y n i ' i H s aa n a n_g w a dh i l q u r b aa w a l y a t aa m aa w a l m a s aa k ii n i w a q uu l uu l i n n aa s i H u s n a n_g w a ' a q ii m u S S a l aa t a w a ' aa t u z z a k aa t a th u m m a t a w a l l a y t u m ' i l l aa q a l ii l a m_g m i n_g k u m w a ' a n_g t u m_g m u 3 r i D uu n a
```

**Vakf:**

```
w a ' i dh ' a kh a dh n aa m ii th aa q a b a n ii4 ' i s r aa4 ' ii l a l aa t a 3 b u d uu n a ' i l l a L L aa h a w a b i l w aa l i d a y n i ' i H s aa n a n_g w a dh i l q u r b aa w a l y a t aa m aa w a l m a s aa k ii n i w a q uu l uu l i n n aa s i H u s n a n_g w a ' a q ii m u S S a l aa t a w a ' aa t u z z a k aa t a th u m m a t a w a l l a y t u m ' i l l aa q a l ii l a m_g m i n_g k u m w a ' a n_g t u m_g m u 3 r i D uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 6:143

**Odak:** فَلِلذَّكَرِ

**Arapça:** ثَمَٰنِيَةَ أَزْوَٰجٍۢ ۖ مِّنَ ٱلضَّأْنِ ٱثْنَيْنِ وَمِنَ ٱلْمَعْزِ ٱثْنَيْنِ ۗ قُلْ ءَآلذَّكَرَيْنِ حَرَّمَ أَمِ ٱلْأُنثَيَيْنِ أَمَّا ٱشْتَمَلَتْ عَلَيْهِ أَرْحَامُ ٱلْأُنثَيَيْنِ ۖ نَبِّـُٔونِى بِعِلْمٍ إِن كُنتُمْ صَٰدِقِينَ

**Vasl:**

```
th a m aa n i y a t a ' a z w aa j i m_g PAUSE m i n a D D a ' n i th n a y n i w a m i n a l m a 3 z i th n a y n i PAUSE q u l ' aa4 l dh dh a k a r a y n i H a r r a m a ' a m i l ' u n_g th a y a y n i ' a m m a sh t a m a l a t 3 a l a y h i ' a r H aa m u l ' u n_g th a y a y n i PAUSE n a b b i ' uu n ii b i 3 i l m i n ' i n_g k u n_g t u m S aa d i q ii n a
```

**Vakf:**

```
th a m aa n i y a t a ' a z w aa6 j_qal PAUSE m m i n a D D a ' n i th n a y n i w a m i n a l m a 3 z i th n a y n PAUSE q u l ' aa4 l dh dh a k a r a y n i H a r r a m a ' a m i l ' u n_g th a y a y n i ' a m m a sh t a m a l a t 3 a l a y h i ' a r H aa m u l ' u n_g th a y a y n PAUSE n a b b i ' uu n ii b i 3 i l m i n ' i n_g k u n_g t u m S aa d i q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### K. Hâ-i sıla (silah suğra/kübra)

#### 2:255

**Odak:** Ayet el-Kürsî — sıla çeşitli pozisyonlarda

**Arapça:** ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ ۚ لَا تَأْخُذُهُۥ سِنَةٌۭ وَلَا نَوْمٌۭ ۚ لَّهُۥ مَا فِى ٱلسَّمَٰوَٰتِ وَمَا فِى ٱلْأَرْضِ ۗ مَن ذَا ٱلَّذِى يَشْفَعُ عِندَهُۥٓ إِلَّا بِإِذْنِهِۦ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَىْءٍۢ مِّنْ عِلْمِهِۦٓ إِلَّا بِمَا شَآءَ ۚ وَسِعَ كُرْسِيُّهُ ٱلسَّمَٰوَٰتِ وَٱلْأَرْضَ ۖ وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ

**Vasl:**

```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu m u PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m u PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D i PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' a PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D a PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii m u
```

**Vakf:**

```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu6 m PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii6 PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa6 PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 112:4

**Odak:** لَّهُۥ كُفُوًا — silah suğra

**Arapça:** وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ

**Vasl:**

```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d u n
```

**Vakf:**

```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### L. Soru hemzesi (BİLİNEN EDGE CASE)

#### 6:143

**Odak:** ءَآلذَّكَرَيْنِ — istifham + medd-i farq

**Arapça:** ثَمَٰنِيَةَ أَزْوَٰجٍۢ ۖ مِّنَ ٱلضَّأْنِ ٱثْنَيْنِ وَمِنَ ٱلْمَعْزِ ٱثْنَيْنِ ۗ قُلْ ءَآلذَّكَرَيْنِ حَرَّمَ أَمِ ٱلْأُنثَيَيْنِ أَمَّا ٱشْتَمَلَتْ عَلَيْهِ أَرْحَامُ ٱلْأُنثَيَيْنِ ۖ نَبِّـُٔونِى بِعِلْمٍ إِن كُنتُمْ صَٰدِقِينَ

**Vasl:**

```
th a m aa n i y a t a ' a z w aa j i m_g PAUSE m i n a D D a ' n i th n a y n i w a m i n a l m a 3 z i th n a y n i PAUSE q u l ' aa4 l dh dh a k a r a y n i H a r r a m a ' a m i l ' u n_g th a y a y n i ' a m m a sh t a m a l a t 3 a l a y h i ' a r H aa m u l ' u n_g th a y a y n i PAUSE n a b b i ' uu n ii b i 3 i l m i n ' i n_g k u n_g t u m S aa d i q ii n a
```

**Vakf:**

```
th a m aa n i y a t a ' a z w aa6 j_qal PAUSE m m i n a D D a ' n i th n a y n i w a m i n a l m a 3 z i th n a y n PAUSE q u l ' aa4 l dh dh a k a r a y n i H a r r a m a ' a m i l ' u n_g th a y a y n i ' a m m a sh t a m a l a t 3 a l a y h i ' a r H aa m u l ' u n_g th a y a y n PAUSE n a b b i ' uu n ii b i 3 i l m i n ' i n_g k u n_g t u m S aa d i q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 10:59

**Odak:** ءَآللَّهُ — istifham + Allah

**Arapça:** قُلْ أَرَءَيْتُم مَّآ أَنزَلَ ٱللَّهُ لَكُم مِّن رِّزْقٍۢ فَجَعَلْتُم مِّنْهُ حَرَامًۭا وَحَلَٰلًۭا قُلْ ءَآللَّهُ أَذِنَ لَكُمْ ۖ أَمْ عَلَى ٱللَّهِ تَفْتَرُونَ

**Vasl:**

```
q u l ' a r a ' a y t u m_g m aa4 ' a n_g z a l a L L aa h u l a k u m_g m i r r i z q i n_g f a j a 3 a l t u m_g m i n h u H a r aa m a n_g w a H a l aa l a n_g q u l ' aa4 l l a h u ' a dh i n a l a k u m PAUSE ' a m 3 a l a L L aa h i t a f t a r uu n a
```

**Vakf:**

```
q u l ' a r a ' a y t u m_g m aa4 ' a n_g z a l a L L aa h u l a k u m_g m i r r i z q i n_g f a j a 3 a l t u m_g m i n h u H a r aa m a n_g w a H a l aa l a n_g q u l ' aa4 l l a h u ' a dh i n a l a k u m PAUSE ' a m 3 a l a L L aa h i t a f t a r uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 10:51

**Odak:** ءَآلْـَٰٔنَ — istifham + medd-i lâzım kalimi mukhaffaf

**Arapça:** أَثُمَّ إِذَا مَا وَقَعَ ءَامَنتُم بِهِۦٓ ۚ ءَآلْـَٰٔنَ وَقَدْ كُنتُم بِهِۦ تَسْتَعْجِلُونَ

**Vasl:**

```
' a th u m m a ' i dh aa m aa w a q a 3 a ' aa m a n_g t u m b i h ii4 PAUSE ' aa4 l ' a n a w a q a d_qal k u n_g t u m b i h ii t a s t a 3 j i l uu n a
```

**Vakf:**

```
' a th u m m a ' i dh aa m aa w a q a 3 a ' aa m a n_g t u m b i h ii4 PAUSE ' aa4 l ' a n a w a q a d_qal k u n_g t u m b i h ii t a s t a 3 j i l uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### M. Tâ-i merbuta

#### 2:30

**Odak:** خَلِيفَةًۭ — wasl: t, waqf: h

**Arapça:** وَإِذْ قَالَ رَبُّكَ لِلْمَلَٰٓئِكَةِ إِنِّى جَاعِلٌۭ فِى ٱلْأَرْضِ خَلِيفَةًۭ ۖ قَالُوٓا۟ أَتَجْعَلُ فِيهَا مَن يُفْسِدُ فِيهَا وَيَسْفِكُ ٱلدِّمَآءَ وَنَحْنُ نُسَبِّحُ بِحَمْدِكَ وَنُقَدِّسُ لَكَ ۖ قَالَ إِنِّىٓ أَعْلَمُ مَا لَا تَعْلَمُونَ

**Vasl:**

```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a t a n_g PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k a PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu n a
```

**Vakf:**

```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a h PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 114:6

**Odak:** ٱلْجِنَّةِ — vasl t

**Arapça:** مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ

**Vasl:**

```
m i n a l j i n n a t i w a n n aa s i
```

**Vakf:**

```
m i n a l j i n n a t i w a n n aa6 s
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### N. Tatweel-hemze ortografisi

#### 9:44

**Odak:** يَسْتَـْٔذِنُكَ — tatweel + sakin hemze

**Arapça:** لَا يَسْتَـْٔذِنُكَ ٱلَّذِينَ يُؤْمِنُونَ بِٱللَّهِ وَٱلْيَوْمِ ٱلْءَاخِرِ أَن يُجَٰهِدُوا۟ بِأَمْوَٰلِهِمْ وَأَنفُسِهِمْ ۗ وَٱللَّهُ عَلِيمٌۢ بِٱلْمُتَّقِينَ

**Vasl:**

```
l aa y a s t a ' dh i n u k a l l a dh ii n a y u ' m i n uu n a b i l l aa h i w a l y a w m i l ' aa kh i r i ' a n_g y u j aa h i d uu b i ' a m w aa l i h i m w a ' a n_g f u s i h i m PAUSE w a L L aa h u 3 a l ii m u m_g b i l m u t t a q ii n a
```

**Vakf:**

```
l aa y a s t a ' dh i n u k a l l a dh ii n a y u ' m i n uu n a b i l l aa h i w a l y a w m i l ' aa kh i r i ' a n_g y u j aa h i d uu b i ' a m w aa l i h i m w a ' a n_g f u s i h i m PAUSE w a L L aa h u 3 a l ii m u m_g b i l m u t t a q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 3:14

**Odak:** ٱلْمَـَٔابِ — tatweel + hemze + medd

**Arapça:** زُيِّنَ لِلنَّاسِ حُبُّ ٱلشَّهَوَٰتِ مِنَ ٱلنِّسَآءِ وَٱلْبَنِينَ وَٱلْقَنَٰطِيرِ ٱلْمُقَنطَرَةِ مِنَ ٱلذَّهَبِ وَٱلْفِضَّةِ وَٱلْخَيْلِ ٱلْمُسَوَّمَةِ وَٱلْأَنْعَٰمِ وَٱلْحَرْثِ ۗ ذَٰلِكَ مَتَٰعُ ٱلْحَيَوٰةِ ٱلدُّنْيَا ۖ وَٱللَّهُ عِندَهُۥ حُسْنُ ٱلْمَـَٔابِ

**Vasl:**

```
z u y y i n a l i n n aa s i H u b b u sh sh a h a w aa t i m i n a n n i s aa4 ' i w a l b a n ii n a w a l q a n aa T ii r i l m u q a n_g T a r a t i m i n a dh dh a h a b i w a l f i D D a t i w a l kh a y l i l m u s a w w a m a t i w a l ' a n_g 3 aa m i w a l H a r th i PAUSE dh aa l i k a m a t aa 3 u l H a y aa t i d d u n_g y aa PAUSE w a L L aa h u 3 i n_g d a h uu H u s n u l m a ' aa b i
```

**Vakf:**

```
z u y y i n a l i n n aa s i H u b b u sh sh a h a w aa t i m i n a n n i s aa4 ' i w a l b a n ii n a w a l q a n aa T ii r i l m u q a n_g T a r a t i m i n a dh dh a h a b i w a l f i D D a t i w a l kh a y l i l m u s a w w a m a t i w a l ' a n_g 3 aa m i w a l H a r th PAUSE dh aa l i k a m a t aa 3 u l H a y aa t i d d u n_g y aa6 PAUSE w a L L aa h u 3 i n_g d a h uu H u s n u l m a ' aa6 b_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 9:57

**Odak:** مَلْجَـًٔا — tatweel + tenvîn-on-hemze

**Arapça:** لَوْ يَجِدُونَ مَلْجَـًٔا أَوْ مَغَٰرَٰتٍ أَوْ مُدَّخَلًۭا لَّوَلَّوْا۟ إِلَيْهِ وَهُمْ يَجْمَحُونَ

**Vasl:**

```
l a w y a j i d uu n a m a l j ' aa4 ' a w m a gh aa r aa t i n ' a w m u d d a kh a l a l l a w a l l a w ' i l a y h i w a h u m y a j_qal m a H uu n a
```

**Vakf:**

```
l a w y a j i d uu n a m a l j ' aa4 ' a w m a gh aa r aa t i n ' a w m u d d a kh a l a l l a w a l l a w ' i l a y h i w a h u m y a j_qal m a H uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 6:26

**Odak:** وَيَنْـَٔوْنَ — nûn sâkin + tatweel hemze

**Arapça:** وَهُمْ يَنْهَوْنَ عَنْهُ وَيَنْـَٔوْنَ عَنْهُ ۖ وَإِن يُهْلِكُونَ إِلَّآ أَنفُسَهُمْ وَمَا يَشْعُرُونَ

**Vasl:**

```
w a h u m y a n h a w n a 3 a n_g h u w a y a n_g w n a 3 a n_g h u PAUSE w a ' i n_g y u h l i k uu n a ' i l l aa4 ' a n_g f u s a h u m w a m aa y a sh 3 u r uu n a
```

**Vakf:**

```
w a h u m y a n h a w n a 3 a n_g h u w a y a n_g w n a 3 a n h PAUSE w a ' i n_g y u h l i k uu n a ' i l l aa4 ' a n_g f u s a h u m w a m aa y a sh 3 u r uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### O. Nadir/özel orthografik işaretler

#### 11:41

**Odak:** مَجْر۪ىٰهَا — küçük kesra U+06EA (imâle?)

**Arapça:** ۞ وَقَالَ ٱرْكَبُوا۟ فِيهَا بِسْمِ ٱللَّهِ مَجْر۪ىٰهَا وَمُرْسَىٰهَآ ۚ إِنَّ رَبِّى لَغَفُورٌۭ رَّحِيمٌۭ

**Vasl:**

```
PAUSE w a q aa l a r k a b uu f ii h aa b i s m i l l aa h i m a j_qal r h aa w a m u r s aa h aa4 PAUSE ' i n n a r a b b ii l a gh a f uu r u r r a H ii m u n
```

**Vakf:**

```
PAUSE w a q aa l a r k a b uu f ii h aa b i s m i l l aa h i m a j_qal r h aa w a m u r s aa h aa4 PAUSE ' i n n a r a b b ii l a gh a f uu r u r r a H ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 51:47

**Odak:** بِأَيْي۟دٍۢ — small high seen U+06DF

**Arapça:** وَٱلسَّمَآءَ بَنَيْنَٰهَا بِأَيْي۟دٍۢ وَإِنَّا لَمُوسِعُونَ

**Vasl:**

```
w a s s a m aa4 ' a b a n a y n aa h aa b i ' a y y d i n_g w a ' i n n aa l a m uu s i 3 uu n a
```

**Vakf:**

```
w a s s a m aa4 ' a b a n a y n aa h aa b i ' a y y d i n_g w a ' i n n aa l a m uu s i 3 uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 68:6

**Odak:** بِأَييِّكُمُ — çift yâ

**Arapça:** بِأَييِّكُمُ ٱلْمَفْتُونُ

**Vasl:**

```
b i ' a y y y i k u m u l m a f t uu n u
```

**Vakf:**

```
b i ' a y y y i k u m u l m a f t uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

### P. Vakf modu kapsamlı

#### 1:1

**Odak:** الرحيم vakf → ii6 m

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 1:4

**Odak:** ٱلدِّينِ vakf

**Arapça:** مَٰلِكِ يَوْمِ ٱلدِّينِ

**Vasl:**

```
m aa l i k i y a w m i d d ii n i
```

**Vakf:**

```
m aa l i k i y a w m i d d ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 112:1

**Odak:** أَحَدٌ vakf → d_qal

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ هُوَ ٱللَّهُ أَحَدٌ

**Vasl:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d u n
```

**Vakf:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d_qal
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

#### 114:6

**Odak:** وَٱلنَّاسِ vakf → aa6 s

**Arapça:** مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ

**Vasl:**

```
m i n a l j i n n a t i w a n n aa s i
```

**Vakf:**

```
m i n a l j i n n a t i w a n n aa6 s
```

**Hafız notu:**

```text
Doğruluk: 
Hata yeri: 
Mevcut: 
Olması gereken: 
Kural: 
Not / eleştiri / öneri: 
```

---

## 7) Açık Uçlu Sorular

Cevaplarınız mimari kararları doğrudan etkileyecek:

**S1.** Bu sistemi gerçek bir hafızlık öğrencisi kullanacak olsa, en çok ne işine yarar? Hangi tecvid kuralının doğru gösterilmesi en kritik?

Cevap: ____________________________________________________________

**S2.** Tilâvet öğretmeni olarak, bir öğrencinin okuyuşundaki tecvid hatasını fonem seviyesinde tespit edebilmek için sembol setinde **şart** olarak görürdünüz ne?

Cevap: ____________________________________________________________

**S3.** Şâtıbî / Tayyibe gibi diğer turuktan birine genişletmek istesek, hangi semboller eklenmeli ya da ayrılmalı?

Cevap: ____________________________________________________________

**S4.** Eğitim platformlarında kullanılırken yanlış öğrenmeye sebep olabilecek bir kararımız var mı? (Mesela `n_g` birleşik sembolü öğrenciyi karıştırır mı?)

Cevap: ____________________________________________________________

**S5.** Şu an Vasl + Vakf iki mod sunuyoruz. Bir öğrenci vakf-ı lâzım ile vakf-ı câiz arasındaki farkı görebilmeli mi? Bunu nasıl temsil edelim?

Cevap: ____________________________________________________________

**S6.** Bilmediğimiz, gözden kaçırdığımız önemli bir konu var mı?

Cevap: ____________________________________________________________

**S7.** Bu sistem ücretsiz dağıtılacak. Müslüman dünyada kullanılması için en çok hangi dilde dökümantasyona ihtiyaç var?

Cevap: ____________________________________________________________

**S8.** Şer'î / dini hassasiyet açısından dikkat etmemiz gereken bir konu var mı? (Örn. fonem etiketlerinin terim seçimi, harf isimlerinin yazımı, vb.)

Cevap: ____________________________________________________________

---

## 8) Genel Eleştiri Bölümü (sınırsız)

Yukarıdaki herhangi bir başlığa girmeyen, ancak söylemek istediğiniz her şey için:

```text
(buraya istediğiniz kadar yazabilirsiniz — kıraat hocası olarak duygularınız,
 ümmet hizmetine yönelik öneriler, kullanım önerileri, dini hassasiyetler,
 hukukî/şer'î kaygılar dahil her şey)



```

---

## 9) Geri Dönüş

Notlarınızı şu şekillerde paylaşabilirsiniz:

1. Bu dökümanı **direkt üzerine yazıp** geri gönderin.
2. Ayet referansları üzerinden **sesli not** olarak paylaşın.
3. Yüz yüze konuşalım — buluşma ayarlayabiliriz.
4. Sadece **en kritik 3-5 hata**yı yazıp gönderin; zaman kısıtınız varsa bu bile çok kıymetli.

Görüşleriniz kaydedilecek, açık kaynak deposunda **atıf** ile teşekkür edilecektir (isminizin anılmamasını tercih ederseniz mahfuz tutarız).

Vakit ayırdığınız için Allah razı olsun. Bu sistem, kullanıldığı her yerden size sevap olarak dönsün.

— Tilavet Phonemizer ekibi
