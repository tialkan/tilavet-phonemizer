# Tilavet Phonemizer V1 - LLM Hafiz Review Prompt

Sen Kur'an-i Kerim tilaveti, Hafs an Asim rivayeti, tecvid kurallari,
waqf/wasl, madd, nun sakin/tanwin, mim sakin, lam shamsiyya/qamariyya,
lafzatullah, qalqalah ve huroof muqatta'at konularinda uzman bir hafizsin.

Bu gorevde senden fetva vermeni veya dini hukum uretmeni istemiyoruz.
Sadece verilen Arapca ayet metni ile sembolik phonemizer ciktisini,
Hafs / Asim tilavet kurallari acisindan teknik olarak karsilastirmani
istiyoruz.

## Proje Baglami

Tilavet uygulamasi, Kur'an tilavetini offline/iOS ortaminda takip etmek icin
gelistiriliyor. Hedef, sesi serbest metne cevirmek degil:

```text
Quran text -> phoneme sequence
Audio -> phoneme posterior
Decoder -> Quran phoneme map alignment
```

Bu yuzden phonemizer ciktisi cok onemli. Model egitimi ve kelime highlight
icin altin etiket olacak.

## Okuma Modu

Lutfen asagidaki varsayimlarla incele:

- Qira'at/rivayet: Hafs an Asim
- Mod: wasl candidate
- Yani kelimeler mumkun oldugunca baglanarak okunuyor
- Ayet sonu waqf ayrica belirtilmedikce varsayilmasin
- Mushaf durak isaretleri `PAUSE` olarak gosterilebilir
- Besmele metinde varsa incelemeye dahildir

Bir yerde waqf ile wasl sonucu farkliysa bunu ozellikle belirt.

## Onemli Sembol Sozlesmesi Notlari

- `L` sadece lafzatullah lam'i tafkhim oldugunda kullanilir. Onceki hareke
  kasra ise lafzatullah lam'i muraqqaq/tarqiq olur ve `l` olarak kalmasi
  beklenir. Bu yuzden `بِسْمِ ٱللَّهِ` ve `لِلَّهِ` icin `l l aa h` hata
  sayilmasin.
- `PAUSE` bu batch'te mushaf durak isaretinin korundugunu gosterir. Her
  `PAUSE` otomatik tam waqf uygulanmis demek degildir. Waqf uygulanmasi
  gerektigini dusunuyorsan `Accuracy: unsure` ile not dus.
- Ayetler ayet-yerel inceleniyor. Bir onceki ayetin sonundan sonraki ayete
  wasl/nun-qutni ile gecis gerekiyorsa bunu ana ayet hatasi sayma; `unsure`
  olarak "cross-ayah variant" diye not dus.
- `n_g`, hem ikhfa hem ghunnali idgham icin ortak semboldur. `يُنفِقُونَ`,
  `مِن شَرِّ`, `مَن ذَا`, `عِندَهُۥ` gibi nun-sakin/tanwin baglamlarini
  bu sozlesmeye gore degerlendir.
- Tanwin + lam/ra idgham bila ghunna oldugunda `n` sembolunun bos/elided
  hale gelmesi normaldir. `هُدًى لِّلْمُتَّقِينَ` icin `h u d a l l...`
  hatali sayilmasin.
- Small alif/dagger alif artik tek uzun vokal olarak beklenir:
  `m a aa` eski/stale bir hatadir; guncel candidate'te `m aa` olmalidir.
- Hamzat qat' her zaman okunur. `أَتَجْعَلُ` gibi kelimelerde wasl bahanesiyle
  hamza dusurulmemelidir.
- `أَحَدٌ`, `ٱلْأَرْضِ` gibi kok hamzasi bulunan kelimelerde hamza qat'
  korunur; bu hamzayi hamzat-wasl gibi dusurme.
- `كُفُوًا` bu batch'teki rasmda waw ile temsil edilir; `k u f u w a n`
  beklenen V1 fonem akistir, hamza bekleme.
- `ٱلْعَٰلَمِينَ` sonundaki nun V1 wasl akista `n a` olarak kalir.

## Fonem Sembolleri

### Konsonantlar

| Symbol | Arabic |
|---|---|
| `'` | hamza / okunan alif carrier |
| `b` | ب |
| `t` | ت |
| `th` | ث |
| `j` | ج |
| `H` | ح |
| `kh` | خ |
| `d` | د |
| `dh` | ذ |
| `r` | ر |
| `z` | ز |
| `s` | س |
| `sh` | ش |
| `S` | ص |
| `D` | ض |
| `T` | ط |
| `Z` | ظ |
| `3` | ع |
| `gh` | غ |
| `f` | ف |
| `q` | ق |
| `k` | ك |
| `l` | ل |
| `L` | lafzatullah tafkhim lam |
| `m` | م |
| `n` | ن |
| `h` | ه |
| `w` | و consonant |
| `y` | ي consonant |

### Vokaller ve Madd

- `a`, `i`, `u`: kisa harekeler
- `aa`, `ii`, `uu`: madd tabii
- `aa4`, `ii4`, `uu4`: 4 hareke madd adayi
- `aa6`, `ii6`, `uu6`: 6 hareke madd adayi

### Tecvid Varyantlari

- `n_g`: nun/tanwin ghunna, ihfa veya ghunnali idgham
- `m_g`: iqlab veya mim ghunna
- `q_qal`, `T_qal`, `b_qal`, `j_qal`, `d_qal`: qalqalah
- `PAUSE`: durak isareti
- `BREATH`: ayet sonu/uzun nefes, bu batch'te zorunlu degil

## Inceleme Kurallari

Her ayet icin:

1. Arapca metni Hafs / Asim wasl okuma ile zihninde oku.
2. Candidate output ile karsilastir.
3. Hata yoksa sadece `Accuracy: yes` yaz.
4. Hata varsa sadece hatali bolumu yaz; tum ayeti bastan yazmana gerek yok.
5. Emin degilsen `Accuracy: unsure` yaz ve nedenini belirt.

Ozellikle su hata turlerini ara:

- Alif wasla yanlis okunmus veya gereksiz okunmus mu?
- Lam shamsiyya/qamariyya dogru mu?
- Lafzatullah `l` / `L` dogru mu?
- Shadda dogru iki konsonant gibi temsil edilmis mi?
- Madd tabii / muttasil / munfasil / lazim dogru mu?
- Taa marbuta wasl halinde `t`, waqf halinde `h` olacak sekilde ele alinmis mi?
- Nun sakin/tanwin: izhar, ikhfa, idgham, iqlab dogru mu?
- Qalqalah sadece uygun sakin harflerde mi var?
- Huroof muqatta'at dogru harf isimleri ve maddleriyle temsil edilmeli mi?
- Waqf/wasl farki varsa not dusulmus mu?

