# Phoneme Spec

Bu dosya V1 sembol sozlesmesidir. Hafiz notlariyla degisebilir, ama degisimler
test ve validation seed ile birlikte yapilmalidir.

## Konsonantlar

| Symbol | Arabic |
|---|---|
| `'` | hamza / pronounced alif carrier |
| `b` | ba |
| `t` | ta |
| `th` | tha |
| `j` | jim |
| `H` | ha throat |
| `kh` | kha |
| `d` | dal |
| `dh` | dhal |
| `r` | ra |
| `z` | zay |
| `s` | sin |
| `sh` | shin |
| `S` | sad |
| `D` | dad |
| `T` | ta emphatic |
| `Z` | za emphatic |
| `3` | ayn |
| `gh` | ghayn |
| `f` | fa |
| `q` | qaf |
| `k` | kaf |
| `l` | lam |
| `L` | lafzatullah tafkhim lam |
| `m` | mim |
| `n` | nun |
| `h` | ha |
| `w` | waw consonant |
| `y` | ya consonant |

## Vokaller

- `a`, `i`, `u`: kisa hareke
- `aa`, `ii`, `uu`: madd tabii
- `aa4`, `ii4`, `uu4`: madd muttasil/munfasil adayi
- `aa6`, `ii6`, `uu6`: madd lazim adayi

## Varyantlar

- `n_g`: nun/tanwin ghunna, ihfa veya ghunnali idgham
- `m_g`: iqlab veya mim ghunna
- `q_qal`, `T_qal`, `b_qal`, `j_qal`, `d_qal`: qalqalah
- `PAUSE`: mushaf durak isareti
- `BREATH`: ayet sonu veya uzun durak icin ayrilacak sembol

## Kritik V1 konvansiyonlari

- Alif wasla utterance basinda okunur, wasl halinde dusurulur.
- Lam shamsiyya yazidaki lam'i fonetik akistan dusurur; sonraki harf shadda
  ile temsil edilir.
- Lam qamariyya fonetik akista `l` olarak kalir.
- Lafzatullah lam'i onceki vokal `a/u` ise `L`, `i` ise `l` olarak isaretlenir.
- Taa marbuta V1 wasl modunda `t`, stop modunda `h` olur.
- Qalqalah sukunlu `q T b j d` harflerinde sembol varyanti olarak isaretlenir.
- Small alif/dagger alif onceki fatha ile birleserek tek uzun vokal uretir:
  `m a aa` degil `m aa`.
- Ha kinayah silah isaretleri `uu`/`ii`, hamza oncesinde `uu4`/`ii4` olarak
  temsil edilir.
- Tasiyici harf uzerindeki hamza ayri hamza olarak kalir; `يَـُٔودُهُۥ`
  orneginde `y a ' uu d u h uu` uretilir.
- Wasl modunda uzun vokalden sonra hamzat-wasl ile baslayan kelime gelirse
  iltiqa al-sakinayn sebebiyle uzun vokal kisa vokale duser:
  `n aa ٱلص...` -> `n a S S...`, `f ii ٱل...` -> `f i l...`.
- `PAUSE` V1'de waqf donusumu degil, mushaf durak marker'idir. Marker
  korunurken final hareke/tanwin oldugu gibi kalabilir; tam waqf fonetigi
  ayri bir export modu olarak tasarlanacaktir.
- `PAUSE` ana CTC fonem sinif listesine zorunlu fonem olarak dahil edilmez.
  Tercih edilen kullanim, pause boundary'yi metadata ve decoder icin optional
  silence/gap prior olarak tasimaktir.
- Ayet-yerel phonemization ayetler arasi wasl/nun-qutni baglantilarini
  varsaymaz. Bu baglantilar sure/akış variant export'unun konusu olacak.
