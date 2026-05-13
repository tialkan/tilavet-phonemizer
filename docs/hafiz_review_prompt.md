# Tilavet Phonemizer V1 — Hafız İnceleme Prompt’u

Selamünaleyküm hocam,

Aşağıdaki çıktıların Kur'an-ı Kerim **Hafs an Asım** rivayetine, **tecvid** kurallarına uygunluğunu kontrol etmenizi rica ediyoruz. Bu bir yazılım çıktısıdır — ses dosyalarıyla hizalama için **altın etiket** olarak kullanılacaktır, bu yüzden doğruluk çok önemli. Sizden:

1. **Yanlış** olan yerleri işaretleyin (hangi kelime, ne olmalıydı).
2. **Tartışmalı / belirsiz** yerleri *kararsız* olarak not edin.
3. Sistemin **daha iyi olabileceği** yerleri / önerilerinizi yazın.

Kod, yazılım, sembol konusunda uzman olmanız gerekmez. Aşağıdaki **fonem sözlüğüne** bakarak çıktıyı sesli okuyup zihnen Hafs okuyuşuyla karşılaştırmanız yeterli.

---

## 1) Çalışma Modu

- **Rivâyet:** Hafs an Asım
- Her örnekte iki çıktı veriyoruz:
  - **Vasl** — kelimeler bağlı okunuyor (ayet ortasında olduğu gibi).
  - **Vakf** — ayet sonunda durulmuş varsayılıyor (tenvin düşmesi, taa-marbuta `h` ye dönmesi, medd-i arıd lis-sükûn 6 hareke vb. uygulanmış).
- Mushaf üstündeki durak işaretleri (ۚ ۛ ۖ ۗ) çıktıda `PAUSE` olarak kalır; otomatik vakf uygulanmaz (`PAUSE` = “okuyucu istese durabilir” işareti).

## 2) Fonem (Sembol) Sözlüğü

### Sessizler

| Sembol | Harf | Sembol | Harf | Sembol | Harf |
|---|---|---|---|---|---|
| `'` | hamza (ء / okunan elif) | `b` | ب | `t` | ت |
| `th` | ث | `j` | ج | `H` | ح |
| `kh` | خ | `d` | د | `dh` | ذ |
| `r` | ر | `z` | ز | `s` | س |
| `sh` | ش | `S` | ص | `D` | ض |
| `T` | ط | `Z` | ظ | `3` | ع |
| `gh` | غ | `f` | ف | `q` | ق |
| `k` | ك | `l` | ل (tarqîq lâm) | `L` | **lafzatullah** tafhîm lâm |
| `m` | م | `n` | ن | `h` | ه |
| `w` | و (konsonant) | `y` | ي (konsonant) | | |

### Sesliler ve Medd

| Sembol | Anlam |
|---|---|
| `a` `i` `u` | Kısa harekeler (fatha · kesra · damme) |
| `aa` `ii` `uu` | **Medd-i tabii** (2 hareke) |
| `aa4` `ii4` `uu4` | **4 hareke** medd (muttasıl / munfasıl / sıla-i kübra) |
| `aa6` `ii6` `uu6` | **6 hareke** medd (lazım / arıd lis-sükûn) |

### Tecvid Varyantları

| Sembol | Anlam |
|---|---|
| `n_g` | Nun/tenvin **ihfâ** veya **idgâm ma‘al ğunne** (ortak sembol) |
| `m_g` | Mim **idgam-ı şefevî** veya **iklâb** |
| `q_qal` `T_qal` `b_qal` `j_qal` `d_qal` | **Kalkale** (ق ط ب ج د sakin) |
| `PAUSE` | Mushaftaki durak işareti |

### Önemli Sözleşme Notları

- `L` **yalnızca** lafzatullah lâmı tafhîm okunduğunda kullanılır. Kesra sonrası lafzatullah tarqîq olur ve `l` kalır (örn. `بِسْمِ ٱللَّهِ`, `لِلَّهِ`).
- Tenvin + lâm/râ idgâm-ı bilâ ğunne durumunda `n` sembolü düşer (örn. `هُدًى لِّلْمُتَّقِينَ` → `... a l l ...`).
- Küçük (hançer) elif tek uzun sesli olarak yazılır: `m aa` (`m a aa` değil).
- Hamze-i kat‘ her zaman okunur, vasl bahanesiyle düşürülmez.
- `كُفُوًا` rasimde vâv ile temsil edilir: `k u f u w a n` (hamza beklenmiyor).
- Ayetler **ayet-yerel** inceleniyor; bir önceki/sonraki ayete bağlanma gerektiren durumları “cross-ayah” notuyla belirtin.