## Cevap Formati

Lutfen cevabini kesinlikle bu formatta ver:

```text
Ayah: 1:1
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

Birden fazla hata varsa ayni ayet icin birden fazla blok yaz:

```text
Ayah: 1:5
Accuracy: no
Location: إِيَّاكَ
Current: ' ii k a
Expected: ' i y y aa k a
Rule: shadda + madd tabii
Note: Ya shadda ile okunur; yalnizca ii seklinde yutulmamali.
```

Hata yoksa kisa yaz:

```text
Ayah: 1:1
Accuracy: yes
Location:
Current:
Expected:
Rule:
Note:
```

## Incelenecek Batch

Asagidaki ayetlerde `Candidate output` alanini kontrol et.

## Ayat

### 1:1 - Fatiha 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 1:2 - Fatiha 2

**Arabic:**
> ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ

**Candidate output:**
```
' a l H a m d u l i l l aa h i r a b b i l 3 aa l a m ii n a
```

**Stored candidate:**
```
' a l H a m d u l i l l aa h i r a b b i l 3 aa l a m ii n a
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `a` -> alif_wasla_initial_vowel
- `l` -> lam_qamariyya
- `H` -> letter
- `a` -> vowel
- `m` -> mim_sakin
- `d` -> letter
- `u` -> vowel
- `l` -> li_prefix
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> letter
- `a` -> vowel
- `b` -> shadda
- `b` -> shadda
- `i` -> vowel
- `l` -> lam_qamariyya
- `3` -> letter
- `aa` -> small_alef_madd_tabii
- `l` -> letter
- `a` -> vowel
- `m` -> letter
- `ii` -> madd_tabii
- `n` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 1:3 - Fatiha 3

**Arabic:**
> ٱلرَّحْمَٰنِ ٱلرَّحِيمِ

**Candidate output:**
```
' a r r a H m aa n i r r a H ii m i
```

**Stored candidate:**
```
' a r r a H m aa n i r r a H ii m i
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `a` -> alif_wasla_initial_vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 1:4 - Fatiha 4

**Arabic:**
> مَٰلِكِ يَوْمِ ٱلدِّينِ

**Candidate output:**
```
m aa l i k i y a w m i d d ii n i
```

**Stored candidate:**
```
m aa l i k i y a w m i d d ii n i
```

**Rule hits:**
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `l` -> letter
- `i` -> vowel
- `k` -> letter
- `i` -> vowel
- `y` -> letter
- `a` -> vowel
- `w` -> letter
- `m` -> letter
- `i` -> vowel
- `d` -> shadda
- `d` -> shadda
- `ii` -> madd_tabii
- `n` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 1:5 - Fatiha 5

**Arabic:**
> إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ

**Candidate output:**
```
' i y y aa k a n a 3 b u d u w a ' i y y aa k a n a s t a 3 ii n u
```

**Stored candidate:**
```
' i y y aa k a n a 3 b u d u w a ' i y y aa k a n a s t a 3 ii n u
```

**Rule hits:**
- `'` -> letter
- `i` -> vowel
- `y` -> shadda
- `y` -> shadda
- `aa` -> madd_tabii
- `k` -> letter
- `a` -> vowel
- `n` -> letter
- `a` -> vowel
- `3` -> letter
- `b` -> letter
- `u` -> vowel
- `d` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `'` -> letter
- `i` -> vowel
- `y` -> shadda
- `y` -> shadda
- `aa` -> madd_tabii
- `k` -> letter
- `a` -> vowel
- `n` -> letter
- `a` -> vowel
- `s` -> letter
- `t` -> letter
- `a` -> vowel
- `3` -> letter
- `ii` -> madd_tabii
- `n` -> letter
- `u` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 1:6 - Fatiha 6

**Arabic:**
> ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ

**Candidate output:**
```
' i h d i n a S S i r aa T a l m u s t a q ii m a
```

**Stored candidate:**
```
' i h d i n a S S i r aa T a l m u s t a q ii m a
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `i` -> alif_wasla_initial_vowel
- `h` -> letter
- `d` -> letter
- `i` -> vowel
- `n` -> letter
- `aa` -> madd_tabii
- `a` -> iltiqa_sakinayn_madd_drop
- `S` -> shadda
- `S` -> shadda
- `i` -> vowel
- `r` -> letter
- `aa` -> small_alef_madd_tabii
- `T` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `m` -> letter
- `u` -> vowel
- `s` -> letter
- `t` -> letter
- `a` -> vowel
- `q` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 1:7 - Fatiha 7

**Arabic:**
> صِرَٰطَ ٱلَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ ٱلْمَغْضُوبِ عَلَيْهِمْ وَلَا ٱلضَّآلِّينَ

**Candidate output:**
```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii n a
```

**Stored candidate:**
```
S i r aa T a l l a dh ii n a ' a n 3 a m t a 3 a l a y h i m gh a y r i l m a gh D uu b i 3 a l a y h i m w a l a D D aa6 l l ii n a
```

**Rule hits:**
- `S` -> letter
- `i` -> vowel
- `r` -> letter
- `aa` -> small_alef_madd_tabii
- `T` -> letter
- `a` -> vowel
- `l` -> article_lam_shadda
- `l` -> article_lam_shadda
- `a` -> vowel
- `dh` -> letter
- `ii` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `'` -> letter
- `a` -> vowel
- `n` -> noon_sakin
- `3` -> letter
- `a` -> vowel
- `m` -> mim_sakin
- `t` -> letter
- `a` -> vowel
- `n` -> izhar
- `n` -> izhar
- `3` -> letter
- `a` -> vowel
- `l` -> letter
- `a` -> vowel
- `y` -> letter
- `h` -> letter
- `i` -> vowel
- `m` -> mim_sakin
- `gh` -> letter
- `a` -> vowel
- `y` -> letter
- `r` -> letter
- `i` -> vowel
- `l` -> lam_qamariyya
- `m` -> letter
- `a` -> vowel
- `gh` -> letter
- `D` -> letter
- `uu` -> madd_tabii
- `b` -> letter
- `i` -> vowel
- `3` -> letter
- `a` -> vowel
- `l` -> letter
- `a` -> vowel
- `y` -> letter
- `h` -> letter
- `i` -> vowel
- `m` -> mim_sakin
- `w` -> letter
- `a` -> vowel
- `l` -> letter
- `aa` -> madd_tabii
- `a` -> iltiqa_sakinayn_madd_drop
- `D` -> shadda
- `D` -> shadda
- `aa6` -> madd_lazim
- `l` -> shadda
- `l` -> shadda
- `ii` -> madd_tabii
- `n` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 2:1 - Bakara 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ الٓمٓ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' a l i f l aa6 m_g m ii6 m
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `'` -> huroof_muqattaat
- `a` -> huroof_muqattaat
- `l` -> huroof_muqattaat
- `i` -> huroof_muqattaat
- `f` -> huroof_muqattaat
- `l` -> huroof_muqattaat
- `aa6` -> huroof_muqattaat
- `m_g` -> huroof_muqattaat
- `m` -> huroof_muqattaat
- `ii6` -> huroof_muqattaat
- `m` -> huroof_muqattaat

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 2:2 - Bakara 2

