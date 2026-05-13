# Validation Status Model

## Genel Bakış

Tilavet Phonemizer V1 phoneme sequence'leri için hafız-destekli, sistematik doğrulama süreci.

### Amacı
- 35 ayet validation seed'inin doğruluğu
- LLM hafız (çeşitli başlı yapay zeka modelleri) review'ları
- Multi-reviewer consensus tracking
- Status promote (candidate → gold) karar verme

---

## Veri Modeli

### Yapı

Her ayet `recovered_seed_with_validation.jsonl` dosyasında şu şekildedir:

```json
{
  "ayah": "1:1",
  "label": "Fatiha 1",
  "arabic": "بِسْمِ ٱللَّهِ...",
  "mode": "hafs_wasl_candidate",
  "candidate_v1": "b i s m i l l aa h...",
  "source": "recovered_prompt",
  
  "status": "candidate_v1",
  "reviews": {
    "gpt4": {
      "verdict": "correct",
      "date": "2026-05-12",
      "notes": "Classic Fatiha opening - correct Hafs wasl"
    },
    "claude": {
      "verdict": "correct",
      "date": "2026-05-12"
    }
  },
  "agreement": {
    "total_reviewers": 2,
    "consensus": 2,
    "percent": 100.0,
    "consensus_verdict": "correct"
  }
}
```

### Alanlar

| Alan | Tip | Açıklama |
|------|-----|----------|
| `ayah` | string | Ayet referansı (Sure:Ayet) |
| `label` | string | İnsan okunabilir etiket |
| `arabic` | string | Orijinal Arap metni (Uthmani script) |
| `candidate_v1` | string | V1 fonem sequence (wasl modu) |
| `status` | enum | Doğrulama durumu |
| `reviews` | dict | Reviewer'lar → Verdictler |
| `agreement` | dict | Consensus metrikleri |

### Status Değerleri

```
candidate_v1
├─ Single (or no) LLM review
└─ Ready for promotion when consensus reached

gold_wasl_v1
├─ Multi-LLM consensus ("correct")
└─ Safe for training/deployment in wasl mode

gold_waqf_on_pause_v1
├─ Waqf-variant testing passed
└─ Future: Safe for waqf mode
```

### Verdict Türleri

- **`correct`**: Fonem sequence Hafs/Asim tecvid kurallarına uygun
- **`error`**: Fonem sequence'de hatası var
- **`unsure`**: Reviewer karar veremiyor (cross-ayah wasl, ambiguous case vb.)

---

## Workflow

### 1. Initialization (Yapıldı ✓)

```bash
python3 scripts/init_validation_model.py \
  --seed data/validation/recovered_seed.jsonl \
  --output data/validation/recovered_seed_with_validation.jsonl \
  --summary data/validation/init_summary.md
```

Çıktı:
- `recovered_seed_with_validation.jsonl` - Tüm 35 ayet enriched yapıda
- `init_summary.md` - Initialization raporu

### 2. Reviewer Verdict Toplama

#### CSV Format

Her reviewer'ın verdictleri bir CSV dosyasına yazılır:

**Format:** `data/verdicts_{reviewer}.csv`

```csv
Ayah,Verdict,Date,Notes
1:1,correct,2026-05-12,Classic opening
1:2,unsure,2026-05-12,Cross-ayah wasl case
...
```

#### Review Template

`data/validation/llm_hafiz_review_full.md` dosyası reviewer'lara verilir.

Her ayet için:
```markdown
### 1:1 - Fatiha 1

**Arabic:**
> بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ

**Candidate output:**
```
b i s m i l l aa h i r r a H m aa n i r r a H ii m i
```

**Reviewer feedback:**
```text
Accuracy: yes / no / unsure
Location:
Current:
Expected:
Rule:
Note:
```
```

### 3. Verdict Merge (Yapıldı ✓)

CSV'den JSON'a merge:

```bash
python3 scripts/merge_reviewer_verdicts.py \
  --verdicts data/verdicts_gpt4.csv \
  --reviewer gpt4 \
  --enriched data/validation/recovered_seed_with_validation.jsonl \
  --output data/validation/recovered_seed_with_validation.jsonl
```

Bu işlem:
1. CSV'yi oku
2. Her ayet'in verdict'ini verdicts dict'ine ekle
3. Agreement metrics'i yeniden calculate et
4. JSONL'yi güncelle

### 4. Validation Dashboard

Status'ü takip et:

```bash
python3 scripts/validation_dashboard.py \
  --enriched data/validation/recovered_seed_with_validation.jsonl \
  --output data/validation/dashboard.md \
  --table
```