## 3) İnceleme Şablonu

Her ayet için aşağıdaki bloğu doldurun:

```text
Ayet: X:Y
Doğruluk: doğru / hatalı / kararsız
Yer:               (hata varsa hangi kelime / nereden başladığı)
Mevcut:            (yanlış olan fonem dizisi)
Olması gereken:    (doğru fonem dizisi veya sözel anlatım)
Kural:             (örn. ihfâ, idgâm bil-ğunne, medd-i muttasıl)
Not:               (ek açıklama, öneri, kararsızlık sebebi)
```

Vasl ve Vakf farklıysa, ayrı ayrı doldurabilirsiniz. “Doğruluk: doğru” yazmanız yeterli ise diğer alanları boş bırakın.

---

## 4) İncelenecek Ayetler (23 parça)

### 1:1

**Odak:** Besmele · lafzatullah tarqiq (kasra sonrası) · lam shamsiyya (الرحمن)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 1:7

**Odak:** İzhar (نْعَ) · medd-i lazım (ٱلضَّآلِّينَ) · iltikā-ı sakineyn (وَلَا ٱل)

**Arapça:** صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ

**Vasl çıktısı:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 2:1

**Odak:** Hurûf-ı mukatta‘a (الم) · medd-i lazım · idgam şefevî seam

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ الٓمٓ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 2:2

**Odak:** Tenvin + lâm idgam-ı bilâ ğunne (هُدًى لِّلْمُتَّقِينَ) · PAUSE markeri

**Arapça:** ذَٰلِكَ ٱلْكِتَٰبُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًۭى لِّلْمُتَّقِينَ

**Vasl çıktısı:**

```
dh aa l i k a l k i t aa b u l aa r a y b a PAUSE f ii h i PAUSE h u d a l l i l m u t t a q ii n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
dh aa l i k a l k i t aa b u l aa r a y b PAUSE f ii6 h PAUSE h u d a l l i l m u t t a q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 2:30

**Odak:** Medd-i muttasıl (مَلَٰٓئِكَةِ) · taa-marbuta wasl/vakf · ihfa

**Arapça:** وَإِذْ قَالَ رَبُّكَ لِلْمَلَٰٓئِكَةِ إِنِّى جَاعِلٌۭ فِى ٱلْأَرْضِ خَلِيفَةًۭ ۖ قَالُوٓا۟ أَتَجْعَلُ فِيهَا مَن يُفْسِدُ فِيهَا وَيَسْفِكُ ٱلدِّمَآءَ وَنَحْنُ نُسَبِّحُ بِحَمْدِكَ وَنُقَدِّسُ لَكَ ۖ قَالَ إِنِّىٓ أَعْلَمُ مَا لَا تَعْلَمُونَ

**Vasl çıktısı:**

```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a t a n PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k a PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a h PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 2:156

**Odak:** İdgam şefevî (هُم مُّ) · medd-i munfasıl cross-word (وَإِنَّآ إِلَيْهِ)

**Arapça:** ٱلَّذِينَ إِذَآ أَصَٰبَتْهُم مُّصِيبَةٌۭ قَالُوٓا۟ إِنَّا لِلَّهِ وَإِنَّآ إِلَيْهِ رَٰجِعُونَ

**Vasl çıktısı:**

```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 2:255

**Odak:** Ayet el-Kürsî başı · lafzatullah tafhîm (L) · medd-i sıla

**Arapça:** ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ ۚ لَا تَأْخُذُهُۥ سِنَةٌۭ وَلَا نَوْمٌۭ ۚ لَّهُۥ مَا فِى ٱلسَّمَٰوَٰتِ وَمَا فِى ٱلْأَرْضِ ۗ مَن ذَا ٱلَّذِى يَشْفَعُ عِندَهُۥٓ إِلَّا بِإِذْنِهِۦ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَىْءٍۢ مِّنْ عِلْمِهِۦٓ إِلَّا بِمَا شَآءَ ۚ وَسِعَ كُرْسِيُّهُ ٱلسَّمَٰوَٰتِ وَٱلْأَرْضَ ۖ وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ

**Vasl çıktısı:**

```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu m u PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m u n PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D i PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' a PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D a PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii m u
```

**Vakf (ayet sonu durunca) çıktısı:**

```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu6 m PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii6 PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa6 PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii6 m
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 6:143