**Arabic:**
> ذَٰلِكَ ٱلْكِتَٰبُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًۭى لِّلْمُتَّقِينَ

**Candidate output:**
```
dh aa l i k a l k i t aa b u l aa r a y b a PAUSE f ii h i PAUSE h u d a l l i l m u t t a q ii n a
```

**Stored candidate:**
```
dh aa l i k a l k i t aa b u l aa r a y b a PAUSE f ii h i PAUSE h u d a l l i l m u t t a q ii n a
```

**Rule hits:**
- `dh` -> letter
- `aa` -> small_alef_madd_tabii
- `l` -> letter
- `i` -> vowel
- `k` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `k` -> letter
- `i` -> vowel
- `t` -> letter
- `aa` -> small_alef_madd_tabii
- `b` -> letter
- `u` -> vowel
- `l` -> letter
- `aa` -> madd_tabii
- `r` -> letter
- `a` -> vowel
- `y` -> letter
- `b` -> letter
- `a` -> vowel
- `PAUSE` -> pause_mark
- `f` -> letter
- `ii` -> madd_tabii
- `h` -> letter
- `i` -> vowel
- `PAUSE` -> pause_mark
- `h` -> letter
- `u` -> vowel
- `d` -> letter
- `a` -> tanwin
- `n` -> tanwin_n
- `l` -> shadda
- `l` -> shadda
- `i` -> vowel
- `l` -> letter
- `m` -> letter
- `u` -> vowel
- `t` -> shadda
- `t` -> shadda
- `a` -> vowel
- `q` -> letter
- `ii` -> madd_tabii
- `n` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 2:3 - Bakara 3

**Arabic:**
> ٱلَّذِينَ يُؤْمِنُونَ بِٱلْغَيْبِ وَيُقِيمُونَ ٱلصَّلَوٰةَ وَمِمَّا رَزَقْنَٰهُمْ يُنفِقُونَ

**Candidate output:**
```
' a l l a dh ii n a y u ' m i n uu n a b i l gh a y b i w a y u q ii m uu n a S S a l aa t a w a m i m m aa r a z a q_qal n aa h u m y u n_g f i q uu n a
```

**Stored candidate:**
```
' a l l a dh ii n a y u ' m i n uu n a b i l gh a y b i w a y u q ii m uu n a S S a l aa t a w a m i m m aa r a z a q_qal n aa h u m y u n_g f i q uu n a
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `a` -> alif_wasla_initial_vowel
- `l` -> article_lam_shadda
- `l` -> article_lam_shadda
- `a` -> vowel
- `dh` -> letter
- `ii` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `y` -> letter
- `u` -> vowel
- `'` -> letter
- `m` -> letter
- `i` -> vowel
- `n` -> letter
- `uu` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `b` -> letter
- `i` -> vowel
- `l` -> lam_qamariyya
- `gh` -> letter
- `a` -> vowel
- `y` -> letter
- `b` -> letter
- `i` -> vowel
- `w` -> letter
- `a` -> vowel
- `y` -> letter
- `u` -> vowel
- `q` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `uu` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `S` -> shadda
- `S` -> shadda
- `a` -> vowel
- `l` -> letter
- `a` -> vowel
- `aa` -> waw_dagger_alef_carrier
- `t` -> letter
- `a` -> vowel
- `w` -> letter
- `a` -> vowel
- `m` -> letter
- `i` -> vowel
- `m` -> shadda
- `m` -> shadda
- `aa` -> madd_tabii
- `r` -> letter
- `a` -> vowel
- `z` -> letter
- `a` -> vowel
- `q_qal` -> qalqalah
- `n` -> letter
- `aa` -> small_alef_madd_tabii
- `h` -> letter
- `u` -> vowel
- `m` -> mim_sakin
- `y` -> letter
- `u` -> vowel
- `n` -> noon_sakin
- `f` -> letter
- `i` -> vowel
- `q` -> letter
- `uu` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `n_g` -> ikhfa

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 2:30 - Bakara 30

**Arabic:**
> وَإِذْ قَالَ رَبُّكَ لِلْمَلَٰٓئِكَةِ إِنِّى جَاعِلٌۭ فِى ٱلْأَرْضِ خَلِيفَةًۭ ۖ قَالُوٓا۟ أَتَجْعَلُ فِيهَا مَن يُفْسِدُ فِيهَا وَيَسْفِكُ ٱلدِّمَآءَ وَنَحْنُ نُسَبِّحُ بِحَمْدِكَ وَنُقَدِّسُ لَكَ ۖ قَالَ إِنِّىٓ أَعْلَمُ مَا لَا تَعْلَمُونَ

**Candidate output:**
```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a t a n PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k a PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu n a
```

**Stored candidate:**
```
w a ' i dh q aa l a r a b b u k a l i l m a l aa4 ' i k a t i ' i n n ii j aa 3 i l u n_g f i l ' a r D i kh a l ii f a t a n PAUSE q aa l uu4 ' a t a j_qal 3 a l u f ii h aa m a n_g y u f s i d u f ii h aa w a y a s f i k u d d i m aa4 ' a w a n a H n u n u s a b b i H u b i H a m d i k a w a n u q a d d i s u l a k a PAUSE q aa l a ' i n n ii4 ' a 3 l a m u m aa l aa t a 3 l a m uu n a
```

