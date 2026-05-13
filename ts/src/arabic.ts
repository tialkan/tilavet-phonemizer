// Unicode values for Arabic characters and diacritics

export const FATHA = '\u064E';
export const KASRA = '\u0650';
export const DAMMA = '\u064F';
export const FATHATAN = '\u064B';
export const KASRATAN = '\u064D';
export const DAMMATAN = '\u064C';

export const SHADDA = '\u0651';
export const SUKUN = '\u0652';
export const SMALL_KASRA = '\u06EA';
export const MADDAH = '\u0653';

export const HAMZA = '\u0621';
export const HAMZA_ABOVE = '\u0654';
export const HAMZA_BELOW = '\u0655';
export const ALIF = '\u0627';
export const ALIF_MADDA = '\u0622';
export const ALIF_HAMZA_ABOVE = '\u0623';
export const ALIF_HAMZA_BELOW = '\u0625';
export const ALIF_WASLA = '\u0671';
export const ALIF_MAQSURA = '\u0649';
export const DAGGER_ALIF = '\u0670';

export const WAW = '\u0648';
export const WAW_HAMZA_ABOVE = '\u0624';
export const SMALL_WAW = '\u06E5';

export const YA = '\u064A';
export const YA_HAMZA_ABOVE = '\u0626';
export const SMALL_YA = '\u06E6';

export const TA_MARBUTA = '\u0629';

export const HARAKAT = new Set([
    FATHA, KASRA, DAMMA, FATHATAN, KASRATAN, DAMMATAN, SUKUN, SMALL_KASRA
]);

export const VOWEL_DIACRITICS = new Set([
    FATHA, KASRA, DAMMA, FATHATAN, KASRATAN, DAMMATAN, SMALL_KASRA
]);

// ... Add more Arabic definitions porting from src/tilavet_phonemizer/arabic.py