**Odak:** Soru hemzesi + Allah-benzeri form (ءَآلذَّكَرَيْنِ) — bilinen edge case

**Arapça:** ثَمَٰنِيَةَ أَزْوَٰجٍۢ ۖ مِّنَ ٱلضَّأْنِ ٱثْنَيْنِ وَمِنَ ٱلْمَعْزِ ٱثْنَيْنِ ۗ قُلْ ءَآلذَّكَرَيْنِ حَرَّمَ أَمِ ٱلْأُنثَيَيْنِ أَمَّا ٱشْتَمَلَتْ عَلَيْهِ أَرْحَامُ ٱلْأُنثَيَيْنِ ۖ نَبِّـُٔونِى بِعِلْمٍ إِن كُنتُمْ صَٰدِقِينَ

**Vasl çıktısı:**

```
th a m aa n i y a t a ' a z w aa j i n PAUSE m m i n a D D a ' n i th n a y n i w a m i n a l m a 3 z i th n a y n i PAUSE q u l ' aa4 l dh dh a k a r a y n i H a r r a m a ' a m i l ' u n_g th a y a y n i ' a m m a sh t a m a l a t 3 a l a y h i ' a r H aa m u l ' u n_g th a y a y n i PAUSE n a b b i ' uu n ii b i 3 i l m i n ' i n_g k u n_g t u m S aa d i q ii n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
th a m aa n i y a t a ' a z w aa6 j PAUSE m m i n a D D a ' n i th n a y n i w a m i n a l m a 3 z i th n a y n PAUSE q u l ' aa4 l dh dh a k a r a y n i H a r r a m a ' a m i l ' u n_g th a y a y n i ' a m m a sh t a m a l a t 3 a l a y h i ' a r H aa m u l ' u n_g th a y a y n PAUSE n a b b i ' uu n ii b i 3 i l m i n ' i n_g k u n_g t u m S aa d i q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 9:65

**Odak:** Çift prefix + alif-wasla (أَبِٱللَّهِ)

**Arapça:** وَلَئِن سَأَلْتَهُمْ لَيَقُولُنَّ إِنَّمَا كُنَّا نَخُوضُ وَنَلْعَبُ ۚ قُلْ أَبِٱللَّهِ وَءَايَٰتِهِۦ وَرَسُولِهِۦ كُنتُمْ تَسْتَهْزِءُونَ

**Vasl çıktısı:**

```
w a l a ' i n_g s a ' a l t a h u m l a y a q uu l u n n a ' i n n a m aa k u n n aa n a kh uu D u w a n a l 3 a b u PAUSE q u l ' a b i l l a h i w a ' aa y aa t i h ii w a r a s uu l i h ii k u n_g t u m t a s t a h z i ' uu n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
w a l a ' i n_g s a ' a l t a h u m l a y a q uu l u n n a ' i n n a m aa k u n n aa n a kh uu D u w a n a l 3 a b PAUSE q u l ' a b i l l a h i w a ' aa y aa t i h ii w a r a s uu l i h ii k u n_g t u m t a s t a h z i ' uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 12:73

**Odak:** Yemin tâ + alif-wasla (تَٱللَّهِ)

**Arapça:** قَالُوا۟ تَٱللَّهِ لَقَدْ عَلِمْتُم مَّا جِئْنَا لِنُفْسِدَ فِى ٱلْأَرْضِ وَمَا كُنَّا سَٰرِقِينَ

**Vasl çıktısı:**

```
q aa l uu t a l l a h i l a q a d_qal 3 a l i m t u m_g m aa j i ' n aa l i n u f s i d a f i l ' a r D i w a m aa k u n n aa s aa r i q ii n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
q aa l uu t a l l a h i l a q a d_qal 3 a l i m t u m_g m aa j i ' n aa l i n u f s i d a f i l ' a r D i w a m aa k u n n aa s aa r i q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 16:16

**Odak:** Multi-prefix + lam shamsiyya (وَبِٱلنَّجْمِ)

**Arapça:** وَعَلَٰمَٰتٍۢ ۚ وَبِٱلنَّجْمِ هُمْ يَهْتَدُونَ

**Vasl çıktısı:**

```
w a 3 a l aa m aa t i n PAUSE w a b i n n a j_qal m i h u m y a h t a d uu n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
w a 3 a l aa m aa6 t PAUSE w a b i n n a j_qal m i h u m y a h t a d uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 24:47