**Rule hits:**
- `w` -> letter
- `a` -> vowel
- `'` -> letter
- `i` -> vowel
- `dh` -> letter
- `q` -> letter
- `aa` -> madd_tabii
- `l` -> letter
- `a` -> vowel
- `r` -> letter
- `a` -> vowel
- `b` -> shadda
- `b` -> shadda
- `u` -> vowel
- `k` -> letter
- `a` -> vowel
- `l` -> letter
- `i` -> vowel
- `l` -> letter
- `m` -> letter
- `a` -> vowel
- `l` -> letter
- `aa4` -> small_alef_madd_muttasil
- `'` -> letter
- `i` -> vowel
- `k` -> letter
- `a` -> vowel
- `t` -> letter
- `i` -> vowel
- `'` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `ii` -> madd_tabii
- `j` -> letter
- `aa` -> madd_tabii
- `3` -> letter
- `i` -> vowel
- `l` -> letter
- `u` -> tanwin
- `n` -> tanwin_n
- `n_g` -> ikhfa
- `f` -> letter
- `ii` -> madd_tabii
- `i` -> iltiqa_sakinayn_madd_drop
- `l` -> lam_qamariyya
- `'` -> letter
- `a` -> vowel
- `r` -> letter
- `D` -> letter
- `i` -> vowel
- `kh` -> letter
- `a` -> vowel
- `l` -> letter
- `ii` -> madd_tabii
- `f` -> letter
- `a` -> vowel
- `t` -> letter
- `a` -> tanwin
- `n` -> tanwin_n
- `PAUSE` -> pause_mark
- `q` -> letter
- `aa` -> madd_tabii
- `l` -> letter
- `uu4` -> madd_tabii
- `'` -> letter
- `a` -> vowel
- `t` -> letter
- `a` -> vowel
- `j_qal` -> qalqalah
- `3` -> letter
- `a` -> vowel
- `l` -> letter
- `u` -> vowel
- `f` -> letter
- `ii` -> madd_tabii
- `h` -> letter
- `aa` -> madd_tabii
- `m` -> letter
- `a` -> vowel
- `n` -> noon_sakin
- `n_g` -> idgham_ghunna
- `y` -> letter
- `u` -> vowel
- `f` -> letter
- `s` -> letter
- `i` -> vowel
- `d` -> letter
- `u` -> vowel
- `f` -> letter
- `ii` -> madd_tabii
- `h` -> letter
- `aa` -> madd_tabii
- `w` -> letter
- `a` -> vowel
- `y` -> letter
- `a` -> vowel
- `s` -> letter
- `f` -> letter
- `i` -> vowel
- `k` -> letter
- `u` -> vowel
- `d` -> shadda
- `d` -> shadda
- `i` -> vowel
- `m` -> letter
- `aa4` -> madd_muttasil_or_munfasil
- `'` -> letter
- `a` -> vowel
- `w` -> letter
- `a` -> vowel
- `n` -> letter
- `a` -> vowel
- `H` -> letter
- `n` -> letter
- `u` -> vowel
- `n` -> letter
- `u` -> vowel
- `s` -> letter
- `a` -> vowel
- `b` -> shadda
- `b` -> shadda
- `i` -> vowel
- `H` -> letter
- `u` -> vowel
- `b` -> letter
- `i` -> vowel
- `H` -> letter
- `a` -> vowel
- `m` -> mim_sakin
- `d` -> letter
- `i` -> vowel
- `k` -> letter
- `a` -> vowel
- `w` -> letter
- `a` -> vowel
- `n` -> letter
- `u` -> vowel
- `q` -> letter
- `a` -> vowel
- `d` -> shadda
- `d` -> shadda
- `i` -> vowel
- `s` -> letter
- `u` -> vowel
- `l` -> letter
- `a` -> vowel
- `k` -> letter
- `a` -> vowel
- `PAUSE` -> pause_mark
- `q` -> letter
- `aa` -> madd_tabii
- `l` -> letter
- `a` -> vowel
- `'` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `ii4` -> madd_munfasil_or_silah
- `'` -> letter
- `a` -> vowel
- `3` -> letter
- `l` -> letter
- `a` -> vowel
- `m` -> letter
- `u` -> vowel
- `m` -> letter
- `aa` -> madd_tabii
- `l` -> letter
- `aa` -> madd_tabii
- `t` -> letter
- `a` -> vowel
- `3` -> letter
- `l` -> letter
- `a` -> vowel
- `m` -> letter
- `uu` -> madd_tabii
- `n` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 2:156 - Bakara 156

**Arabic:**
> ٱلَّذِينَ إِذَآ أَصَٰبَتْهُم مُّصِيبَةٌۭ قَالُوٓا۟ إِنَّا لِلَّهِ وَإِنَّآ إِلَيْهِ رَٰجِعُونَ

**Candidate output:**
```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu n a
```

**Stored candidate:**
```
' a l l a dh ii n a ' i dh aa4 ' a S aa b a t h u m_g m u S ii b a t u n_g q aa l uu4 ' i n n aa l i l l aa h i w a ' i n n aa4 ' i l a y h i r aa j i 3 uu n a
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `a` -> alif_wasla_initial_vowel
- `l` -> article_lam_shadda
- `l` -> article_lam_shadda
- `a` -> vowel
- `dh` -> letter
- `ii` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `'` -> letter
- `i` -> vowel
- `dh` -> letter
- `aa4` -> madd_muttasil_or_munfasil
- `'` -> letter
- `a` -> vowel
- `S` -> letter
- `aa` -> small_alef_madd_tabii
- `b` -> letter
- `a` -> vowel
- `t` -> letter
- `h` -> letter
- `u` -> vowel
- `m` -> mim_sakin
- `m_g` -> idgham_shafawi
- `m` -> shadda
- `u` -> vowel
- `S` -> letter
- `ii` -> madd_tabii
- `b` -> letter
- `a` -> vowel
- `t` -> letter
- `u` -> tanwin
- `n` -> tanwin_n
- `n_g` -> ikhfa
- `q` -> letter
- `aa` -> madd_tabii
- `l` -> letter
- `uu4` -> madd_tabii
- `'` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa` -> madd_tabii
- `l` -> li_prefix
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `w` -> letter
- `a` -> vowel
- `'` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa4` -> madd_muttasil_or_munfasil
- `'` -> letter
- `i` -> vowel
- `l` -> letter
- `a` -> vowel
- `y` -> letter
- `h` -> letter
- `i` -> vowel
- `r` -> letter
- `aa` -> small_alef_madd_tabii
- `j` -> letter
- `i` -> vowel
- `3` -> letter
- `uu` -> madd_tabii
- `n` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 2:255 - Bakara 255

**Arabic:**
> ٱللَّهُ لَآ إِلَٰهَ إِلَّا هُوَ ٱلْحَىُّ ٱلْقَيُّومُ ۚ لَا تَأْخُذُهُۥ سِنَةٌۭ وَلَا نَوْمٌۭ ۚ لَّهُۥ مَا فِى ٱلسَّمَٰوَٰتِ وَمَا فِى ٱلْأَرْضِ ۗ مَن ذَا ٱلَّذِى يَشْفَعُ عِندَهُۥٓ إِلَّا بِإِذْنِهِۦ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَىْءٍۢ مِّنْ عِلْمِهِۦٓ إِلَّا بِمَا شَآءَ ۚ وَسِعَ كُرْسِيُّهُ ٱلسَّمَٰوَٰتِ وَٱلْأَرْضَ ۖ وَلَا يَـُٔودُهُۥ حِفْظُهُمَا ۚ وَهُوَ ٱلْعَلِىُّ ٱلْعَظِيمُ