Dashboard gösterir:
- Status dağılımı (candidate_v1, gold_wasl_v1 vb.)
- Reviewer coverage
- Verdict dağılımı
- Agreement metrics
- Sonraki adımlar

### 5. Status Promotion (Future)

Consensus'a ulaşan ayet'leri promote et:

```bash
python3 scripts/promote_status.py \
  --enriched data/validation/recovered_seed_with_validation.jsonl \
  --from candidate_v1 \
  --to gold_wasl_v1 \
  --min_consensus 3 \
  --output data/validation/recovered_seed_with_validation.jsonl
```

Promotion kuralları:
- Minimum 3 reviewer oyu gerekli
- Hepsi "correct" veya majority oyu
- Hata varsa promote etme

---

## Reviewer Protocol

### LLM Hafız Rolleri

Her reviewer (Claude, GPT-4, Gemini vb.):

```
Sen Kur'an-ı Kerim tilaveti, Hafs an Asim rivayeti, tecvid kuralları
uzman bir hafızsın. Tilavet Phonemizer V1'in çıktılarını inceleyecek,
doğru/yanlış kararları işaretleyeceksin.

NOT: Dini fetva verme amacı yok. Sadece Hafs/Asim tecvid kuralları
açısından teknik doğruluk kontrol edeceksin.
```

### Review Batch'leri

1. **Batch 1** ← Current (35 ayet)
   - Fatiha, çeşitli sure'lar, Muhammadiyyat
   - Temel tecvid kurallarını cover et

2. **Batch 2** (gelecekte)
   - 50 rasgele ayet
   - Coverage genişletme

3. **Batch 3** (gelecekte)
   - Huroof muqatta'at özel
   - Madd variant'ları

4. **Batch 4** (gelecekte)
   - Waqf/PAUSE edge cases

5. **Batch 5** (gelecekte)
   - Cross-ayah connections

### Dispute Resolution

```
Consensus Senaryo:
- 3+ reviewer aynı verdict → Karar kabul
- 2-2 split → Senior reviewer (GPT-4) tie-breaker
- Tek reviewer → Manual kontrol gerekli
```

---

## Senaryo: İlk LLM Batch Tamamlama

### Adım 1: Reviewer'ları Hazırla

Handoff'taki llm_hafiz_review_full.md'yi ilk reviewer'a (GPT-4) gönder:

```bash
cat data/validation/llm_hafiz_review_full.md
# Kopyala, Claude/GPT-4/Gemini'ye gönder
# Reviewer markdownlı template'i doldurur
```

### Adım 2: Review CSV'sini Oluştur

Reviewer'ın markdownl feedback'ini parse edip CSV yap:

```
Ayah,Verdict,Date,Notes
1:1,correct,2026-05-13,...
...
```

### Adım 3: Merge

```bash
python3 scripts/merge_reviewer_verdicts.py \
  --verdicts data/verdicts_gpt4.csv \
  --reviewer gpt4
```

### Adım 4: Check Dashboard

```bash
python3 scripts/validation_dashboard.py --table
```

Çıktı:
```
Reviewer Coverage:
- gpt4: 35 / 35 (100.0%)

Verdict Distribution:
- correct: 33
- unsure: 2
- error: 0

Next Steps:
1. Send batch to Claude / Gemini / Qwen
2. Merge their verdicts
3. Calculate consensus
4. Promote agreed ayahs to gold_wasl_v1
```

---

## Scripts Referansı

| Script | Amaç | Komut |
|--------|------|-------|
| `init_validation_model.py` | Seed enrichment | `python3 scripts/init_validation_model.py` |
| `merge_reviewer_verdicts.py` | CSV→JSON merge | `python3 scripts/merge_reviewer_verdicts.py --verdicts ... --reviewer ...` |
| `validation_dashboard.py` | Status takip | `python3 scripts/validation_dashboard.py --table` |
| `promote_status.py` | Consensus→gold | `python3 scripts/promote_status.py --min_consensus 3` (TBD) |

---

## Gelecek Adımlar

1. **Claude Review**
   - Handoff kopyasını Claude'a gönder
   - CSV çıkış bekle

2. **Gemini / Qwen Review**
   - Multi-LLM consensus hedefi

3. **Error Triage**
   - 2-2 split ayahs → Senior reviewer kontrol

4. **Status Promotion**
   - gold_wasl_v1'e promote (consensus ayahs)

5. **Waqf Variant**
   - PAUSE → fonetik waqf kuralları

---

## Notlar

- `recovered_seed.jsonl` orijinal kalır
- `recovered_seed_with_validation.jsonl` aktif validation file
- CSV'ler `data/verdicts_{reviewer}.csv` formatında
- Dashboard'u sık kontrol et: `python3 scripts/validation_dashboard.py --table`
