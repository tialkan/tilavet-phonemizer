# Recovery Notes

Bu repo, kaybolan onceki calismadan elde kalan ana dersleri kalici hale
getirmek icin acildi.

## Kurtarilan kararlar

- Whisper large-v3-turbo ana runtime motoru olmamali.
- Whisper ancak debug/teacher veya data bootstrapping araci olarak tutulabilir.
- Asil urun problemi ASR degil, Quran-only audio-to-phoneme alignment.
- Phonemizer altin etiket uretir; CTC modeli fonem posterioru uretir.
- Decoder serbest metin degil, Quran fonem haritasi icinde arama yapar.
- Word highlight icin her kelimenin fonem offset'i onceden tutulur.

## Eski V0'dan gorulen riskler

- Alif wasla ve connected/disconnected okuma karisabiliyor.
- Lam Allah icin tarqiq/tafkhim ayri sembol karari gerekiyor.
- Taa marbuta wasl/waqf modu acikca belirtilmeli.
- Huroof muqatta'at ayri tablo gerektiriyor.
- Waqf isaretleri ve ayet sonu stratejisi model hedefinden ayrilmali.
- LLM hafiz kontrolu yardimci olabilir, ama nihai kabul insan hafiz notuyla
  ve testle yapilmali.

## Yeniden kaybetmemek icin

- Her kural testle girecek.
- Her tartismali ayet validation seed'e eklenecek.
- Hafiz notlari serbest metin olarak kalmayacak; ayah/location/current/expected
  formatinda islenecek.
- Buyuk model egitimine gecmeden once phonemizer coverage raporu cikacak.