**Candidate output:**
```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu m u PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m u n PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D i PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' a PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D a PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii m u
```

**Stored candidate:**
```
' a L L aa h u l aa4 ' i l aa h a ' i l l aa h u w a l H a y y u l q a y y uu m u PAUSE l aa t a ' kh u dh u h uu s i n a t u n_g w a l aa n a w m u n PAUSE l l a h uu m aa f i s s a m aa w aa t i w a m aa f i l ' a r D i PAUSE m a n_g dh a l l a dh ii y a sh f a 3 u 3 i n_g d a h uu4 ' i l l aa b i ' i dh n i h ii PAUSE y a 3 l a m u m aa b a y n a ' a y d ii h i m w a m aa kh a l f a h u m PAUSE w a l aa y u H ii T uu n a b i sh a y ' i m_g m i n 3 i l m i h ii4 ' i l l aa b i m aa sh aa4 ' a PAUSE w a s i 3 a k u r s i y y u h u s s a m aa w aa t i w a l ' a r D a PAUSE w a l aa y a ' uu d u h uu H i f Z u h u m aa PAUSE w a h u w a l 3 a l i y y u l 3 a Z ii m u
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `a` -> allah_initial_vowel
- `L` -> lam_allah
- `L` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `u` -> vowel
- `l` -> letter
- `aa4` -> madd_muttasil_or_munfasil
- `'` -> letter
- `i` -> vowel
- `l` -> letter
- `aa` -> small_alef_madd_tabii
- `h` -> letter
- `a` -> vowel
- `'` -> letter
- `i` -> vowel
- `l` -> shadda
- `l` -> shadda
- `aa` -> madd_tabii
- `h` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `H` -> letter
- `a` -> vowel
- `y` -> shadda
- `y` -> shadda
- `u` -> vowel
- `l` -> lam_qamariyya
- `q` -> letter
- `a` -> vowel
- `y` -> shadda
- `y` -> shadda
- `uu` -> madd_tabii
- `m` -> letter
- `u` -> vowel
- `PAUSE` -> pause_mark
- `l` -> letter
- `aa` -> madd_tabii
- `t` -> letter
- `a` -> vowel
- `'` -> letter
- `kh` -> letter
- `u` -> vowel
- `dh` -> letter
- `u` -> vowel
- `h` -> letter
- `uu` -> madd_silah
- `s` -> letter
- `i` -> vowel
- `n` -> letter
- `a` -> vowel
- `t` -> letter
- `u` -> tanwin
- `n` -> tanwin_n
- `n_g` -> idgham_ghunna
- `w` -> letter
- `a` -> vowel
- `l` -> letter
- `aa` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `w` -> letter
- `m` -> letter
- `u` -> tanwin
- `n` -> tanwin_n
- `PAUSE` -> pause_mark
- `l` -> shadda
- `l` -> shadda
- `a` -> vowel
- `h` -> letter
- `uu` -> madd_silah
- `m` -> letter
- `aa` -> madd_tabii
- `f` -> letter
- `ii` -> madd_tabii
- `i` -> iltiqa_sakinayn_madd_drop
- `s` -> shadda
- `s` -> shadda
- `a` -> vowel
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `w` -> letter
- `aa` -> small_alef_madd_tabii
- `t` -> letter
- `i` -> vowel
- `w` -> letter
- `a` -> vowel
- `m` -> letter
- `aa` -> madd_tabii
- `f` -> letter
- `ii` -> madd_tabii
- `i` -> iltiqa_sakinayn_madd_drop
- `l` -> lam_qamariyya
- `'` -> letter
- `a` -> vowel
- `r` -> letter
- `D` -> letter
- `i` -> vowel
- `PAUSE` -> pause_mark
- `m` -> letter
- `a` -> vowel
- `n` -> noon_sakin
- `n_g` -> ikhfa
- `dh` -> letter
- `aa` -> madd_tabii
- `a` -> iltiqa_sakinayn_madd_drop
- `l` -> article_lam_shadda
- `l` -> article_lam_shadda
- `a` -> vowel
- `dh` -> letter
- `ii` -> madd_tabii
- `y` -> letter
- `a` -> vowel
- `sh` -> letter
- `f` -> letter
- `a` -> vowel
- `3` -> letter
- `u` -> vowel
- `3` -> letter
- `i` -> vowel
- `n` -> noon_sakin
- `d` -> letter
- `a` -> vowel
- `h` -> letter
- `uu4` -> madd_silah
- `n_g` -> ikhfa
- `'` -> letter
- `i` -> vowel
- `l` -> shadda
- `l` -> shadda
- `aa` -> madd_tabii
- `b` -> letter
- `i` -> vowel
- `'` -> letter
- `i` -> vowel
- `dh` -> letter
- `n` -> letter
- `i` -> vowel
- `h` -> letter
- `ii` -> madd_silah
- `PAUSE` -> pause_mark
- `y` -> letter
- `a` -> vowel
- `3` -> letter
- `l` -> letter
- `a` -> vowel
- `m` -> letter
- `u` -> vowel
- `m` -> letter
- `aa` -> madd_tabii
- `b` -> letter
- `a` -> vowel
- `y` -> letter
- `n` -> letter
- `a` -> vowel
- `'` -> letter
- `a` -> vowel
- `y` -> letter
- `d` -> letter
- `ii` -> madd_tabii
- `h` -> letter
- `i` -> vowel
- `m` -> mim_sakin
- `w` -> letter
- `a` -> vowel
- `m` -> letter
- `aa` -> madd_tabii
- `kh` -> letter
- `a` -> vowel
- `l` -> letter
- `f` -> letter
- `a` -> vowel
- `h` -> letter
- `u` -> vowel
- `m` -> mim_sakin
- `PAUSE` -> pause_mark
- `w` -> letter
- `a` -> vowel
- `l` -> letter
- `aa` -> madd_tabii
- `y` -> letter
- `u` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `T` -> letter
- `uu` -> madd_tabii
- `n` -> letter
- `a` -> vowel
- `b` -> letter
- `i` -> vowel
- `sh` -> letter
- `a` -> vowel
- `y` -> letter
- `'` -> letter
- `i` -> tanwin
- `n` -> tanwin_n
- `m_g` -> idgham_ghunna
- `m` -> shadda
- `i` -> vowel
- `n` -> noon_sakin
- `n` -> izhar
- `3` -> letter
- `i` -> vowel
- `l` -> letter
- `m` -> letter
- `i` -> vowel
- `h` -> letter
- `ii4` -> madd_silah
- `'` -> letter
- `i` -> vowel
- `l` -> shadda
- `l` -> shadda
- `aa` -> madd_tabii
- `b` -> letter
- `i` -> vowel
- `m` -> letter
- `aa` -> madd_tabii
- `sh` -> letter
- `aa4` -> madd_muttasil_or_munfasil
- `'` -> letter
- `a` -> vowel
- `PAUSE` -> pause_mark
- `w` -> letter
- `a` -> vowel
- `s` -> letter
- `i` -> vowel
- `3` -> letter
- `a` -> vowel
- `k` -> letter
- `u` -> vowel
- `r` -> letter
- `s` -> letter
- `i` -> vowel
- `y` -> shadda
- `y` -> shadda
- `u` -> vowel
- `h` -> letter
- `u` -> vowel
- `s` -> shadda
- `s` -> shadda
- `a` -> vowel
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `w` -> letter
- `aa` -> small_alef_madd_tabii
- `t` -> letter
- `i` -> vowel
- `w` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `'` -> letter
- `a` -> vowel
- `r` -> letter
- `D` -> letter
- `a` -> vowel
- `PAUSE` -> pause_mark
- `w` -> letter
- `a` -> vowel
- `l` -> letter
- `aa` -> madd_tabii
- `y` -> letter
- `a` -> pre_hamza_vowel
- `'` -> hamza_mark
- `uu` -> madd_tabii
- `d` -> letter
- `u` -> vowel
- `h` -> letter
- `uu` -> madd_silah
- `H` -> letter
- `i` -> vowel
- `f` -> letter
- `Z` -> letter
- `u` -> vowel
- `h` -> letter
- `u` -> vowel
- `m` -> letter
- `aa` -> madd_tabii
- `PAUSE` -> pause_mark
- `w` -> letter
- `a` -> vowel
- `h` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `3` -> letter
- `a` -> vowel
- `l` -> letter
- `i` -> vowel
- `y` -> shadda
- `y` -> shadda
- `u` -> vowel
- `l` -> lam_qamariyya
- `3` -> letter
- `a` -> vowel
- `Z` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `u` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 19:1 - Maryam 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ كٓهيعٓصٓ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i k aa6 f h aa y aa 3 a y n_g S aa6 d_qal
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i k aa6 f h aa y aa 3 a y n_g S aa6 d_qal
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `k` -> huroof_muqattaat
- `aa6` -> huroof_muqattaat
- `f` -> huroof_muqattaat
- `h` -> huroof_muqattaat
- `aa` -> huroof_muqattaat
- `y` -> huroof_muqattaat
- `aa` -> huroof_muqattaat
- `3` -> huroof_muqattaat
- `a` -> huroof_muqattaat
- `y` -> huroof_muqattaat
- `n_g` -> huroof_muqattaat
- `S` -> huroof_muqattaat
- `aa6` -> huroof_muqattaat
- `d_qal` -> huroof_muqattaat

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 36:1 - Yasin 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ يسٓ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i y aa s ii6 n
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i y aa s ii6 n
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `y` -> huroof_muqattaat
- `aa` -> huroof_muqattaat
- `s` -> huroof_muqattaat
- `ii6` -> huroof_muqattaat
- `n` -> huroof_muqattaat

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 36:2 - Yasin 2

