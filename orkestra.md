# Tilavet Phonemizer - Hugging Face Yayın Yol Haritası

## Proje Hedefi

Tilavet Phonemizer'i Hugging Face'e yayınlanmaya hazır, mükemmel ve kusursuz bir paket haline getirmek.

## Mevcut Durum (May 2026)

✅ **Tamamlanan:**
- V1 rule-based phonemizer çekirdeği (833 satır)
- 32 unit test (tümü geçiyor)
- 35 ayetlik validation seed
- V1 fonem sembol sözleşmesi
- Hafız review süreci altyapısı
- LLM review synthesis dokümantasyonu

⏳ **Pending (P0):**
- Waqf/PAUSE varyant modu
- Ayetler arası wasl/nun qutni

## Yol Haritası

### Faz 1: Paket Altyapısı ve Standartlaştırma

#### 1.1 PyPI/Hugging Face Paket Yapısı
- [ ] `pyproject.toml` güncelleme:
  - `license` alanını açık lisansla değiştirme (MIT/Apache-2.0)
  - `keywords`, `classifiers` ekleme
  - `dependencies` tanımlama
  - `optional-dependencies` (dev, test)
- [ ] `MANIFEST.in` oluşturma (tüm gerekli dosyalar için)
- [ ] `setup.py` yerine pyproject.toml'a tam güvenme
- [ ] Package metadata kontrolü: `python3 -m build --check`

#### 1.2 Dokümantasyon Standartlaştırma
- [ ] `README.md` genişletme:
  - Kurulum talimatları
  - Hızlı başlangıç örnekleri
  - API referansı linkleri
  - Kullanım örnekleri
  - Hafız validation süreci açıklaması
- [ ] `CHANGELOG.md` oluşturma
- [ ] `CONTRIBUTING.md` oluşturma
- [ ] `LICENSE` dosyası ekleme

