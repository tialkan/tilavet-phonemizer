import { describe, it, expect } from 'vitest';
import { Phonemizer } from '../src/phonemizer';

describe('Phonemizer', () => {
    it('should phonemize Basmala in wasl mode', () => {
        const p = new Phonemizer();
        const result = p.phonemize("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ");
        expect(result.text).toBe("b i s m i l l aa h i r r a H m aa n i r r a H ii m i");
    });

    it('should phonemize Basmala with waqf on pause', () => {
        const p = new Phonemizer({ waqf_on_pause: true });
        const result = p.phonemize("ٱلرَّحِيمِ ۝");
        expect(result.text).toBe("' a r r a H ii6 m PAUSE");
    });

    it('should handle Alif Lam Mim (Muqattaat)', () => {
        const p = new Phonemizer();
        const result = p.phonemize("الٓمٓ");
        expect(result.text).toBe("' a l i f l aa6 m_g m ii6 m");
    });

    it('should handle Ikhfa across words', () => {
        const p = new Phonemizer();
        const result = p.phonemize("مِن شَرِّ");
        expect(result.text).toBe("m i n_g sh a r r i");
    });
});