**Arabic:**
> وَٱلْقُرْءَانِ ٱلْحَكِيمِ

**Candidate output:**
```
w a l q u r ' aa n i l H a k ii m i
```

**Stored candidate:**
```
w a l q u r ' aa n i l H a k ii m i
```

**Rule hits:**
- `w` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `q` -> letter
- `u` -> vowel
- `r` -> letter
- `'` -> letter
- `aa` -> madd_tabii
- `n` -> letter
- `i` -> vowel
- `l` -> lam_qamariyya
- `H` -> letter
- `a` -> vowel
- `k` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 67:1 - Mulk 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ تَبَٰرَكَ ٱلَّذِى بِيَدِهِ ٱلْمُلْكُ وَهُوَ عَلَىٰ كُلِّ شَىْءٍۢ قَدِيرٌ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i t a b aa r a k a l l a dh ii b i y a d i h i l m u l k u w a h u w a 3 a l aa k u l l i sh a y ' i n_g q a d ii r u n
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i t a b aa r a k a l l a dh ii b i y a d i h i l m u l k u w a h u w a 3 a l aa k u l l i sh a y ' i n_g q a d ii r u n
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `t` -> letter
- `a` -> vowel
- `b` -> letter
- `aa` -> small_alef_madd_tabii
- `r` -> letter
- `a` -> vowel
- `k` -> letter
- `a` -> vowel
- `l` -> article_lam_shadda
- `l` -> article_lam_shadda
- `a` -> vowel
- `dh` -> letter
- `ii` -> madd_tabii
- `b` -> letter
- `i` -> vowel
- `y` -> letter
- `a` -> vowel
- `d` -> letter
- `i` -> vowel
- `h` -> letter
- `i` -> vowel
- `l` -> lam_qamariyya
- `m` -> letter
- `u` -> vowel
- `l` -> letter
- `k` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `h` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `3` -> letter
- `a` -> vowel
- `l` -> letter
- `aa` -> madd_tabii
- `k` -> letter
- `u` -> vowel
- `l` -> shadda
- `l` -> shadda
- `i` -> vowel
- `sh` -> letter
- `a` -> vowel
- `y` -> letter
- `'` -> letter
- `i` -> tanwin
- `n` -> tanwin_n
- `n_g` -> ikhfa
- `q` -> letter
- `a` -> vowel
- `d` -> letter
- `ii` -> madd_tabii
- `r` -> letter
- `u` -> tanwin
- `n` -> tanwin_n

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 108:1 - Kawthar 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ إِنَّآ أَعْطَيْنَٰكَ ٱلْكَوْثَرَ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' i n n aa4 ' a 3 T a y n aa k a l k a w th a r a
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i ' i n n aa4 ' a 3 T a y n aa k a l k a w th a r a
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `'` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa4` -> madd_muttasil_or_munfasil
- `'` -> letter
- `a` -> vowel
- `3` -> letter
- `T` -> letter
- `a` -> vowel
- `y` -> letter
- `n` -> letter
- `aa` -> small_alef_madd_tabii
- `k` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `k` -> letter
- `a` -> vowel
- `w` -> letter
- `th` -> letter
- `a` -> vowel
- `r` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 108:2 - Kawthar 2

**Arabic:**
> فَصَلِّ لِرَبِّكَ وَٱنْحَرْ

**Candidate output:**
```
f a S a l l i l i r a b b i k a w a n H a r
```