**Odak:** Multi-prefix + lam shamsiyya râ (وَبِٱلرَّسُولِ)

**Arapça:** وَيَقُولُونَ ءَامَنَّا بِٱللَّهِ وَبِٱلرَّسُولِ وَأَطَعْنَا ثُمَّ يَتَوَلَّىٰ فَرِيقٌۭ مِّنْهُم مِّنۢ بَعْدِ ذَٰلِكَ ۚ وَمَآ أُو۟لَٰٓئِكَ بِٱلْمُؤْمِنِينَ

**Vasl çıktısı:**

```
w a y a q uu l uu n a ' aa m a n n aa b i l l a h i w a b i r r a s uu l i w a ' a T a 3 n aa th u m m a y a t a w a l l aa f a r ii q u m_g m i m_g h u m_g m i m_g b a 3 d i dh aa l i k a PAUSE w a m aa4 ' uu l aa4 ' i k a b i l m u ' m i n ii n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
w a y a q uu l uu n a ' aa m a n n aa b i l l a h i w a b i r r a s uu l i w a ' a T a 3 n aa th u m m a y a t a w a l l aa f a r ii q u m_g m i m_g h u m_g m i m_g b a 3 d i dh aa l i k PAUSE w a m aa4 ' uu l aa4 ' i k a b i l m u ' m i n ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 19:1

**Odak:** 5-letter hurûf-ı mukatta‘a (كهيعص) seam ihfa

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ كٓهيعٓصٓ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i k aa6 f h aa y aa 3 aa6 y n_g S aa6 d
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i k aa6 f h aa y aa 3 aa6 y n_g S aa6 d
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 42:2

**Odak:** Tek başına mukatta‘a (عسق) — eskiden hatalıydı

**Arapça:** عٓسٓقٓ

**Vasl çıktısı:**

```
3 aa6 y n_g s ii6 n_g q aa6 f
```

**Vakf (ayet sonu durunca) çıktısı:**

```
3 aa6 y n_g s ii6 n_g q aa6 f
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 53:1

**Odak:** Tek prefix + lam shamsiyya (وَٱلنَّجْمِ)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ وَٱلنَّجْمِ إِذَا هَوَىٰ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i w a n n a j_qal m i ' i dh aa h a w aa
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i w a n n a j_qal m i ' i dh aa h a w aa
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 108:1

**Odak:** Medd-i munfasıl cross-word · küçük elif (نَٰكَ)

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ إِنَّآ أَعْطَيْنَٰكَ ٱلْكَوْثَرَ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' i n n aa4 ' a 3 T a y n aa k a l k a w th a r a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' i n n aa4 ' a 3 T a y n aa k a l k a w th a r
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 112:1

**Odak:** Lafzatullah tafhîm (fatha öncesi) · sonda tenvin

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ هُوَ ٱللَّهُ أَحَدٌ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d u n
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 112:4

**Odak:** İdgam-ı bilâ ğunne (يَكُن لَّ) · hâ-i sıla · vâv ile kufuwan

**Arapça:** وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ

**Vasl çıktısı:**

```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d u n
```

**Vakf (ayet sonu durunca) çıktısı:**

