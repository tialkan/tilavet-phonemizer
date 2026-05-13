"""Arabic script constants used by the rule-based phonemizer."""

from __future__ import annotations

ALEF = "\u0627"
ALEF_MADDA = "\u0622"
ALEF_HAMZA_ABOVE = "\u0623"
ALEF_HAMZA_BELOW = "\u0625"
ALEF_WASLA = "\u0671"
ALEF_MAQSURA = "\u0649"
HAMZA = "\u0621"
WAW_HAMZA = "\u0624"
YA_HAMZA = "\u0626"

# All bases that carry a hamza glottal stop. Used e.g. to detect madd muttasil
# (long vowel directly followed by a hamza-bearing letter within the same word).
HAMZA_LETTERS = {HAMZA, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, WAW_HAMZA, YA_HAMZA}

# Within-word idgham pairs (Hafs): when the first letter is sakin (orthographically
# bare, no sukun mark, no harakah) and the second has shadda, the first is absorbed.
# Mutamathilain (same letter) is detected by base equality at runtime.
# This set enumerates mutajansayn (same makhraj) and mutaqaribayn (close makhraj).
IDGHAM_HOMORGANIC_PAIRS = {
    # mutajansayn
    ("ت", "ط"), ("ط", "ت"),
    ("ت", "د"), ("د", "ت"),
    ("د", "ط"), ("ط", "د"),
    ("ث", "ذ"), ("ذ", "ث"),
    ("ث", "ظ"), ("ظ", "ث"),
    ("ذ", "ظ"), ("ظ", "ذ"),
    ("ب", "م"),
    # mutaqaribayn
    ("ق", "ك"), ("ك", "ق"),
    ("ل", "ر"),
}

FATHATAN = "\u064b"
DAMMATAN = "\u064c"
KASRATAN = "\u064d"
FATHA = "\u064e"
DAMMA = "\u064f"
KASRA = "\u0650"
SHADDA = "\u0651"
SUKUN = "\u0652"
# Small low kasra (U+06EA) \u2014 used in rare Quranic orthography (e.g.
# \u0645\u064e\u062c\u0652\u0631\u06ea\u0649\u0670\u0647\u064e\u0627). In Hafs reading it functions as a short kasra (i).
SMALL_KASRA = "\u06ea"
MADDAH = "\u0653"
HAMZA_ABOVE = "\u0654"
HAMZA_BELOW = "\u0655"
DAGGER_ALEF = "\u0670"
SMALL_WAW = "\u06e5"
SMALL_YA = "\u06e6"

TATWEEL = "\u0640"
BOM = "\ufeff"

DIACRITICS = {
    FATHATAN,
    DAMMATAN,
    KASRATAN,
    FATHA,
    DAMMA,
    KASRA,
    SHADDA,
    SUKUN,
    MADDAH,
    DAGGER_ALEF,
    HAMZA_ABOVE,
    HAMZA_BELOW,
    "\u0656",
    "\u0657",
    "\u0658",
    "\u0659",
    "\u065a",
    "\u065b",
    "\u065c",
    "\u065d",
    "\u065e",
    "\u065f",
    "\u06d6",
    "\u06d7",
    "\u06d8",
    "\u06d9",
    "\u06da",
    "\u06db",
    "\u06dc",
    "\u06df",
    "\u06e0",
    "\u06e1",
    "\u06e2",
    "\u06e3",
    "\u06e4",
    "\u06e7",
    "\u06e8",
    "\u06ea",
    "\u06eb",
    "\u06ec",
    "\u06ed",
}

STOP_SIGNS = {
    "\u06d5",
    "\u06d6",
    "\u06d7",
    "\u06d8",
    "\u06d9",
    "\u06da",
    "\u06db",
    "\u06dd",
    "\u06de",
    "\u06e9",
    "\u061b",
}

IGNORABLE = {
    BOM,
    TATWEEL,
    "\u06dd",  # end of ayah sign
    "\u06de",
    "\u06e9",
    "\u06ee",
    "\u06ef",
    "\u06fa",
    "\u06fb",
    "\u06fc",
    "\u06ff",
}

ALEF_CARRIERS = {
    ALEF,
    ALEF_MADDA,
    ALEF_HAMZA_ABOVE,
    ALEF_HAMZA_BELOW,
    ALEF_WASLA,
}

SUN_LETTERS = {
    "\u062a",  # ta
    "\u062b",  # tha
    "\u062f",  # dal
    "\u0630",  # dhal
    "\u0631",  # ra
    "\u0632",  # zay
    "\u0633",  # sin
    "\u0634",  # shin
    "\u0635",  # sad
    "\u0636",  # dad
    "\u0637",  # ta emphatic
    "\u0638",  # za emphatic
    "\u0644",  # lam
    "\u0646",  # nun
}

LETTER_TO_SYMBOL = {
    HAMZA: "'",
    ALEF: "'",
    ALEF_MADDA: "'",
    ALEF_HAMZA_ABOVE: "'",
    ALEF_HAMZA_BELOW: "'",
    ALEF_WASLA: "'",
    WAW_HAMZA: "'",
    YA_HAMZA: "'",
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
}

QALQALAH = {"q", "T", "b", "j", "d"}
VOWELS = {"a", "i", "u", "aa", "ii", "uu", "aa4", "ii4", "uu4", "aa6", "ii6", "uu6"}