**Stored candidate:**
```
f a S a l l i l i r a b b i k a w a n H a r
```

**Rule hits:**
- `f` -> letter
- `a` -> vowel
- `S` -> letter
- `a` -> vowel
- `l` -> shadda
- `l` -> shadda
- `i` -> vowel
- `l` -> letter
- `i` -> vowel
- `r` -> letter
- `a` -> vowel
- `b` -> shadda
- `b` -> shadda
- `i` -> vowel
- `k` -> letter
- `a` -> vowel
- `w` -> letter
- `a` -> vowel
- `n` -> noon_sakin
- `H` -> letter
- `a` -> vowel
- `r` -> letter
- `n` -> izhar

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 108:3 - Kawthar 3

**Arabic:**
> إِنَّ شَانِئَكَ هُوَ ٱلْأَبْتَرُ

**Candidate output:**
```
' i n n a sh aa n i ' a k a h u w a l ' a b_qal t a r u
```

**Stored candidate:**
```
' i n n a sh aa n i ' a k a h u w a l ' a b_qal t a r u
```

**Rule hits:**
- `'` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `a` -> vowel
- `sh` -> letter
- `aa` -> madd_tabii
- `n` -> letter
- `i` -> vowel
- `'` -> letter
- `a` -> vowel
- `k` -> letter
- `a` -> vowel
- `h` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `'` -> letter
- `a` -> vowel
- `b_qal` -> qalqalah
- `t` -> letter
- `a` -> vowel
- `r` -> letter
- `u` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 112:1 - Ikhlas 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ هُوَ ٱللَّهُ أَحَدٌ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d u n
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l h u w a L L aa h u ' a H a d u n
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `q` -> letter
- `u` -> vowel
- `l` -> letter
- `h` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `L` -> lam_allah
- `L` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `u` -> vowel
- `'` -> letter
- `a` -> vowel
- `H` -> letter
- `a` -> vowel
- `d` -> letter
- `u` -> tanwin
- `n` -> tanwin_n

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 112:2 - Ikhlas 2

**Arabic:**
> ٱللَّهُ ٱلصَّمَدُ

**Candidate output:**
```
' a L L aa h u S S a m a d u
```

**Stored candidate:**
```
' a L L aa h u S S a m a d u
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `a` -> allah_initial_vowel
- `L` -> lam_allah
- `L` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `u` -> vowel
- `S` -> shadda
- `S` -> shadda
- `a` -> vowel
- `m` -> letter
- `a` -> vowel
- `d` -> letter
- `u` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 112:3 - Ikhlas 3

**Arabic:**
> لَمْ يَلِدْ وَلَمْ يُولَدْ

**Candidate output:**
```
l a m y a l i d_qal w a l a m y uu l a d_qal
```

**Stored candidate:**
```
l a m y a l i d_qal w a l a m y uu l a d_qal
```

**Rule hits:**
- `l` -> letter
- `a` -> vowel
- `m` -> mim_sakin
- `y` -> letter
- `a` -> vowel
- `l` -> letter
- `i` -> vowel
- `d_qal` -> qalqalah
- `w` -> letter
- `a` -> vowel
- `l` -> letter
- `a` -> vowel
- `m` -> mim_sakin
- `y` -> letter
- `uu` -> madd_tabii
- `l` -> letter
- `a` -> vowel
- `d_qal` -> qalqalah

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 112:4 - Ikhlas 4

**Arabic:**
> وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌۢ

**Candidate output:**
```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d u n
```

**Stored candidate:**
```
w a l a m y a k u l l a h uu k u f u w a n ' a H a d u n
```

**Rule hits:**
- `w` -> letter
- `a` -> vowel
- `l` -> letter
- `a` -> vowel
- `m` -> mim_sakin
- `y` -> letter
- `a` -> vowel
- `k` -> letter
- `u` -> vowel
- `n` -> noon_sakin
- `l` -> shadda
- `l` -> shadda
- `a` -> vowel
- `h` -> letter
- `uu` -> madd_silah
- `k` -> letter
- `u` -> vowel
- `f` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> tanwin
- `n` -> tanwin_n
- `n` -> izhar
- `'` -> letter
- `a` -> vowel
- `H` -> letter
- `a` -> vowel
- `d` -> letter
- `u` -> tanwin
- `n` -> tanwin_n

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 113:1 - Falaq 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i l f a l a q i
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i l f a l a q i
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `q` -> letter
- `u` -> vowel
- `l` -> letter
- `'` -> letter
- `a` -> vowel
- `3` -> letter
- `uu` -> madd_tabii
- `dh` -> letter
- `u` -> vowel
- `b` -> letter
- `i` -> vowel
- `r` -> letter
- `a` -> vowel
- `b` -> shadda
- `b` -> shadda
- `i` -> vowel
- `l` -> lam_qamariyya
- `f` -> letter
- `a` -> vowel
- `l` -> letter
- `a` -> vowel
- `q` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 113:2 - Falaq 2

**Arabic:**
> مِن شَرِّ مَا خَلَقَ

**Candidate output:**
```
m i n_g sh a r r i m aa kh a l a q a
```

**Stored candidate:**
```
m i n_g sh a r r i m aa kh a l a q a
```

**Rule hits:**
- `m` -> letter
- `i` -> vowel
- `n` -> noon_sakin
- `n_g` -> ikhfa
- `sh` -> letter
- `a` -> vowel
- `r` -> shadda
- `r` -> shadda
- `i` -> vowel
- `m` -> letter
- `aa` -> madd_tabii
- `kh` -> letter
- `a` -> vowel
- `l` -> letter
- `a` -> vowel
- `q` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 113:3 - Falaq 3

**Arabic:**
> وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ

**Candidate output:**
```
w a m i n_g sh a r r i gh aa s i q i n ' i dh aa w a q a b a
```

**Stored candidate:**
```
w a m i n_g sh a r r i gh aa s i q i n ' i dh aa w a q a b a
```

**Rule hits:**
- `w` -> letter
- `a` -> vowel
- `m` -> letter
- `i` -> vowel
- `n` -> noon_sakin
- `n_g` -> ikhfa
- `sh` -> letter
- `a` -> vowel
- `r` -> shadda
- `r` -> shadda
- `i` -> vowel
- `gh` -> letter
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel
- `q` -> letter
- `i` -> tanwin
- `n` -> tanwin_n
- `n` -> izhar
- `'` -> letter
- `i` -> vowel
- `dh` -> letter
- `aa` -> madd_tabii
- `w` -> letter
- `a` -> vowel
- `q` -> letter
- `a` -> vowel
- `b` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 113:4 - Falaq 4

**Arabic:**
> وَمِن شَرِّ ٱلنَّفَّٰثَٰتِ فِى ٱلْعُقَدِ