```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 113:1

**Odak:** Hamze-i kat‘ (أَعُوذُ) · şedde · lam qamariyya

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i l f a l a q i
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i l f a l a q
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 78:1

**Odak:** Kısa ayet — soru hemzesi

**Arapça:** بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ عَمَّ يَتَسَآءَلُونَ

**Vasl çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i 3 a m m a y a t a s aa4 ' a l uu n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i 3 a m m a y a t a s aa4 ' a l uu6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 2:233

**Odak:** İdgam-ı mütecânis (د+ت → ت ت) örneği

**Arapça:** ۞ وَٱلْوَٰلِدَٰتُ يُرْضِعْنَ أَوْلَٰدَهُنَّ حَوْلَيْنِ كَامِلَيْنِ ۖ لِمَنْ أَرَادَ أَن يُتِمَّ ٱلرَّضَاعَةَ ۚ وَعَلَى ٱلْمَوْلُودِ لَهُۥ رِزْقُهُنَّ وَكِسْوَتُهُنَّ بِٱلْمَعْرُوفِ ۚ لَا تُكَلَّفُ نَفْسٌ إِلَّا وُسْعَهَا ۚ لَا تُضَآرَّ وَٰلِدَةٌۢ بِوَلَدِهَا وَلَا مَوْلُودٌۭ لَّهُۥ بِوَلَدِهِۦ ۚ وَعَلَى ٱلْوَارِثِ مِثْلُ ذَٰلِكَ ۗ فَإِنْ أَرَادَا فِصَالًا عَن تَرَاضٍۢ مِّنْهُمَا وَتَشَاوُرٍۢ فَلَا جُنَاحَ عَلَيْهِمَا ۗ وَإِنْ أَرَدتُّمْ أَن تَسْتَرْضِعُوٓا۟ أَوْلَٰدَكُمْ فَلَا جُنَاحَ عَلَيْكُمْ إِذَا سَلَّمْتُم مَّآ ءَاتَيْتُم بِٱلْمَعْرُوفِ ۗ وَٱتَّقُوا۟ ٱللَّهَ وَٱعْلَمُوٓا۟ أَنَّ ٱللَّهَ بِمَا تَعْمَلُونَ بَصِيرٌۭ

**Vasl çıktısı:**

```
PAUSE w a l w aa l i d aa t u y u r D i 3 n a ' a w l aa d a h u n n a H a w l a y n i k aa m i l a y n i PAUSE l i m a n ' a r aa d a ' a n_g y u t i m m a r r a D aa 3 a t a PAUSE w a 3 a l a l m a w l uu d i l a h uu r i z q u h u n n a w a k i s w a t u h u n n a b i l m a 3 r uu f i PAUSE l aa t u k a l l a f u n a f s u n ' i l l aa w u s 3 a h aa PAUSE l aa t u D aa6 r r a w aa l i d a t u m_g b i w a l a d i h aa w a l aa m a w l uu d u l l a h uu b i w a l a d i h ii PAUSE w a 3 a l a l w aa r i th i m i th l u dh aa l i k a PAUSE f a ' i n ' a r aa d aa f i S aa l a n 3 a n_g t a r aa D i m_g m i n_g h u m aa w a t a sh aa w u r i n_g f a l aa j u n aa H a 3 a l a y h i m aa PAUSE w a ' i n ' a r a t t u m ' a n_g t a s t a r D i 3 uu4 ' a w l aa d a k u m f a l aa j u n aa H a 3 a l a y k u m ' i dh aa s a l l a m t u m_g m aa4 ' aa t a y t u m b i l m a 3 r uu f i PAUSE w a t t a q u L L aa h a w a 3 l a m uu4 ' a n n a L L aa h a b i m aa t a 3 m a l uu n a b a S ii r u n
```

**Vakf (ayet sonu durunca) çıktısı:**

```
PAUSE w a l w aa l i d aa t u y u r D i 3 n a ' a w l aa d a h u n n a H a w l a y n i k aa m i l a y n PAUSE l i m a n ' a r aa d a ' a n_g y u t i m m a r r a D aa 3 a h PAUSE w a 3 a l a l m a w l uu d i l a h uu r i z q u h u n n a w a k i s w a t u h u n n a b i l m a 3 r uu6 f PAUSE l aa t u k a l l a f u n a f s u n ' i l l aa w u s 3 a h aa6 PAUSE l aa t u D aa6 r r a w aa l i d a t u m_g b i w a l a d i h aa w a l aa m a w l uu d u l l a h uu b i w a l a d i h ii6 PAUSE w a 3 a l a l w aa r i th i m i th l u dh aa l i k PAUSE f a ' i n ' a r aa d aa f i S aa l a n 3 a n_g t a r aa D i m_g m i n_g h u m aa w a t a sh aa w u r i n_g f a l aa j u n aa H a 3 a l a y h i m aa6 PAUSE w a ' i n ' a r a t t u m ' a n_g t a s t a r D i 3 uu4 ' a w l aa d a k u m f a l aa j u n aa H a 3 a l a y k u m ' i dh aa s a l l a m t u m_g m aa4 ' aa t a y t u m b i l m a 3 r uu6 f PAUSE w a t t a q u L L aa h a w a 3 l a m uu4 ' a n n a L L aa h a b i m aa t a 3 m a l uu n a b a S ii6 r
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 77:20

**Odak:** İdgam-ı mütekārib (ق+ك)

