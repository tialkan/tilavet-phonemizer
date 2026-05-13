import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from tilavet_phonemizer import Phonemizer, PhonemizerConfig
from tilavet_phonemizer.arabic import (
    DAGGER_ALEF,
    DAMMA,
    FATHA,
    HAMZA_ABOVE,
    KASRA,
    MADDAH,
)
from tilavet_phonemizer.cli import main
from tilavet_phonemizer.phonemizer import ArabicChar, RuleHit, WordSpan, _State


class CoverageBranchTests(unittest.TestCase):
    def setUp(self):
        self.phonemizer = Phonemizer()

    def test_empty_input_and_empty_private_word(self):
        self.assertEqual(self.phonemizer.phonemize("   ").text, "")
        self.assertEqual(self.phonemizer.phonemize("").text, "")
        self.assertEqual(Phonemizer(PhonemizerConfig(emit_pause=False)).phonemize("ۘ").text, "")
        self.assertEqual(self.phonemizer._phonemize_word("", _State(True)), ([], []))

    def test_split_pause_mark_after_current_token(self):
        self.assertEqual(self.phonemizer._tokens("رَيْبَۛ فِيهِ").__next__(), "رَيْبَ")
        self.assertEqual(self.phonemizer._cluster("ۛ"), [])
        self.assertEqual(self.phonemizer._cluster(" "), [])

    def test_muqattaat_rejects_unknown_skeleton_and_unknown_letter(self):
        laa = self.phonemizer._cluster("لَآ")
        self.assertIsNone(self.phonemizer._try_muqattaat(laa, "لَآ"))
        clusters = [ArabicChar("پ", (MADDAH,))]
        self.phonemizer._MUQATTAT_SKELETONS.add("پ")
        try:
            self.assertIsNone(self.phonemizer._try_muqattaat(clusters, "پٓ"))
        finally:
            self.phonemizer._MUQATTAT_SKELETONS.remove("پ")

    def test_muqattaat_uu_branch_and_fallback_branch(self):
        self.assertEqual(self.phonemizer.phonemize("نٓ").text, "n uu6 n")
        original = self.phonemizer._MUQATTAT_NAMES["ن"]
        self.phonemizer._MUQATTAT_NAMES["ن"] = (["n", "x", "n"], 1, "x")
        try:
            self.assertEqual(self.phonemizer.phonemize("نٓ").text, "n x n")
        finally:
            self.phonemizer._MUQATTAT_NAMES["ن"] = original

    def test_allah_li_prefix_and_initial_article_short_paths(self):
        self.assertEqual(self.phonemizer.phonemize("لِلَّهِ").text, "l i l l aa h i")
        clusters = self.phonemizer._cluster("ٱلْ")
        out = []
        rules = []
        self.assertEqual(self.phonemizer._emit_article(clusters, 0, _State(True), "ٱلْ", out, rules), 2)
        self.assertEqual(out, [])
        self.assertEqual(self.phonemizer.phonemize("ٱلَّذِينَ").text, "' a l l a dh ii n a")

    def test_initial_wasla_damma_guess(self):
        self.assertEqual(self.phonemizer.phonemize("ٱدْعُ").text, "' u d_qal 3 u")

    def test_alef_madda_lazim_and_unknown_symbol(self):
        self.assertEqual(self.phonemizer.phonemize("آلَّذِي").text, "' aa6 l l a dh ii")
        self.assertEqual(self.phonemizer.phonemize("پَ").text, "")

    def test_mim_sakin_and_long_vowel_carriers(self):
        self.assertEqual(self.phonemizer.phonemize("هُم").text, "h u m")
        self.assertEqual(self.phonemizer.phonemize("قُولُوا").text, "q uu l uu")
        self.assertEqual(self.phonemizer.phonemize("قِيلَ").text, "q ii l a")
        self.assertTrue(self.phonemizer._is_long_vowel_carrier([ArabicChar("ق", (DAMMA,)), ArabicChar("و", ())], 1))
        self.assertTrue(self.phonemizer._is_long_vowel_carrier([ArabicChar("ق", (KASRA,)), ArabicChar("ي", ())], 1))

    def test_small_alef_madd_and_silah_ii_madd(self):
        out = []
        rules = []
        clusters = [ArabicChar("ه", (FATHA, DAGGER_ALEF, MADDAH))]
        self.phonemizer._emit_vowel_and_madd(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["aa4"])
        self.assertEqual(self.phonemizer.phonemize("هِۦٓ").text, "h ii4")

    def test_carrier_hamza_multivowel_and_madd_branches(self):
        out = []
        rules = []
        clusters = [ArabicChar("ي", (FATHA, KASRA, HAMZA_ABOVE))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["y", "a", "'", "i"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (FATHA, DAMMA, HAMZA_ABOVE))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["y", "a", "'", "u"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (KASRA, DAMMA, HAMZA_ABOVE))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["y", "i", "'", "u"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (DAMMA, KASRA, HAMZA_ABOVE))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        # Mark order: DAMMA is on the consonant, KASRA on the hamza.
        self.assertEqual(out, ["y", "u", "'", "i"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (DAMMA, DAMMA, HAMZA_ABOVE))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        # Dual same-vowel: first damma on consonant, second on hamza.
        self.assertEqual(out, ["y", "u", "'", "u"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (KASRA, HAMZA_ABOVE)), ArabicChar("ي", ())]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["y", "'", "ii"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (FATHA, HAMZA_ABOVE)), ArabicChar("ا", (MADDAH,))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["y", "'", "aa4"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (DAMMA, HAMZA_ABOVE))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["y", "'", "u"])

        out = []
        rules = []
        clusters = [ArabicChar("ي", (FATHA, HAMZA_ABOVE))]
        self.phonemizer._emit_cluster(clusters, 0, "x", out, rules)
        self.assertEqual(out, ["y", "'", "a"])

    def test_iltiqa_and_silah_noop_paths(self):
        rules = []
        symbols = []
        self.phonemizer._apply_iltiqa_sakinayn(symbols, rules, "ٱلْبَيْتِ")
        self.assertEqual(symbols, [])

        symbols = ["b"]
        self.phonemizer._apply_iltiqa_sakinayn(symbols, rules, "ٱلْبَيْتِ")
        self.assertEqual(symbols, ["b"])

        no_wasl = Phonemizer(PhonemizerConfig(wasl=False))
        symbols = ["aa"]
        no_wasl._apply_iltiqa_sakinayn(symbols, rules, "ٱلْبَيْتِ")
        self.assertEqual(symbols, ["aa"])

        self.assertFalse(self.phonemizer._starts_with_hamza([]))
        symbols = []
        self.phonemizer._upgrade_silah_before_hamza(symbols, rules, ["'"], "x")
        self.assertEqual(symbols, [])

        symbols = ["uu"]
        rules = []
        self.phonemizer._upgrade_silah_before_hamza(symbols, rules, ["'"], "x")
        self.assertEqual(symbols, ["uu4"])
        # Plain madd tabii at word boundary upgraded to munfasil
        self.assertEqual(rules[-1].rule, "madd_munfasil")

        symbols = ["uu"]
        rules = [RuleHit(0, "uu", "madd_silah", "h")]
        self.phonemizer._upgrade_silah_before_hamza(symbols, rules, ["'"], "x")
        self.assertEqual(symbols, ["uu4"])
        self.assertEqual(rules[-1].rule, "madd_silah_kubra")

    def test_upgrade_previous_vowel_fallback(self):
        out = ["b"]
        rules = []
        self.phonemizer._upgrade_previous_vowel(out, rules, "aa", "fallback", "x")
        self.assertEqual(out, ["b", "aa"])

    def test_resolve_pending_mim_geminate_shift(self):
        state = _State(True, pending_mim_index=0)
        symbols = ["m"]
        word_symbols = ["m", "m", "a"]
        word_rules = [RuleHit(0, "m", "shadda", "x"), RuleHit(1, "m", "shadda", "x")]
        rules = []
        self.phonemizer._resolve_pending_mim(state, word_symbols, word_rules, symbols, rules, "x")
        self.assertEqual(symbols, ["m_g"])
        self.assertEqual(word_symbols, ["m", "a"])

    def test_coalesce_leading_geminate_noop_and_shift(self):
        word_symbols = ["m"]
        word_rules = []
        self.phonemizer._coalesce_leading_geminate_after(["m_g"], word_symbols, word_rules, "m_g", "m")
        self.assertEqual(word_symbols, ["m"])

        word_symbols = ["m", "m", "a"]
        word_rules = [RuleHit(0, "m", "shadda", "x"), RuleHit(1, "m", "shadda", "x")]
        self.phonemizer._coalesce_leading_geminate_after(["m_g"], word_symbols, word_rules, "m_g", "m")
        self.assertEqual(word_symbols, ["m", "a"])

    def test_next_consonant_and_empty_waqf_paths(self):
        self.assertIsNone(self.phonemizer._first_consonant(["a", "PAUSE"]))
        self.assertIsNone(self.phonemizer._last_vowel(["b", "PAUSE"]))
        self.assertIsNone(self.phonemizer._next_consonant(["a", "PAUSE"], 0))
        rules = []
        symbols = ["a"]
        self.phonemizer._apply_waqf_transformations(symbols, rules, WordSpan("x", 1, 1), "x")
        self.assertEqual(symbols, ["a"])
        self.phonemizer._apply_waqf_transformations(symbols, rules, WordSpan("x", 0, 0), "x")
        self.assertEqual(symbols, ["a"])
        self.phonemizer._apply_waqf_transformations(symbols, rules, WordSpan("x", 1, 2), "x")
        self.assertEqual(symbols, ["a"])

    def test_waqf_extends_final_madd_arid(self):
        p = Phonemizer(PhonemizerConfig(waqf_on_pause=True))
        self.assertEqual(p.phonemize("قَالُواۚ").text, "q aa l uu6 PAUSE")

    def test_noon_assimilation_rare_paths(self):
        symbols = ["n", "b"]
        rules = [RuleHit(0, "n", "tanwin_n", "x")]
        self.phonemizer._resolve_noon_within_word(symbols, rules, "x")
        self.assertEqual(symbols[0], "m_g")

        symbols = ["b"]
        rules = [RuleHit(0, "b", "letter", "x")]
        self.phonemizer._resolve_noon_within_word(symbols, rules, "x")
        self.assertEqual(symbols, ["b"])

        symbols = ["m"]
        rules = [RuleHit(0, "n", "tanwin_n", "x")]
        self.phonemizer._resolve_noon_within_word(symbols, rules, "x")
        self.assertEqual(symbols, ["m"])

        symbols = ["n"]
        rules = [RuleHit(0, "n", "tanwin_n", "x")]
        self.phonemizer._resolve_noon_within_word(symbols, rules, "x")
        self.assertEqual(symbols, ["n"])

    def test_pending_index_break_paths(self):
        self.assertIsNone(self.phonemizer._pending_noon_index_from_rules([RuleHit(0, "n", "tanwin_n", "x")], ["n"], 1, 1))
        self.assertIsNone(self.phonemizer._pending_mim_index_from_rules([RuleHit(0, "m", "mim_sakin", "x")], ["m"], 1, 1))


class CliTests(unittest.TestCase):
    def test_cli_prints_text(self):
        with patch.object(sys, "argv", ["tilavet-phonemizer", "هُوَ"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main()
        self.assertEqual(output.getvalue().strip(), "h u w a")

    def test_cli_prints_rules(self):
        with patch.object(sys, "argv", ["tilavet-phonemizer", "هُوَ", "--rules"]):
            output = io.StringIO()
            with redirect_stdout(output):
                main()
        lines = output.getvalue().splitlines()
        self.assertEqual(lines[0], "h u w a")
        self.assertTrue(any("letter" in line for line in lines[1:]))

    def test_cli_module_main_guard(self):
        import runpy

        with patch.object(sys, "argv", ["tilavet-phonemizer", "هُوَ"]):
            output = io.StringIO()
            with redirect_stdout(output):
                runpy.run_module("tilavet_phonemizer.cli", run_name="__main__")
        self.assertEqual(output.getvalue().strip(), "h u w a")


if __name__ == "__main__":
    unittest.main()
