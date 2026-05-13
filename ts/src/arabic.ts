export const ALEF = "\u0627";
export const ALEF_MADDA = "\u0622";
export const ALEF_HAMZA_ABOVE = "\u0623";
export const ALEF_HAMZA_BELOW = "\u0625";
export const ALEF_WASLA = "\u0671";
export const ALEF_MAQSURA = "\u0649";
export const HAMZA = "\u0621";
export const WAW_HAMZA = "\u0624";
export const YA_HAMZA = "\u0626";

export const HAMZA_LETTERS = new Set([HAMZA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, WAW_HAMZA, YA_HAMZA]);

// Representing pairs as strings formatted like "X,Y" since JS Sets of arrays/objects check by reference.
export const IDGHAM_HOMORGANIC_PAIRS = new Set([
    "ت,ط", "ط,ت",
    "ت,د", "د,ت",
    "د,ط", "ط,د",
    "ث,ذ", "ذ,ث",
    "ث,ظ", "ظ,ث",
    "ذ,ظ", "ظ,ذ",
    "ب,م",
    "ق,ك", "ك,ق",
    "ل,ر"
]);

export const FATHATAN = "\u064b";
export const DAMMATAN = "\u064c";
export const KASRATAN = "\u064d";
export const FATHA = "\u064e";
export const DAMMA = "\u064f";
export const KASRA = "\u0650";
export const SHADDA = "\u0651";
export const SUKUN = "\u0652";
export const SMALL_KASRA = "\u06ea";
export const MADDAH = "\u0653";
export const HAMZA_ABOVE = "\u0654";
export const HAMZA_BELOW = "\u0655";
export const DAGGER_ALEF = "\u0670";
export const SMALL_WAW = "\u06e5";
export const SMALL_YA = "\u06e6";

export const TATWEEL = "\u0640";
export const BOM = "\ufeff";

export const DIACRITICS = new Set([
    FATHATAN, DAMMATAN, KASRATAN,
    FATHA, DAMMA, KASRA,
    SHADDA, SUKUN, MADDAH,
    DAGGER_ALEF, HAMZA_ABOVE, HAMZA_BELOW,
    "\u0656", "\u0657", "\u0658", "\u0659", "\u065a", "\u065b", "\u065c", "\u065d", "\u065e", "\u065f",
    "\u06d6", "\u06d7", "\u06d8", "\u06d9", "\u06da", "\u06db", "\u06dc", "\u06df",
    "\u06e0", "\u06e1", "\u06e2", "\u06e3", "\u06e4", "\u06e7", "\u06e8", "\u06ea", "\u06eb", "\u06ec", "\u06ed"
]);

export const STOP_SIGNS = new Set([
    "\u06d5", "\u06d6", "\u06d7", "\u06d8", "\u06d9", "\u06da", "\u06db", "\u06dd", "\u06de", "\u06e9", "\u061b"
]);

export const IGNORABLE = new Set([
    BOM, TATWEEL, "\u06dd", "\u06de", "\u06e9", "\u06ee", "\u06ef", "\u06fa", "\u06fb", "\u06fc", "\u06ff"
]);

export const ALEF_CARRIERS = new Set([
    ALEF, ALEF_MADDA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, ALEF_WASLA
]);

export const SUN_LETTERS = new Set([
    "\u062a", "\u062b", "\u062f", "\u0630", "\u0631", "\u0632", "\u0633", "\u0634",
    "\u0635", "\u0636", "\u0637", "\u0638", "\u0644", "\u0646"
]);

export const LETTER_TO_SYMBOL: Record<string, string> = {
    [HAMZA]: "'",
    [ALEF]: "'",
    [ALEF_MADDA]: "'",
    [ALEF_HAMZA_ABOVE]: "'",
    [ALEF_HAMZA_BELOW]: "'",
    [ALEF_WASLA]: "'",
    [WAW_HAMZA]: "'",
    [YA_HAMZA]: "'",
    "\u0628": "b",
    "\u062a": "t",
    "\u062b": "th",
    "\u062c": "j",
    "\u062d": "H",
    "\u062e": "kh",
    "\u062f": "d",
    "\u0630": "dh",
    "\u0631": "r",
    "\u0632": "z",
    "\u0633": "s",
    "\u0634": "sh",
    "\u0635": "S",
    "\u0636": "D",
    "\u0637": "T",
    "\u0638": "Z",
    "\u0639": "3",
    "\u063a": "gh",
    "\u0641": "f",
    "\u0642": "q",
    "\u0643": "k",
    "\u0644": "l",
    "\u0645": "m",
    "\u0646": "n",
    "\u0647": "h",
    "\u0629": "h",
    "\u0648": "w",
    "\u064a": "y",
};

export const QALQALAH = new Set(["q", "T", "b", "j", "d"]);
export const VOWELS = new Set(["a", "i", "u", "aa", "ii", "uu", "aa4", "ii4", "uu4", "aa6", "ii6", "uu6"]);