**Arapça:** أَلَمْ نَخْلُقكُّم مِّن مَّآءٍۢ مَّهِينٍۢ

**Vasl çıktısı:**

```
' a l a m n a kh l u k k u m_g m i m_g m aa4 ' i m_g m a h ii n i n
```

**Vakf (ayet sonu durunca) çıktısı:**

```
' a l a m n a kh l u k k u m_g m i m_g m aa4 ' i m_g m a h ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

### 9:44

**Odak:** Tatweel-hemze ortografisi (يَسْتَـْٔذِنُكَ)

**Arapça:** لَا يَسْتَـْٔذِنُكَ ٱلَّذِينَ يُؤْمِنُونَ بِٱللَّهِ وَٱلْيَوْمِ ٱلْءَاخِرِ أَن يُجَٰهِدُوا۟ بِأَمْوَٰلِهِمْ وَأَنفُسِهِمْ ۗ وَٱللَّهُ عَلِيمٌۢ بِٱلْمُتَّقِينَ

**Vasl çıktısı:**

```
l aa y a s t a ' dh i n u k a l l a dh ii n a y u ' m i n uu n a b i l l a h i w a l y a w m i l ' aa kh i r i ' a n_g y u j aa h i d uu b i ' a m w aa l i h i m w a ' a n_g f u s i h i m PAUSE w a l l a h u 3 a l ii m u m_g b i l m u t t a q ii n a
```

**Vakf (ayet sonu durunca) çıktısı:**

```
l aa y a s t a ' dh i n u k a l l a dh ii n a y u ' m i n uu n a b i l l a h i w a l y a w m i l ' aa kh i r i ' a n_g y u j aa h i d uu b i ' a m w aa l i h i m w a ' a n_g f u s i h i m PAUSE w a l l a h u 3 a l ii m u m_g b i l m u t t a q ii6 n
```

**Hafız notu:**

```text
Doğruluk: 
Yer: 
Mevcut: 
Olması gereken: 
Kural: 
Not: 
```

---

## 5) Genel Geri Bildirim Soruları

Aşağıdaki sorulara da kısa cevaplarınızı rica ediyoruz (zorunlu değil):

1. **Sözleşme yeterli mi?** Sembol sözlüğünde eksik kalan bir tecvid ayrımı (ör. ğunne süresi, kalkale şiddet farkı, idgam-ı nâkıs/kâmil, mertebeler) gördünüz mü?
2. **Medd uzunlukları**: 2/4/6 hareke kategorileri yeterli mi? **Lîn meddi** (ـَوْ ـَيْ), **medd-i ʿivaz**, **medd-i ferʿî** ayrı sembolle gösterilmeli mi?
3. **Râ harfi tafhîm/tarqîq**: Şu an sadece lafzatullah lâmı için `L`/`l` ayrımı var. Râ (ر/R) için de benzer ayrım gerekir mi? (Hafs’ta bazı kelimelerde mertebe tartışmalı.)
4. **Vakf modunda medd-i arıd lis-sükûn**: Şu an her vakf sonunu 6 hareke (`ii6` vb.) işaretliyoruz. Sizce 2/4/6 seçeneği için ayrı semboller (örn. `ii2 ii4 ii6`) gerekir mi, yoksa kıraat kararı olduğundan tek sembol yeterli mi?
5. **Hurûf-ı mukatta‘a** (الم, كهيعص, عسق vb.): Harf isimleri arasındaki idgâm/ihfâ uygulamasını doğru buldunuz mu?
6. **Eksik kalan kelime / formlar**: Kuran’da geçip bu sembol setinin temsil edemediği bir kelime/form var mı? (Özellikle nadir orta-kelime alif-madda, küçük harekeler ʾU+06EA / U+06DFˮ vs.)
7. **Genel öneri**: Sistem ses tanıma (otomatik tilâvet takibi, kelime-kelime highlight) için kullanılacak. Doğru hizalama açısından öncelik vermemiz gereken bir nokta var mı?

---

## 6) Geri Dönüş

Notlarınızı doğrudan yukarıdaki bloklara yazıp dosyayı geri verebilirsiniz; veya örnek başına kısa sesli mesaj/notla da paylaşabilirsiniz. Vakit ayırdığınız için çok teşekkür ederiz; her uyarı sistemin doğruluğuna doğrudan yansıyacak.

Allah razı olsun.