#### 1.3 Test Altyapısı Güçlendirme
- [ ] `pytest` geçişi (unittest'ten)
- [ ] `pytest.ini` yapılandırması
- [ ] Coverage raporu (`pytest-cov`)
- [ ] CI/CD için GitHub Actions workflow
- [ ] Test kapsamını %80+ çıkarma
- [ ] Integration testler ekleme

### Faz 2: Fonem Doğruluk ve Kalite

#### 2.1 Waqf/PAUSE Varyant Modu (P0)
- [ ] `waqf_on_pause` fonksiyonu implementasyonu:
  - Final hareke düşmesi kuralları
  - Tanwin dönüşümleri
  - Taa marbuta (t → h)
  - Madd arid lis-sukun işlemleri
  - Pause sonrası idgham kesilmesi
- [ ] Unit testler ekleme
- [ ] Validation seed güncelleme

#### 2.2 Ayetler Arası Wasl/Nun Qutni (P0)
- [ ] Cross-ayah wasl fonksiyonu
- [ ] Nun qutni variantları
- [ ] Sure/akış modu export
- [ ] Integration testler

#### 2.3 Quran-Wide Validation
- [ ] Tüm Kuran için phonemization testi
- [ ] Hata tespit ve düzeltme
- [ ] Performans benchmarking
- [ ] Memory usage optimizasyonu

### Faz 3: LLM Hafız Review Entegrasyonu

#### 3.1 Multi-LLM Review Pipeline
- [ ] Review prompt standardizasyonu
- [ ] Reviewer LLM listesi (5-6 farklı model):
  1. GPT-4 (primary)
  2. Claude 3.5 Opus
  3. Gemini Ultra
  4. Llama 3 70B
  5. Mistral Large
  6. Qwen 72B
- [ ] Review format standardizasyonu
- [ ] Review aggregation logic
- [ ] Dispute resolution mekanizması

#### 3.2 Review Automation
- [ ] Automated review script
- [ ] Review result parsing
- [ ] Auto-test generation from reviews
- [ ] Review tracking dashboard

#### 3.3 Validation Status Modeli
- [ ] `candidate_v1` → `gold_wasl_v1` promotion
- [ ] `gold_waqf_on_pause_v1` alanı
- [ ] Reviewer provenance tracking
- [ ] Agreement count calculation

### Faz 4: Hugging Face Hub Hazırlığı

#### 4.1 Model Card
- [ ] `README.md` → Hugging Face model card formatı
  - Model description
  - Usage examples
  - Training data (kaynak)
  - Limitations
  - Citation
  - Ethical considerations
- [ ] Inference widget demo
- [ ] Spaces demo (opsiyonel)

#### 4.2 Dataset Hazırlığı
- [ ] Quran text dataset (Uthmani script)
- [ ] Phonemized Quran dataset
- [ ] Validation dataset (35 ayet + expansion)
- [ ] Dataset card oluşturma

#### 4.3 Release Stratejisi
- [ ] Semantic versioning (v0.1.0 → v1.0.0)
- [ ] Pre-release testing
- [ ] Beta release (v0.2.0-beta)
- [ ] Stable release (v1.0.0)

### Faz 5: Runtime ve Export

#### 5.1 CTC Class Listesi
- [ ] `phoneme-spec.md`'den class listesi üretimi
- [ ] `PAUSE` metadata handling
- [ ] Class-to-index mapping
- [ ] Index-to-class mapping

#### 5.2 Quran-Wide Export
- [ ] Sure/ayet/kelime/fonem offset map
- [ ] Pause boundary metadata
- [ ] Trie/suffix index for decoder
- [ ] JSON export format
- [ ] Binary export format (opsiyonel)

#### 5.3 API Tasarımı
- [ ] Python API docstrings
- [ ] Type hints ekleme
- [ ] Error handling
- [ ] Logging infrastructure
- [ ] Configuration management

### Faz 6: Quality Assurance

#### 6.1 Code Quality
- [ ] `black` formatting
- [ ] `isort` import sorting
- [ ] `ruff` linting
- [ ] `mypy` type checking
- [ ] Pre-commit hooks

#### 6.2 Documentation Quality
- [ ] Sphinx/MkDocs site
- [ ] API reference otomatik üretim
- [ ] Tutorial notebooks
- [ ] Video demo (opsiyonel)

#### 6.3 Security
- [ ] Dependabot alerts
- [ ] Security scanning
- [ ] SAST checks
- [ ] Dependency audit

### Faz 7: Hugging Face Yayını

#### 7.1 Hub Upload
- [ ] Hugging Face CLI kurulumu
- - [ ] Repository oluşturma
- [ ] `huggingface-cli upload` testi
- [ ] Git-LFS büyük dosyalar için
- [ ] Release tagging

#### 7.2 Post-Release
- [ ] Community feedback monitoring
- [ ] Issue triage
- [ ] Bug fix releases
- [ ] Feature requests tracking

## LLM Hafız Review Protocol

### Reviewer Rolleri

Her LLM'e şu rol verilecek:
```
Sen Kuran tecvidi ve fonetik uzmanı bir hafızsın. Tilavet Phonemizer V1'in 
çıktılarını inceleyecek, doğru/yanlış kararları işaretleyecek ve 
iyileştirme önerileri sunacaksın.
```

### Review Format

Her review şunları içermeli:
1. **Doğruluk Kararı**: Doğru/Yanlış/Kararsız
2. **Tecvid Kural Referansı**: Hangi kurala dayanıyor
3. **Öneri**: V1 sembolleriyle düzeltilmiş çıktı
4. **Açıklama**: Neden bu karar

### Dispute Resolution

- 3+ reviewer aynı yönde → Karar kabul
- 2-2 split → Senior hafız (GPT-4) tie-breaker
- Tek review → Manuel review gerekli

### Review Schedule

1. **Batch 1**: Mevcut 35 ayet (seed)
2. **Batch 2**: 50 rastgele ayet
3. **Batch 3**: Huroof muqatta'at özel
4. **Batch 4**: Waqf/PAUSE edge cases
5. **Batch 5**: Cross-ayah connections

## Kritik Başarı Metrikleri

- ✅ Test coverage: %80+
- ✅ LLM reviewer agreement: %85+
- ✅ Quran-wide phonemization: <1 error/1000 phonemes
- ✅ Performance: <100ms/ayet
- ✅ Memory: <100MB for full Quran

## Riskler ve Mitigasyon

| Risk | Olasılık | Etki | Mitigasyon |
|------|----------|------|------------|
| LLM review disagreement | Yüksek | Orta | Senior reviewer tie-breaker |
| Quran-wide errors | Orta | Yüksek | Incremental validation |
| Performance issues | Düşük | Orta | Profiling ve optimizasyon |
| License issues | Düşük | Yüksek | Legal review |
| Hugging Face rejection | Düşük | Orta | Pre-release testing |

## Sonraki Adım

Faz 1.1'den başla: `pyproject.toml` güncelleme.
