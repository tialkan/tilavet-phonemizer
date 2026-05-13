"""A small, testable Quran phonemizer core.

This is intentionally conservative. It captures the repeatable V1 rules and
leaves advanced qira'at edge cases to validation-backed iterations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Optional

from .arabic import (
    ALEF,
    ALEF_MADDA,
    ALEF_MAQSURA,
    ALEF_WASLA,
    DAGGER_ALEF,
    DAMMA,
    DAMMATAN,
    DIACRITICS,
    FATHA,
    FATHATAN,
    HAMZA_ABOVE,
    HAMZA_BELOW,
    HAMZA_LETTERS,
    IDGHAM_HOMORGANIC_PAIRS,
    IGNORABLE,
    KASRA,
    KASRATAN,
    LETTER_TO_SYMBOL,
    MADDAH,
    QALQALAH,
    SHADDA,
    SMALL_KASRA,
    SMALL_WAW,
    SMALL_YA,
    STOP_SIGNS,
    SUKUN,
    SUN_LETTERS,
    VOWELS,
)


@dataclass(frozen=True)
class ArabicChar:
    base: str
    marks: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuleHit:
    symbol_index: int
    symbol: str
    rule: str
    source: str


@dataclass(frozen=True)
class WordSpan:
    token: str
    start: int
    end: int


@dataclass
class PhonemizationResult:
    symbols: list[str]
    rules: list[RuleHit] = field(default_factory=list)
    words: list[WordSpan] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(symbol for symbol in self.symbols if symbol)


@dataclass
class PhonemizerConfig:
    start_of_utterance: bool = True
    wasl: bool = True
    emit_pause: bool = True
    waqf_on_pause: bool = False
    cross_ayah_wasl: bool = False


@dataclass
class _State:
    at_utterance_start: bool
    previous_vowel: Optional[str] = None
    pending_noon_index: Optional[int] = None
    pending_mim_index: Optional[int] = None
    after_pause: bool = False


class Phonemizer:
    """Rule-based V1 seed phonemizer for Hafs-style Quran text."""

    _word_re = re.compile(r"\s+")
    _izhar = {"'", "h", "3", "H", "gh", "kh"}
    _idgham_ghunna = {"y", "n", "m", "w"}
    _idgham_no_ghunna = {"l", "r", "L"}
    _ikhfa = {"t", "th", "j", "d", "dh", "z", "s", "sh", "S", "D", "T", "Z", "f", "q", "k"}

    def __init__(self, config: Optional[PhonemizerConfig] = None) -> None:
        self.config = config or PhonemizerConfig()

    def phonemize(self, text: str) -> PhonemizationResult:
        state = _State(at_utterance_start=self.config.start_of_utterance)
        symbols: list[str] = []
        rules: list[RuleHit] = []
        words: list[WordSpan] = []

        for raw_token in self._tokens(text):
            if self._is_pause_token(raw_token):
                if self.config.emit_pause:
                    # Mushaf optional-pause markers (ۖ ۚ ۛ ۗ) are advisory: in
                    # wasl reading the reciter does not actually stop, so cross-
                    # word assimilation (ihfa, idgham, iqlab) must still apply.
                    # Therefore we KEEP `state.pending_noon_index` so the next
                    # word can resolve it. Only in waqf_on_pause mode do we
                    # finalise the noon as izhar at the pause boundary.
                    if self.config.waqf_on_pause:
                        self._resolve_pending_noon(state, None, symbols, rules, raw_token)
                        if words:
                            self._apply_waqf_transformations(symbols, rules, words[-1], raw_token)
                    if not self.config.cross_ayah_wasl:
                        symbols.append("PAUSE")
                        rules.append(RuleHit(len(symbols) - 1, "PAUSE", "pause_mark", raw_token))
                        state.after_pause = True
                continue

            word_symbols, word_rules = self._phonemize_word(raw_token, state)
            if not word_symbols:
                continue

            self._resolve_pending_noon(
                state, self._first_consonant(word_symbols), symbols, rules, raw_token
            )
            self._coalesce_leading_geminate_after(symbols, word_symbols, word_rules, "m_g", "m")
            self._resolve_pending_mim(state, word_symbols, word_rules, symbols, rules, raw_token)
            # Upgrade silah sughra to kubra if current word starts with hamza
            self._upgrade_silah_before_hamza(symbols, rules, word_symbols, raw_token)
            if not (self.config.waqf_on_pause and state.after_pause):
                self._apply_iltiqa_sakinayn(symbols, rules, raw_token)
            state.after_pause = False

            start = len(symbols)
            symbols.extend(word_symbols)
            for hit in word_rules:
                rules.append(
                    RuleHit(
                        symbol_index=start + hit.symbol_index,
                        symbol=hit.symbol,
                        rule=hit.rule,
                        source=hit.source,
                    )
                )
            end = len(symbols)
            words.append(WordSpan(raw_token, start, end))

            state.pending_noon_index = self._pending_noon_index_from_rules(
                rules, symbols, start, end
            )
            state.pending_mim_index = self._pending_mim_index_from_rules(rules, symbols, start, end)
            state.previous_vowel = self._last_vowel(symbols)
            state.at_utterance_start = False

        self._resolve_pending_noon(state, None, symbols, rules, "")
        return PhonemizationResult(symbols=symbols, rules=rules, words=words)

    def _tokens(self, text: str) -> Iterable[str]:
        for token in self._word_re.split(text.strip()):
            if not token:
                continue
            pause_parts = self._split_pause_marks(token)
            yield from pause_parts

    def _split_pause_marks(self, token: str) -> list[str]:
        parts: list[str] = []
        current: list[str] = []
        for char in token:
            if char in STOP_SIGNS:
                if current:
                    parts.append("".join(current))
                    current = []
                parts.append(char)
            else:
                current.append(char)
        if current:
            parts.append("".join(current))
        return parts

    def _is_pause_token(self, token: str) -> bool:
        return bool(token) and all(char in STOP_SIGNS for char in token)

    def _phonemize_word(self, token: str, state: _State) -> tuple[list[str], list[RuleHit]]:
        clusters = self._cluster(token)
        if not clusters:
            return [], []

        muqattaat = self._try_muqattaat(clusters, token)
        if muqattaat is not None:
            return muqattaat

        allah = self._try_allah(clusters, state, token)
        if allah is not None:
            return allah

        out: list[str] = []
        rules: list[RuleHit] = []
        index = 0

        prefixed_article_start = self._prefixed_article_start(clusters)
        prefixed_dropped = self._prefixed_dropped_article_start(clusters)
        if prefixed_article_start is not None:
            index = self._emit_cluster(clusters, 0, token, out, rules)
            local_state = _State(at_utterance_start=False, previous_vowel=self._last_vowel(out))
            index = self._emit_article(
                clusters, prefixed_article_start, local_state, token, out, rules
            )
        elif prefixed_dropped is not None:
            # li-prefix + bare article lam (no alif). Emit li-prefix as a regular
            # cluster, then handle the bare article lam (lam shamsiyya/qamariyya)
            # using the same logic as _emit_article, just without the leading
            # alif-wasla cluster.
            index = self._emit_cluster(clusters, 0, token, out, rules)
            index = self._emit_bare_article_lam(
                clusters, prefixed_dropped, token, out, rules
            )
        elif self._prefixed_wasla_start(clusters) is not None:
            index = self._emit_cluster(clusters, 0, token, out, rules)
            index = 2
        else:
            article_start = self._article_start(clusters)
            if article_start is not None:
                index = self._emit_article(clusters, article_start, state, token, out, rules)
            elif clusters[0].base == ALEF_WASLA:
                index = self._emit_initial_wasla(clusters, state, token, out, rules)

        while index < len(clusters):
            index = self._emit_cluster(clusters, index, token, out, rules)

        self._resolve_noon_within_word(out, rules, token)
        return out, rules

    def _cluster(self, token: str) -> list[ArabicChar]:
        clusters: list[ArabicChar] = []
        for char in token:
            if char in {SMALL_WAW, SMALL_YA}:
                if clusters:
                    previous = clusters[-1]
                    clusters[-1] = ArabicChar(previous.base, previous.marks + (char,))
                continue
            if char in IGNORABLE:
                continue
            if char in DIACRITICS:
                if clusters:
                    previous = clusters[-1]
                    clusters[-1] = ArabicChar(previous.base, previous.marks + (char,))
                continue
            if char in STOP_SIGNS or char.isspace():
                continue
            clusters.append(ArabicChar(char, ()))
        return clusters

    def _skeleton(self, clusters: list[ArabicChar]) -> str:
        return "".join(cluster.base for cluster in clusters if cluster.base not in IGNORABLE)

    # Muqattaat letter name pronunciations
    # Format: (phonemes, madd_vowel_index, madd_vowel)
    # madd_vowel: "a" -> aa6, "i" -> ii6, "u" -> uu6
    # The base form uses madd tabii (aa, ii, uu) for characteristic vowel.
    # When maddah is present, upgrade to madd lazim (aa6, ii6, uu6).
    _MUQATTAT_NAMES: dict[str, tuple[list[str], int, str]] = {
        # Alif: alif - characteristic vowel is 'i' (kasra), not doubled
        "ا": (["'", "a", "l", "i", "f"], 3, "i"),
        # Lam: laam - characteristic vowel 'aa' (madd tabii)
        "ل": (["l", "aa", "m"], 1, "a"),
        # Mim: miim - characteristic vowel 'ii' (madd tabii)
        "م": (["m", "ii", "m"], 1, "i"),
        # Ya: yaa - characteristic vowel 'aa' (madd tabii)
        "ي": (["y", "aa"], 1, "a"),
        # Sin: siin - characteristic vowel 'ii' (madd tabii)
        "س": (["s", "ii", "n"], 1, "i"),
        # Kaf: kaaf - characteristic vowel 'aa' (madd tabii)
        "ك": (["k", "aa", "f"], 1, "a"),
        # Ha: haa - characteristic vowel 'aa' (madd tabii)
        "ه": (["h", "aa"], 1, "a"),
        # Ayn: ayn - characteristic vowel 'a', not doubled
        "ع": (["3", "a", "y", "n"], 1, "a"),
        # Sad: saad - characteristic vowel 'aa' (madd tabii)
        "ص": (["S", "aa", "d"], 1, "a"),
        # Ta: taa - characteristic vowel 'aa' (madd tabii)
        "ط": (["T", "aa"], 1, "a"),
        # Ha (throat): haa - characteristic vowel 'aa' (madd tabii)
        "ح": (["H", "aa"], 1, "a"),
        # Nun: nuun - characteristic vowel 'uu' (madd tabii)
        "ن": (["n", "uu", "n"], 1, "u"),
        # Qaf: qaaf - characteristic vowel 'aa' (madd tabii)
        "ق": (["q", "aa", "f"], 1, "a"),
        # Ra: raa - characteristic vowel 'aa' (madd tabii)
        "ر": (["r", "aa"], 1, "a"),
    }

    # Known muqattaat skeleton patterns in the Quran
    _MUQATTAT_SKELETONS: set[str] = {
        "الم", "المص", "المر", "كهيعص", "طه", "طسم", "طس",
        "يس", "ص", "حم", "حمعسق", "عسق", "ق", "ن",
    }

    def _try_muqattaat(
        self,
        clusters: list[ArabicChar],
        token: str,
    ) -> Optional[tuple[list[str], list[RuleHit]]]:
        skeleton = self._skeleton(clusters)
        # Match against curated muqattaat skeletons. The presence of MADDAH on
        # individual letters decides whether each letter's characteristic vowel
        # becomes madd lazim (`aa6/ii6/uu6`) or stays madd tabii (`aa/ii/uu`).
        # Letters without MADDAH (e.g. طه) still need expansion to their letter
        # names rather than being read as a regular word.
        if skeleton not in self._MUQATTAT_SKELETONS:
            return None

        # Check if all letters are known muqattaat
        for cluster in clusters:
            if cluster.base not in self._MUQATTAT_NAMES:
                return None

        # Build phonemes dynamically based on maddah presence
        out: list[str] = []
        rules: list[RuleHit] = []

        for cluster in clusters:
            name_phonemes, madd_idx, madd_vowel = self._MUQATTAT_NAMES[cluster.base]
            has_madd = MADDAH in cluster.marks

            if has_madd and madd_idx < len(name_phonemes):
                # Replace the characteristic vowel with madd lazim
                for i, ph in enumerate(name_phonemes):
                    if i == madd_idx:
                        # Apply madd lazim based on vowel type
                        if madd_vowel == "a":
                            out.append("aa6")
                        elif madd_vowel == "i":
                            out.append("ii6")
                        elif madd_vowel == "u":
                            out.append("uu6")
                        else:
                            out.append(ph)
                    else:
                        out.append(ph)
            else:
                out.extend(name_phonemes)

        # Apply within-muqattaat ikhfa/idgham at the seams between letter names:
        # - trailing `n` (e.g. end of ع="3 a y n") + ikhfa or ghunna consonant → n_g
        # - trailing `m` + `m` (lam's final mim → mim's initial mim) → m_g (idgham
        #   shafawi mim ghunna)
        idgham_ghunna = {"y", "n", "m", "w"}
        for i in range(len(out) - 1):
            sym = out[i]
            nxt = out[i + 1]
            if sym == "n" and (nxt in self._ikhfa or nxt in idgham_ghunna):
                out[i] = "n_g"
            elif sym == "m" and nxt == "m":
                out[i] = "m_g"

        rules = [
            RuleHit(index, symbol, "huroof_muqattaat", token)
            for index, symbol in enumerate(out)
        ]
        return out, rules

    def _try_allah(
        self,
        clusters: list[ArabicChar],
        state: _State,
        token: str,
    ) -> Optional[tuple[list[str], list[RuleHit]]]:
        skeleton = self._skeleton(clusters)
        if skeleton in {"الله", "ٱلله"}:
            out: list[str] = []
            rules: list[RuleHit] = []
            if state.at_utterance_start:
                self._emit(out, rules, "'", "alif_wasla_initial", token)
                self._emit(out, rules, "a", "allah_initial_vowel", token)
                lam = "L"
            else:
                lam = self._allah_lam_symbol(state.previous_vowel)
            self._emit_allah_core(clusters, lam, token, out, rules)
            return out, rules

        if skeleton == "لله":
            out = []
            rules = []
            prefix = clusters[0]
            self._emit(out, rules, "l", "li_prefix", token)
            self._emit_short_vowel(prefix.marks, token, out, rules)
            self._emit_allah_core(clusters[1:], "l", token, out, rules)
            return out, rules

        return None

    def _allah_lam_symbol(self, previous_vowel: Optional[str]) -> str:
        # Tafkhim (L) when the preceding vowel family is fatha or damma.
        # Tarqiq (l) when it is kasra. The full set covers short, tabii, and
        # extended (4/6 harakah) madd variants.
        if previous_vowel in {
            "a", "aa", "aa4", "aa6",
            "u", "uu", "uu4", "uu6",
        }:
            return "L"
        return "l"

    def _emit_allah_core(
        self,
        clusters: list[ArabicChar],
        lam_symbol: str,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> None:
        self._emit(out, rules, lam_symbol, "lam_allah", token)
        self._emit(out, rules, lam_symbol, "lam_allah_shadda", token)
        self._emit(out, rules, "aa", "allah_madd", token)
        self._emit(out, rules, "h", "letter", token)

        final_marks = clusters[-1].marks if clusters else ()
        self._emit_short_vowel(final_marks, token, out, rules)

    def _article_start(self, clusters: list[ArabicChar]) -> Optional[int]:
        if (
            len(clusters) >= 2
            and clusters[0].base in {ALEF_WASLA, ALEF}
            and clusters[1].base == "ل"
        ):
            return 0
        return None

    def _prefixed_article_start(self, clusters: list[ArabicChar]) -> Optional[int]:
        if (
            len(clusters) >= 3
            and clusters[0].base in {"و", "ف", "ب", "ك"}
            and clusters[1].base in {ALEF_WASLA, ALEF}
            and clusters[2].base == "ل"
        ):
            return 1
        return None

    def _prefixed_wasla_start(self, clusters: list[ArabicChar]) -> Optional[int]:
        if (
            len(clusters) >= 2
            and clusters[0].base in {"و", "ف", "ب", "ك"}
            and clusters[1].base == ALEF_WASLA
        ):
            return 1
        return None

    def _prefixed_dropped_article_start(self, clusters: list[ArabicChar]) -> Optional[int]:
        """li-prefix + bare article lam (article alif dropped in writing).
        Example: لِلنَّاسِ = li- + al-naas, where the article ا drops orthographically.
        Returns index of the article lam (the second ل), or None.
        Excludes the Allah form (shadda on article lam) which is handled separately."""
        if (
            len(clusters) >= 3
            and clusters[0].base == "ل"
            and self._has_vowel(clusters[0].marks)
            and clusters[1].base == "ل"
            and not self._has_vowel(clusters[1].marks)
            and SHADDA not in clusters[1].marks
        ):
            return 1
        return None

    def _emit_article(
        self,
        clusters: list[ArabicChar],
        start: int,
        state: _State,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> int:
        next_index = start + 2
        if next_index >= len(clusters):
            return next_index

        if state.at_utterance_start:
            self._emit(out, rules, "'", "alif_wasla_initial", token)
            self._emit(out, rules, "a", "alif_wasla_initial_vowel", token)

        article_lam = clusters[start + 1]
        if SHADDA in article_lam.marks:
            self._emit(out, rules, "l", "article_lam_shadda", token)
            self._emit(out, rules, "l", "article_lam_shadda", token)
            self._emit_short_vowel(article_lam.marks, token, out, rules)
            return next_index

        # Detect Allah-form reached via prefix/wasla:
        #   ...ٱ + ل(bare) + ل(SHADDA+FATHA) + ه(harakah)
        # The article lam is bare (already handled as shamsiyya-elided into the
        # Allah lam below), the next cluster is lam-with-shadda-fatha, and the
        # one after is the ha. We delegate to the Allah core so that the
        # implicit dagger alif (`aa`) and tafkhim/tarqiq lam are correct.
        if (
            next_index + 1 < len(clusters)
            and clusters[next_index].base == "ل"
            and SHADDA in clusters[next_index].marks
            and FATHA in clusters[next_index].marks
            and clusters[next_index + 1].base == "ه"
        ):
            lam_sym = self._allah_lam_symbol(self._last_vowel(out) or state.previous_vowel)
            # The article lam is silently merged into the Allah lam (shamsiyya-like).
            rules.append(RuleHit(len(out), "", "lam_shamsiyya_elided", token))
            self._emit_allah_core(clusters[next_index:], lam_sym, token, out, rules)
            return next_index + 2

        next_base = clusters[next_index].base
        if next_base not in SUN_LETTERS:
            self._emit(out, rules, "l", "lam_qamariyya", token)
        else:
            rules.append(RuleHit(len(out), "", "lam_shamsiyya_elided", token))
        # If the article lam carries a movement vowel (iltiqa al-sakinayn case,
        # e.g. ٱلِٱسْمُ where lam takes kasra), emit it.
        if self._has_vowel(article_lam.marks):
            self._emit_short_vowel(article_lam.marks, token, out, rules)
        return next_index

    def _emit_bare_article_lam(
        self,
        clusters: list[ArabicChar],
        article_idx: int,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> int:
        """Emit a bare article lam (no preceding alif-wasla, i.e. orthographically
        dropped after a li-prefix, or following an alif-madda in madd-i farq
        forms like ءَآللَّهُ)."""
        next_index = article_idx + 1
        if next_index >= len(clusters):
            return next_index

        # Allah-form detection: bare article lam directly followed by
        # ل(SHADDA+FATHA) + ه(harakah) is the lafzatullah pattern. Delegate to
        # the Allah core so tafkhim/tarqiq and the dagger alif are correct.
        if (
            next_index + 1 < len(clusters)
            and clusters[next_index].base == "ل"
            and SHADDA in clusters[next_index].marks
            and FATHA in clusters[next_index].marks
            and clusters[next_index + 1].base == "ه"
        ):
            lam_sym = self._allah_lam_symbol(self._last_vowel(out))
            rules.append(RuleHit(len(out), "", "lam_shamsiyya_elided", token))
            self._emit_allah_core(clusters[next_index:], lam_sym, token, out, rules)
            return next_index + 2

        article_lam = clusters[article_idx]
        next_base = clusters[next_index].base
        if next_base not in SUN_LETTERS:
            self._emit(out, rules, "l", "lam_qamariyya", token)
        else:
            rules.append(RuleHit(len(out), "", "lam_shamsiyya_elided", token))
        # If article lam has a movement vowel, emit it (rare; lam usually has sukun).
        if self._has_vowel(article_lam.marks):
            self._emit_short_vowel(article_lam.marks, token, out, rules)
        return next_index

    def _emit_initial_wasla(
        self,
        clusters: list[ArabicChar],
        state: _State,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> int:
        if state.at_utterance_start:
            self._emit(out, rules, "'", "alif_wasla_initial", token)
            self._emit(
                out, rules, self._guess_wasla_vowel(clusters), "alif_wasla_initial_vowel", token
            )
        return 1

    def _guess_wasla_vowel(self, clusters: list[ArabicChar]) -> str:
        for cluster in clusters[1:4]:
            if DAMMA in cluster.marks:
                return "u"
        return "i"

    def _emit_cluster(
        self,
        clusters: list[ArabicChar],
        index: int,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> int:
        cluster = clusters[index]
        base = cluster.base

        # Internal alif-wasla (any position ≥ 1): drops in wasl mode.
        # If followed by article lam, dispatch to article handler so that
        # lam shamsiyya/qamariyya and Allah forms are handled correctly even
        # after multi-consonant prefixes (e.g. وَبِٱللَّهِ, تَٱللَّهِ, أَبِٱلْكِتَابِ).
        if base == ALEF_WASLA and index >= 1:
            if index + 1 < len(clusters) and clusters[index + 1].base == "ل":
                local_state = _State(
                    at_utterance_start=False,
                    previous_vowel=self._last_vowel(out),
                )
                return self._emit_article(clusters, index, local_state, token, out, rules)
            # No article follows: alif-wasla is silent in wasl, just skip
            return index + 1

        # Bare article lam after a li-prefix (orthographic alif-drop).
        # Pattern: ...ل(vowel)ل(no-vowel,no-shadda)X → li- + article-lam-elided + X.
        # Handles وَلِلرِّجَالِ, فَلِلذَّكَرِ etc. without needing a dedicated dispatch.
        if (
            base == "ل"
            and index >= 1
            and not self._has_vowel(cluster.marks)
            and SHADDA not in cluster.marks
            and clusters[index - 1].base == "ل"
            and self._has_vowel(clusters[index - 1].marks)
        ):
            return self._emit_bare_article_lam(clusters, index, token, out, rules)

        # Within-word idgham (mutamathilain / mutajansayn / mutaqaribayn).
        # Orthographic signal: current letter is bare (no marks at all -- no
        # harakah, no sukun, no shadda) and the next letter carries shadda.
        # The current consonant is absorbed into the next.
        # Examples: أَرَدتُّمْ (د+ت), يُدْرِككُّمُ (ك+ك), نَخْلُقكُّم (ق+ك).
        if (
            index >= 1
            and not cluster.marks  # truly bare cluster
            and index + 1 < len(clusters)
            and SHADDA in clusters[index + 1].marks
            and self._is_idgham_pair(base, clusters[index + 1].base)
        ):
            rules.append(RuleHit(len(out), "", "idgham_within_word", token))
            return index + 1

        if base == ALEF_MADDA:
            next_cluster = clusters[index + 1] if index + 1 < len(clusters) else None
            # Detect madd-i farq: alif-madda + bare article lam + shadda-bearing
            # letter (e.g. ءَآلذَّكَرَيْنِ, ءَآللَّهُ). In this rare form, the
            # alif-madda is elongated to 6 harakah, the article lam is silent
            # (shamsiyya elision OR the Allah-lam absorbs it), and the next
            # shadda-bearing letter is read with its doubling.
            is_farq = (
                next_cluster
                and next_cluster.base == "ل"
                and not self._has_vowel(next_cluster.marks)
                and SHADDA not in next_cluster.marks
                and index + 2 < len(clusters)
                and SHADDA in clusters[index + 2].marks
            )
            # Detect madd-i lazim kalimi mukhaffaf: alif-madda + lam(SUKUN).
            # Only two instances in the Quran: ءَآلْـَٰٔنَ (10:51, 10:91).
            is_lazim_mukhaffaf = (
                not is_farq
                and next_cluster is not None
                and next_cluster.base == "ل"
                and SUKUN in next_cluster.marks
            )
            # Determine the madd category from what follows.
            if is_farq:
                madd_sym, madd_rule = "aa6", "madd_farq"
            elif is_lazim_mukhaffaf:
                madd_sym, madd_rule = "aa6", "madd_lazim_kalimi_mukhaffaf"
            elif next_cluster and SHADDA in next_cluster.marks:
                madd_sym, madd_rule = "aa6", "madd_lazim"
            elif next_cluster and next_cluster.base in HAMZA_LETTERS:
                madd_sym, madd_rule = "aa4", "madd_muttasil"
            elif index == 0:
                madd_sym, madd_rule = "aa", "madd_badl"
            else:
                madd_sym, madd_rule = "aa", "madd_tabii"

            if index == 0:
                self._emit(out, rules, "'", "hamza", token)
                self._emit(out, rules, madd_sym, madd_rule, token)
            else:
                self._upgrade_previous_vowel(out, rules, madd_sym, madd_rule, token, drop_preceding_hamza=True)

            # In the madd-i farq case, delegate the silent article lam (and the
            # potential Allah-form that follows it) to the bare-article handler.
            if is_farq:
                return self._emit_bare_article_lam(clusters, index + 1, token, out, rules)
            return index + 1

        if base == "و" and DAGGER_ALEF in cluster.marks and not self._has_vowel(cluster.marks):
            self._upgrade_previous_vowel(out, rules, "aa", "waw_dagger_alef_carrier", token)
            return index + 1

        if self._is_long_vowel_carrier(clusters, index):
            return index + 1

        symbol = self._symbol_for_cluster(cluster)
        if symbol is None:
            return index + 1

        if symbol == "n" and self._is_sakin_like(cluster.marks):
            self._emit(out, rules, "n", "noon_sakin", token)
            # Tatweel-hamze pattern: sakin noon followed by a hamza-on-tatweel
            # attached to the same cluster (e.g. وَيَنْـَٔوْنَ). Emit the hamza
            # and its vowel after the sakin noon.
            if self._has_hamza_mark(cluster.marks):
                return self._emit_trailing_hamza(clusters, index, token, out, rules)
            return index + 1

        if symbol == "m" and self._is_sakin_like(cluster.marks):
            self._emit(out, rules, "m", "mim_sakin", token)
            if self._has_hamza_mark(cluster.marks):
                return self._emit_trailing_hamza(clusters, index, token, out, rules)
            return index + 1

        if SUKUN in cluster.marks and symbol in QALQALAH:
            self._emit(out, rules, f"{symbol}_qal", "qalqalah", token)
            return index + 1

        if SHADDA in cluster.marks:
            self._emit(out, rules, symbol, "shadda", token)
            self._emit(out, rules, symbol, "shadda", token)
        else:
            self._emit(out, rules, symbol, "letter", token)

        if self._has_hamza_mark(cluster.marks):
            return self._emit_carrier_hamza(clusters, index, token, out, rules)

        return self._emit_vowel_and_madd(clusters, index, token, out, rules)

    def _symbol_for_cluster(self, cluster: ArabicChar) -> Optional[str]:
        if cluster.base == "ة":
            return "t" if self.config.wasl else "h"
        if cluster.base == ALEF_MAQSURA:
            return (
                "y"
                if SUKUN in cluster.marks
                or SHADDA in cluster.marks
                or self._has_vowel(cluster.marks)
                else None
            )
        return LETTER_TO_SYMBOL.get(cluster.base)

    def _is_long_vowel_carrier(self, clusters: list[ArabicChar], index: int) -> bool:
        if index == 0:
            return False
        base = clusters[index].base
        marks = clusters[index].marks
        if base == ALEF and not self._has_hamza_mark(marks):
            return True
        if (
            base == ALEF_MAQSURA
            and SUKUN not in marks
            and self._is_plain_madd_letter(clusters[index])
            and MADDAH not in marks
        ):
            return True
        previous_marks = clusters[index - 1].marks
        if base == "و" and DAMMA in previous_marks and self._is_plain_madd_letter(clusters[index]):
            return True
        if base == "ي" and KASRA in previous_marks and self._is_plain_madd_letter(clusters[index]):
            return True
        return False

    def _emit_vowel_and_madd(
        self,
        clusters: list[ArabicChar],
        index: int,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> int:
        cluster = clusters[index]
        marks = cluster.marks
        next_cluster = clusters[index + 1] if index + 1 < len(clusters) else None

        if cluster.base == "ه" and SMALL_WAW in marks:
            self._emit(out, rules, "uu4" if MADDAH in marks else "uu", "madd_silah", token)
            return index + 1
        if cluster.base == "ه" and SMALL_YA in marks:
            self._emit(out, rules, "ii4" if MADDAH in marks else "ii", "madd_silah", token)
            return index + 1

        if FATHATAN in marks:
            self._emit(out, rules, "a", "tanwin", token)
            self._emit(out, rules, "n", "tanwin_n", token)
            return index + 1
        if DAMMATAN in marks:
            self._emit(out, rules, "u", "tanwin", token)
            self._emit(out, rules, "n", "tanwin_n", token)
            return index + 1
        if KASRATAN in marks:
            self._emit(out, rules, "i", "tanwin", token)
            self._emit(out, rules, "n", "tanwin_n", token)
            return index + 1

        if FATHA in marks and DAGGER_ALEF in marks:
            if MADDAH in marks:
                self._emit(out, rules, "aa4", "small_alef_madd_muttasil", token)
            else:
                self._emit(out, rules, "aa", "small_alef_madd_tabii", token)
            return index + 1

        if (
            FATHA in marks
            and next_cluster is not None
            and (
                next_cluster.base == ALEF
                or (
                    next_cluster.base == ALEF_MAQSURA
                    and SUKUN not in next_cluster.marks
                    and self._is_plain_madd_letter(next_cluster)
                    and MADDAH not in next_cluster.marks
                )
            )
        ):
            if MADDAH in next_cluster.marks:
                if index + 2 < len(clusters) and SHADDA in clusters[index + 2].marks:
                    self._emit(out, rules, "aa6", "madd_lazim", token)
                elif (
                    # Madd-i farq: FATHA + ALEF(MADDAH) + bare article lam + SHADDA letter
                    # e.g. ءَآلذَّكَرَيْنِ, ءَآللَّهُ
                    index + 3 < len(clusters)
                    and clusters[index + 2].base == "ل"
                    and not self._has_vowel(clusters[index + 2].marks)
                    and SHADDA not in clusters[index + 2].marks
                    and SHADDA in clusters[index + 3].marks
                ):
                    self._emit(out, rules, "aa6", "madd_farq", token)
                    # Delegate the silent article lam (incl. Allah-form) to the
                    # bare-article handler, then continue from after it.
                    return self._emit_bare_article_lam(clusters, index + 2, token, out, rules)
                elif (
                    # Madd-i lazim kalimi mukhaffaf: FATHA + ALEF(MADDAH) + lam(SUKUN)
                    # The article lam carries a sukun (no shadda elsewhere). Only
                    # known instances in the Quran are ءَآلْـَٰٔنَ (10:51, 10:91).
                    index + 2 < len(clusters)
                    and clusters[index + 2].base == "ل"
                    and SUKUN in clusters[index + 2].marks
                ):
                    self._emit(out, rules, "aa6", "madd_lazim_kalimi_mukhaffaf", token)
                else:
                    self._emit(out, rules, "aa4", "madd_muttasil_or_munfasil", token)
            else:
                self._emit(out, rules, "aa", "madd_tabii", token)
            return index + 2

        if (
            KASRA in marks
            and next_cluster is not None
            and next_cluster.base in {"ي", ALEF_MAQSURA}
            and self._is_plain_madd_letter(next_cluster)
        ):
            if MADDAH in next_cluster.marks:
                self._emit(out, rules, "ii4", "madd_munfasil_or_silah", token)
            else:
                self._emit(out, rules, "ii", "madd_tabii", token)
            return index + 2

        if (
            DAMMA in marks
            and next_cluster is not None
            and next_cluster.base == "و"
            and self._is_plain_madd_letter(next_cluster)
        ):
            self._emit(
                out, rules, "uu4" if MADDAH in next_cluster.marks else "uu", "madd_tabii", token
            )
            return index + 2

        self._emit_short_vowel(marks, token, out, rules)

        if DAGGER_ALEF in marks:
            self._emit(out, rules, "aa", "small_alef_madd_tabii", token)

        return index + 1

    def _emit_carrier_hamza(
        self,
        clusters: list[ArabicChar],
        index: int,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> int:
        """Handle a consonant cluster that carries a hamza diacritic (HAMZA_ABOVE
        or HAMZA_BELOW). The cluster's `marks` may encode TWO segments:

          1. the consonant's own harakah, then
          2. the hamza's harakah (or SUKUN, indicating a sakin hamza).

        Examples (mark sequence → expected emission):
          (FATHA, DAMMA, HAMZA_ABOVE)  -- يَـُٔ pattern: ' a + ' + u/uu
          (FATHA, SUKUN, HAMZA_ABOVE)  -- ـَْٔ pattern : a + ' (sakin hamza)
          (FATHA, FATHA, HAMZA_ABOVE)  -- ـَـَٔ pattern: a + ' + a
          (FATHA, HAMZA_ABOVE)         -- ـَٔ single  : ' + a
        """
        cluster = clusters[index]
        marks = cluster.marks
        next_cluster = clusters[index + 1] if index + 1 < len(clusters) else None

        # Walk marks in source order, capturing the consonant's harakah and the
        # hamza's harakah/tanwin (and whether the hamza is sakin) separately.
        # SHADDA and the hamza mark itself are skipped here (SHADDA was emitted
        # as the doubling pair before this method ran).
        consonant_harakat = None  # FATHA/KASRA/DAMMA/SUKUN/None
        hamza_harakat = None       # FATHA/KASRA/DAMMA/None
        hamza_tanwin = None        # FATHATAN/DAMMATAN/KASRATAN/None
        hamza_sakin = False
        seen_first = False
        for m in marks:
            if m in (HAMZA_ABOVE, HAMZA_BELOW, SHADDA):
                continue
            if not seen_first:
                consonant_harakat = m
                seen_first = True
            else:
                if m == SUKUN:
                    hamza_sakin = True
                elif m in (FATHA, KASRA, DAMMA):
                    hamza_harakat = m
                elif m in (FATHATAN, DAMMATAN, KASRATAN):
                    hamza_tanwin = m

        # If only one mark and it is SUKUN, treat hamza as sakin (no pre-vowel).
        if seen_first and consonant_harakat == SUKUN and hamza_harakat is None and not hamza_sakin and hamza_tanwin is None:
            consonant_harakat = None
            hamza_sakin = True
        # If the consonant carries a vowel/tanwin and the hamza has nothing,
        # treat that mark as the hamza's (e.g. أَ standalone: hamza-fatha).
        if seen_first and hamza_harakat is None and not hamza_sakin and hamza_tanwin is None and consonant_harakat in (FATHA, KASRA, DAMMA):
            hamza_harakat = consonant_harakat
            consonant_harakat = None

        # Emit the consonant's pre-hamza vowel, if any.
        if consonant_harakat == FATHA:
            self._emit(out, rules, "a", "pre_hamza_vowel", token)
        elif consonant_harakat == KASRA:
            self._emit(out, rules, "i", "pre_hamza_vowel", token)
        elif consonant_harakat == DAMMA:
            self._emit(out, rules, "u", "pre_hamza_vowel", token)

        # Emit the hamza glottal stop itself.
        self._emit(out, rules, "'", "hamza_mark", token)

        if hamza_sakin:
            return index + 1

        # Hamza followed by a homogeneous long-vowel carrier (madd through hamza).
        if (
            hamza_harakat == DAMMA
            and next_cluster is not None
            and next_cluster.base == "و"
            and self._is_plain_madd_letter(next_cluster)
        ):
            self._emit(
                out, rules, "uu4" if MADDAH in next_cluster.marks else "uu", "madd_tabii", token
            )
            return index + 2
        if (
            hamza_harakat == KASRA
            and next_cluster is not None
            and next_cluster.base in {"ي", ALEF_MAQSURA}
            and self._is_plain_madd_letter(next_cluster)
        ):
            self._emit(
                out, rules, "ii4" if MADDAH in next_cluster.marks else "ii", "madd_tabii", token
            )
            return index + 2
        if (
            hamza_harakat == FATHA
            and next_cluster is not None
            and next_cluster.base in {ALEF, ALEF_MAQSURA}
        ):
            self._emit(
                out, rules, "aa4" if MADDAH in next_cluster.marks else "aa", "madd_tabii", token
            )
            return index + 2

        # Plain short vowel on the hamza.
        if hamza_harakat == DAMMA:
            self._emit(out, rules, "u", "hamza_vowel", token)
        elif hamza_harakat == KASRA:
            self._emit(out, rules, "i", "hamza_vowel", token)
        elif hamza_harakat == FATHA:
            self._emit(out, rules, "a", "hamza_vowel", token)

        # Tanwin on the hamza (e.g. مَلْجَـًٔا: hamza carries fathatan and the
        # following alif is the silent tanwin carrier).
        if hamza_tanwin == FATHATAN:
            self._emit(out, rules, "a", "tanwin", token)
            self._emit(out, rules, "n", "tanwin_n", token)
        elif hamza_tanwin == DAMMATAN:
            self._emit(out, rules, "u", "tanwin", token)
            self._emit(out, rules, "n", "tanwin_n", token)
        elif hamza_tanwin == KASRATAN:
            self._emit(out, rules, "i", "tanwin", token)
            self._emit(out, rules, "n", "tanwin_n", token)

        return index + 1

    def _emit_short_vowel(
        self,
        marks: tuple[str, ...],
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> None:
        if FATHA in marks:
            self._emit(out, rules, "a", "vowel", token)
        elif KASRA in marks or SMALL_KASRA in marks:
            self._emit(out, rules, "i", "vowel", token)
        elif DAMMA in marks:
            self._emit(out, rules, "u", "vowel", token)

    def _has_vowel(self, marks: tuple[str, ...]) -> bool:
        return any(mark in marks for mark in
                   (FATHA, DAMMA, KASRA, FATHATAN, DAMMATAN, KASRATAN, SMALL_KASRA))

    def _is_plain_madd_letter(self, cluster: ArabicChar) -> bool:
        return not self._has_vowel(cluster.marks) and SHADDA not in cluster.marks

    def _is_sakin_like(self, marks: tuple[str, ...]) -> bool:
        return SUKUN in marks or (not self._has_vowel(marks) and SHADDA not in marks)

    def _has_hamza_mark(self, marks: tuple[str, ...]) -> bool:
        return HAMZA_ABOVE in marks or HAMZA_BELOW in marks

    def _emit_trailing_hamza(
        self,
        clusters: list[ArabicChar],
        index: int,
        token: str,
        out: list[str],
        rules: list[RuleHit],
    ) -> int:
        """Emit a hamza glottal stop attached to the trailing portion of a
        cluster whose consonant has already been emitted (e.g. a sakin noon/mim
        followed by an orthographically-glued tatweel-hamza). The hamza's
        harakah is whichever vowel mark appears in the cluster (after any
        SUKUN/HAMZA_* discount)."""
        marks = clusters[index].marks
        self._emit(out, rules, "'", "hamza_mark", token)
        # Find the hamza's vowel (FATHA/KASRA/DAMMA) in marks, skipping SUKUN
        for m in marks:
            if m in (FATHA, KASRA, DAMMA):
                vowel_map = {FATHA: "a", KASRA: "i", DAMMA: "u"}
                self._emit(out, rules, vowel_map[m], "hamza_vowel", token)
                break
        return index + 1

    def _is_idgham_pair(self, first: str, second: str) -> bool:
        """True if (first sakin, second shadda) constitutes a valid within-word
        idgham: mutamathilain (same base) or one of the enumerated homorganic /
        close-articulation pairs. Long-vowel carriers (alif, waw, ya) are excluded
        because they often carry shadda for unrelated phonemic reasons."""
        if first in {ALEF, "و", "ي"}:
            return False
        if first == second:
            return True
        return (first, second) in IDGHAM_HOMORGANIC_PAIRS

    def _apply_iltiqa_sakinayn(
        self,
        symbols: list[str],
        rules: list[RuleHit],
        next_token: str,
    ) -> None:
        if not self.config.wasl or not self._starts_with_wasla(next_token):
            return

        index = self._last_nonempty_symbol_index(symbols)
        if index is None:
            return

        replacement = {
            "aa": "a",
            "aa4": "a",
            "aa6": "a",
            "ii": "i",
            "ii4": "i",
            "ii6": "i",
            "uu": "u",
            "uu4": "u",
            "uu6": "u",
        }.get(symbols[index])
        if replacement is None:
            return

        symbols[index] = replacement
        rules.append(RuleHit(index, replacement, "iltiqa_sakinayn_madd_drop", next_token))

    def _starts_with_wasla(self, token: str) -> bool:
        clusters = self._cluster(token)
        return bool(clusters) and clusters[0].base == ALEF_WASLA

    def _starts_with_hamza(self, word_symbols: list[str]) -> bool:
        """Check if the word's first phoneme is a hamza."""
        if not word_symbols:
            return False
        return word_symbols[0] == "'"

    def _upgrade_silah_before_hamza(
        self,
        symbols: list[str],
        rules: list[RuleHit],
        word_symbols: list[str],
        source: str,
    ) -> None:
        """When the next word starts with a hamza, upgrade the preceding tabii
        madd (aa/ii/uu) at the word boundary to its munfasil counterpart
        (aa4/ii4/uu4). When the madd is specifically ha-silah-sughra it becomes
        silah-kubra; otherwise it is plain madd munfasil."""
        if not self._starts_with_hamza(word_symbols):
            return

        index = self._last_nonempty_symbol_index(symbols)
        if index is None:
            return

        upgrade_map = {"aa": "aa4", "uu": "uu4", "ii": "ii4"}
        sym = symbols[index]
        if sym not in upgrade_map:
            return

        symbols[index] = upgrade_map[sym]
        was_silah = any(
            hit.symbol_index == index and hit.rule == "madd_silah" for hit in rules
        )
        new_rule = "madd_silah_kubra" if was_silah else "madd_munfasil"
        rules.append(RuleHit(index, symbols[index], new_rule, source))

    def _upgrade_previous_vowel(
        self,
        out: list[str],
        rules: list[RuleHit],
        symbol: str,
        rule: str,
        source: str,
        drop_preceding_hamza: bool = False,
    ) -> None:
        for index in range(len(out) - 1, -1, -1):
            if out[index] == "a":
                out[index] = symbol
                rules.append(RuleHit(index, symbol, rule, source))
                # ءَآ pattern: hemze is a carrier, remove the spurious ' symbol
                if drop_preceding_hamza and index > 0 and out[index - 1] == "'":
                    out.pop(index - 1)
                    rules_to_drop = [r for r in rules if r.symbol_index == index - 1 and r.symbol == "'"]
                    for r in rules_to_drop:
                        rules.remove(r)
                return
            if out[index] not in VOWELS:
                break
        self._emit(out, rules, symbol, rule, source)

    def _emit(
        self,
        out: list[str],
        rules: list[RuleHit],
        symbol: str,
        rule: str,
        source: str,
    ) -> None:
        out.append(symbol)
        rules.append(RuleHit(len(out) - 1, symbol, rule, source))

    def _first_consonant(self, symbols: list[str]) -> Optional[str]:
        for symbol in symbols:
            if symbol and symbol not in VOWELS and symbol != "PAUSE":
                return symbol.replace("_qal", "")
        return None

    def _last_vowel(self, symbols: list[str]) -> Optional[str]:
        for symbol in reversed(symbols):
            if symbol in VOWELS:
                return symbol
        return None

    def _pending_noon_index_from_rules(
        self,
        rules: list[RuleHit],
        symbols: list[str],
        start: int,
        end: int,
    ) -> Optional[int]:
        for hit in reversed(rules):
            if hit.symbol_index < start:
                break
            if (
                start <= hit.symbol_index < end
                and hit.rule in {"tanwin_n", "noon_sakin"}
                and symbols[hit.symbol_index] == "n"
            ):
                return hit.symbol_index
        return None

    def _pending_mim_index_from_rules(
        self,
        rules: list[RuleHit],
        symbols: list[str],
        start: int,
        end: int,
    ) -> Optional[int]:
        for hit in reversed(rules):
            if hit.symbol_index < start:
                break
            if (
                start <= hit.symbol_index < end
                and hit.rule == "mim_sakin"
                and symbols[hit.symbol_index] == "m"
            ):
                return hit.symbol_index
        return None

    def _resolve_noon_within_word(
        self,
        symbols: list[str],
        rules: list[RuleHit],
        source: str,
    ) -> None:
        for hit in list(rules):
            if hit.rule not in {"tanwin_n", "noon_sakin"} or symbols[hit.symbol_index] != "n":
                continue
            next_consonant = self._next_consonant(symbols, hit.symbol_index + 1)
            if next_consonant is not None:
                self._apply_noon_assimilation(
                    hit.symbol_index, next_consonant, symbols, rules, source
                )

    def _resolve_pending_noon(
        self,
        state: _State,
        next_consonant: Optional[str],
        symbols: list[str],
        rules: list[RuleHit],
        source: str,
    ) -> None:
        pending = state.pending_noon_index
        state.pending_noon_index = None
        if pending is None or next_consonant is None:
            return

        self._apply_noon_assimilation(pending, next_consonant, symbols, rules, source)

    def _apply_noon_assimilation(
        self,
        pending: int,
        next_consonant: str,
        symbols: list[str],
        rules: list[RuleHit],
        source: str,
    ) -> None:
        if next_consonant == "b":
            symbols[pending] = "m_g"
            rules.append(RuleHit(pending, "m_g", "iqlab", source))
        elif next_consonant == "m":
            symbols[pending] = "m_g"
            rules.append(RuleHit(pending, "m_g", "idgham_ghunna", source))
        elif next_consonant in self._idgham_ghunna:
            symbols[pending] = "n_g"
            rules.append(RuleHit(pending, "n_g", "idgham_ghunna", source))
        elif next_consonant in self._idgham_no_ghunna:
            symbols[pending] = ""
            rules.append(RuleHit(pending, "", "idgham_no_ghunna", source))
        elif next_consonant in self._ikhfa:
            symbols[pending] = "n_g"
            rules.append(RuleHit(pending, "n_g", "ikhfa", source))
        elif next_consonant in self._izhar:
            rules.append(RuleHit(pending, "n", "izhar", source))

    def _resolve_pending_mim(
        self,
        state: _State,
        word_symbols: list[str],
        word_rules: list[RuleHit],
        symbols: list[str],
        rules: list[RuleHit],
        source: str,
    ) -> None:
        pending = state.pending_mim_index
        state.pending_mim_index = None
        if pending is None or self._first_consonant(word_symbols) != "m":
            return

        symbols[pending] = "m_g"
        rules.append(RuleHit(pending, "m_g", "idgham_shafawi", source))
        if len(word_symbols) >= 2 and word_symbols[0] == "m" and word_symbols[1] == "m":
            del word_symbols[0]
            shifted: list[RuleHit] = []
            skipped = False
            for hit in word_rules:
                if not skipped and hit.symbol_index == 0 and hit.symbol == "m":
                    skipped = True
                    continue
                new_index = hit.symbol_index - 1 if hit.symbol_index > 0 else hit.symbol_index
                shifted.append(RuleHit(new_index, hit.symbol, hit.rule, hit.source))
            word_rules[:] = shifted

    def _coalesce_leading_geminate_after(
        self,
        symbols: list[str],
        word_symbols: list[str],
        word_rules: list[RuleHit],
        previous_symbol: str,
        leading_symbol: str,
    ) -> None:
        # Look past PAUSE markers; an advisory mushaf pause must not break
        # the iqlab/idgham coalescing if reading continues in wasl.
        previous = None
        for s in reversed(symbols):
            if not s or s == "PAUSE":
                continue
            previous = s
            break
        if previous != previous_symbol:
            return
        if (
            len(word_symbols) < 2
            or word_symbols[0] != leading_symbol
            or word_symbols[1] != leading_symbol
        ):
            return

        del word_symbols[0]
        shifted: list[RuleHit] = []
        skipped = False
        for hit in word_rules:
            if not skipped and hit.symbol_index == 0 and hit.symbol == leading_symbol:
                skipped = True
                continue
            new_index = hit.symbol_index - 1 if hit.symbol_index > 0 else hit.symbol_index
            shifted.append(RuleHit(new_index, hit.symbol, hit.rule, hit.source))
        word_rules[:] = shifted

    def _last_nonempty_symbol(self, symbols: list[str]) -> Optional[str]:
        for symbol in reversed(symbols):
            if symbol:
                return symbol
        return None

    def _last_nonempty_symbol_index(self, symbols: list[str]) -> Optional[int]:
        for index in range(len(symbols) - 1, -1, -1):
            if symbols[index]:
                return index
        return None

    def _next_consonant(self, symbols: list[str], start: int) -> Optional[str]:
        for symbol in symbols[start:]:
            if symbol and symbol not in VOWELS and symbol != "PAUSE":
                return symbol.replace("_qal", "")
        return None

    def _apply_waqf_transformations(
        self,
        symbols: list[str],
        rules: list[RuleHit],
        word_span: WordSpan,
        source: str,
    ) -> None:
        """Apply waqf transformations to the word before PAUSE marker."""
        if word_span.end <= word_span.start:
            return

        word_symbols = symbols[word_span.start : word_span.end]
        if not word_symbols:
            return

        # 1. Remove tanwin (vowel + n at word end)
        last_idx = len(word_symbols) - 1
        if last_idx >= 1 and word_symbols[last_idx] == "n" and word_symbols[last_idx - 1] in {"a", "i", "u"}:
            word_symbols[last_idx] = ""
            word_symbols[last_idx - 1] = ""

        # 2. Drop final short harakah
        last_idx = self._last_nonempty_symbol_index(word_symbols)
        if last_idx is not None and word_symbols[last_idx] in {"a", "i", "u"}:
            word_symbols[last_idx] = ""

        # 3. Convert taa marbuta t -> h
        if self._is_taa_marbuta(word_span, 0):
            for idx in range(len(word_symbols) - 1, -1, -1):
                if word_symbols[idx] == "t":
                    word_symbols[idx] = "h"
                    rules.append(RuleHit(word_span.start + idx, "h", "taa_marbuta_waqf", source))
                    break

        # 3b. Apply qalqalah on the now-sakin final consonant (waqf forces a
        # closing glottal release on qalqalah letters ق ط ب ج د).
        last_idx = self._last_nonempty_symbol_index(word_symbols)
        if last_idx is not None and word_symbols[last_idx] in QALQALAH:
            word_symbols[last_idx] = f"{word_symbols[last_idx]}_qal"
            rules.append(RuleHit(
                word_span.start + last_idx,
                word_symbols[last_idx],
                "qalqalah_kubra_waqf",
                source,
            ))

        # 4. Extend madd arid lis-sukun (aa/ii/uu -> aa6/ii6/uu6 at word end)
        #    Applies when a tabii madd is followed by a consonant that becomes
        #    sakin at waqf (either as the final symbol, or one before final consonant).
        madd_tabii = {"aa", "ii", "uu"}
        madd_map = {"aa": "aa6", "ii": "ii6", "uu": "uu6"}
        last_idx = self._last_nonempty_symbol_index(word_symbols)
        if last_idx is not None:
            last_sym = word_symbols[last_idx]
            if last_sym in madd_tabii:
                # Madd is the final symbol (e.g. هُدًى after tanwin drop)
                if not self._is_dagger_alef_madd(word_span, 0):
                    word_symbols[last_idx] = madd_map[last_sym]
                    rules.append(RuleHit(
                        word_span.start + last_idx,
                        word_symbols[last_idx],
                        "madd_arid_lis_sukun_waqf",
                        source,
                    ))
            elif last_sym not in {"a", "i", "u", ""}:
                # Final symbol is a consonant (sakin at waqf); look one step back for tabii madd.
                # Madd arid applies only when the madd is DIRECTLY before the sakin consonant
                # (no intervening harakah or consonant).
                prev_idx = last_idx - 1
                while prev_idx >= 0 and not word_symbols[prev_idx]:
                    prev_idx -= 1
                if prev_idx >= 0 and word_symbols[prev_idx] in madd_tabii:
                    word_symbols[prev_idx] = madd_map[word_symbols[prev_idx]]
                    rules.append(RuleHit(
                        word_span.start + prev_idx,
                        word_symbols[prev_idx],
                        "madd_arid_lis_sukun_waqf",
                        source,
                    ))

        # Update symbols list
        symbols[word_span.start : word_span.end] = word_symbols

    def _is_taa_marbuta(self, word_span: WordSpan, symbol_offset: int) -> bool:
        """Check if the word's token contains taa marbuta (ة) as its final letter."""
        token = word_span.token
        # Check if the token ends with taa marbuta (with optional diacritics)
        return "ة" in token

    def _is_dagger_alef_madd(self, word_span: WordSpan, symbol_offset: int) -> bool:
        """Check if the word's token contains dagger alif (ٰ)."""
        token = word_span.token
        return DAGGER_ALEF in token