**Candidate output:**
```
w a m i n_g sh a r r i n n a f f aa th aa t i f i l 3 u q a d i
```

**Stored candidate:**
```
w a m i n_g sh a r r i n n a f f aa th aa t i f i l 3 u q a d i
```

**Rule hits:**
- `w` -> letter
- `a` -> vowel
- `m` -> letter
- `i` -> vowel
- `n` -> noon_sakin
- `n_g` -> ikhfa
- `sh` -> letter
- `a` -> vowel
- `r` -> shadda
- `r` -> shadda
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `a` -> vowel
- `f` -> shadda
- `f` -> shadda
- `aa` -> small_alef_madd_tabii
- `th` -> letter
- `aa` -> small_alef_madd_tabii
- `t` -> letter
- `i` -> vowel
- `f` -> letter
- `ii` -> madd_tabii
- `i` -> iltiqa_sakinayn_madd_drop
- `l` -> lam_qamariyya
- `3` -> letter
- `u` -> vowel
- `q` -> letter
- `a` -> vowel
- `d` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 113:5 - Falaq 5

**Arabic:**
> وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ

**Candidate output:**
```
w a m i n_g sh a r r i H aa s i d i n ' i dh aa H a s a d a
```

**Stored candidate:**
```
w a m i n_g sh a r r i H aa s i d i n ' i dh aa H a s a d a
```

**Rule hits:**
- `w` -> letter
- `a` -> vowel
- `m` -> letter
- `i` -> vowel
- `n` -> noon_sakin
- `n_g` -> ikhfa
- `sh` -> letter
- `a` -> vowel
- `r` -> shadda
- `r` -> shadda
- `i` -> vowel
- `H` -> letter
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel
- `d` -> letter
- `i` -> tanwin
- `n` -> tanwin_n
- `n` -> izhar
- `'` -> letter
- `i` -> vowel
- `dh` -> letter
- `aa` -> madd_tabii
- `H` -> letter
- `a` -> vowel
- `s` -> letter
- `a` -> vowel
- `d` -> letter
- `a` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 114:1 - Nas 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ قُلْ أَعُوذُ بِرَبِّ ٱلنَّاسِ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i n n aa s i
```

**Stored candidate:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i q u l ' a 3 uu dh u b i r a b b i n n aa s i
```

**Rule hits:**
- `b` -> letter
- `i` -> vowel
- `s` -> letter
- `m` -> letter
- `i` -> vowel
- `l` -> lam_allah
- `l` -> lam_allah_shadda
- `aa` -> allah_madd
- `h` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `m` -> letter
- `aa` -> small_alef_madd_tabii
- `n` -> letter
- `i` -> vowel
- `r` -> shadda
- `r` -> shadda
- `a` -> vowel
- `H` -> letter
- `ii` -> madd_tabii
- `m` -> letter
- `i` -> vowel
- `q` -> letter
- `u` -> vowel
- `l` -> letter
- `'` -> letter
- `a` -> vowel
- `3` -> letter
- `uu` -> madd_tabii
- `dh` -> letter
- `u` -> vowel
- `b` -> letter
- `i` -> vowel
- `r` -> letter
- `a` -> vowel
- `b` -> shadda
- `b` -> shadda
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 114:2 - Nas 2

**Arabic:**
> مَلِكِ ٱلنَّاسِ

**Candidate output:**
```
m a l i k i n n aa s i
```

**Stored candidate:**
```
m a l i k i n n aa s i
```

**Rule hits:**
- `m` -> letter
- `a` -> vowel
- `l` -> letter
- `i` -> vowel
- `k` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 114:3 - Nas 3

**Arabic:**
> إِلَٰهِ ٱلنَّاسِ

**Candidate output:**
```
' i l aa h i n n aa s i
```

**Stored candidate:**
```
' i l aa h i n n aa s i
```

**Rule hits:**
- `'` -> letter
- `i` -> vowel
- `l` -> letter
- `aa` -> small_alef_madd_tabii
- `h` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 114:4 - Nas 4

**Arabic:**
> مِن شَرِّ ٱلْوَسْوَاسِ ٱلْخَنَّاسِ

**Candidate output:**
```
m i n_g sh a r r i l w a s w aa s i l kh a n n aa s i
```

**Stored candidate:**
```
m i n_g sh a r r i l w a s w aa s i l kh a n n aa s i
```

**Rule hits:**
- `m` -> letter
- `i` -> vowel
- `n` -> noon_sakin
- `n_g` -> ikhfa
- `sh` -> letter
- `a` -> vowel
- `r` -> shadda
- `r` -> shadda
- `i` -> vowel
- `l` -> lam_qamariyya
- `w` -> letter
- `a` -> vowel
- `s` -> letter
- `w` -> letter
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel
- `l` -> lam_qamariyya
- `kh` -> letter
- `a` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 114:5 - Nas 5

**Arabic:**
> ٱلَّذِى يُوَسْوِسُ فِى صُدُورِ ٱلنَّاسِ

**Candidate output:**
```
' a l l a dh ii y u w a s w i s u f ii S u d uu r i n n aa s i
```

**Stored candidate:**
```
' a l l a dh ii y u w a s w i s u f ii S u d uu r i n n aa s i
```

**Rule hits:**
- `'` -> alif_wasla_initial
- `a` -> alif_wasla_initial_vowel
- `l` -> article_lam_shadda
- `l` -> article_lam_shadda
- `a` -> vowel
- `dh` -> letter
- `ii` -> madd_tabii
- `y` -> letter
- `u` -> vowel
- `w` -> letter
- `a` -> vowel
- `s` -> letter
- `w` -> letter
- `i` -> vowel
- `s` -> letter
- `u` -> vowel
- `f` -> letter
- `ii` -> madd_tabii
- `S` -> letter
- `u` -> vowel
- `d` -> letter
- `uu` -> madd_tabii
- `r` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

### 114:6 - Nas 6

**Arabic:**
> مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ

**Candidate output:**
```
m i n a l j i n n a t i w a n n aa s i
```

**Stored candidate:**
```
m i n a l j i n n a t i w a n n aa s i
```

**Rule hits:**
- `m` -> letter
- `i` -> vowel
- `n` -> letter
- `a` -> vowel
- `l` -> lam_qamariyya
- `j` -> letter
- `i` -> vowel
- `n` -> shadda
- `n` -> shadda
- `a` -> vowel
- `t` -> letter
- `i` -> vowel
- `w` -> letter
- `a` -> vowel
- `n` -> shadda
- `n` -> shadda
- `aa` -> madd_tabii
- `s` -> letter
- `i` -> vowel

**Hafiz note:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```

