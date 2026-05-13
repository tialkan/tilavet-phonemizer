# Waqf / Pause Decision

Bu karar 35 ayetlik V1 LLM hafiz review turlarindan sonra alindi.

## Karar

V1 seed icin **Option A** korunacak:

```text
wasl phoneme sequence + PAUSE metadata marker
```

`PAUSE`, fonetik waqf donusumu degil, mushaf durak isaretinin yerini gosteren
opsiyonel alignment ipucudur.

Ornek:

```text
r a y b a PAUSE f ii h i
kh a l ii f a t a n PAUSE q aa l uu4
n a w m u n PAUSE l l a h uu
```

Bu ciktilar dogrudan "kari burada kesin waqf yapti" anlamina gelmez. Runtime
decoder `PAUSE` noktasinda sessizlik/nefes ihtimaline daha yuksek tolerans
gosterebilir.

## Neden Option A?

- V1'in hedefi tek ve tutarli bir wasl candidate uretmek.
- Kelime highlight icin kelime-fonem offsetleri stabil kaliyor.
- Mushaf duraklari zorunlu waqf degil; okuyucu bazen durur, bazen wasl eder.
- `PAUSE` fonem akisini bozmadan metadata olarak UI ve decoder tarafina bilgi
  tasir.
- LLM review turlarinda kalan `PAUSE` itirazlari fonemizer bug'i degil,
  variant/runtime politikasi olarak siniflandirildi.

## CTC / Model Karari

`PAUSE`, ana CTC phoneme class listesine zorunlu fonem olarak sokulmayacak.

Tavsiye edilen temsil:

- phoneme sequence: wasl sembolleri
- metadata: pause boundary indexleri
- decoder: pause boundary'de optional gap/silence prior

Eger ileride model special token desteklerse `PAUSE` soft alignment token'i
olarak denenebilir, ama temel fonetik sinif sayimina dahil edilmemeli.

## Roadmap: Option C

Gercek dunya tilavetinde waqf cok yaygin oldugu icin daha sonra **Option C**
tasarlanacak:

1. `wasl_candidate`
2. `waqf_on_pause`
3. `cross_ayah_wasl`

Runtime Quran-only decoder bu varyantlari bir graph gibi kullanabilir.

## Waqf-on-PAUSE Modunda Gereken Donusumler

Bu mod V1 seed icin aktif degil; ileride ayri export olarak uygulanacak.

- final short harakah dusmesi veya sakinlesme
- tanwinin waqf formuna donusmesi
- taa marbuta `t` -> `h`
- madd arid lis-sukun icin uzatma varyanti
- pause sonrasi takip eden kelimeyle idgham/wasl iliskisinin kesilmesi
- ayetler arasi wasl/nun qutni varyantlarinin ayri graph kenarlari olarak
  modellenmesi

## Pratik Sonuc

35 ayetlik mevcut `candidate_v1`:

- V1 wasl+metadata seed olarak korunabilir.
- Dogrudan `gold_v1`e cevrilmeden once `status` alanlari ayrica isaretlenmeli.
- Waqf varyantlari icin ayri `gold_waqf_on_pause` veya variant export uretmek
  daha dogru olur.
