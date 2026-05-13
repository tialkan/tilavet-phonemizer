# Hafiz Validation Protocol

## Amac

Phonemizer ciktisinin dogru oldugunu LLM tahminiyle degil, kural ve hafiz
notuyla ilerletmek.

## Her batch icin format

Her ayet icin:

- Arabic text
- Phonemizer output
- Rule hits
- Hafiz note

Hafiz notu mumkunse su formatta alinmali:

```text
Ayah: 2:255
Location: "... ilgili kelime ..."
Current: ...
Expected: ...
Rule: madd / idgham / ihfa / lam Allah / qalqalah / waqf / other
Confidence: high / medium / low
Note:
```

## Batch secimi

Ilk 35 ayetlik seed korunur, ama V1 gelistirmede her batch dengeli olmali:

- Fatiha tamami
- kisa sureler: Ikhlas, Falaq, Nas, Kawthar
- uzun ve kural yogun ayetler: 2:30, 2:156, 2:255
- huroof muqatta'at: 2:1, 19:1, 36:1
- tanwin/nun sakin yogun ornekler
- waqf isaretleri olan ornekler

## Kabul kriteri

Bir kural V1'e girmeden once:

1. En az bir validation ornegi olmali.
2. Unit test eklenmeli.
3. Rule hit adi dokumanda gecmeli.
4. Degisim eski seed orneklerini bozuyorsa not dusulmeli.

