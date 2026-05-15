"""Tests for the public API surface added to support downstream tools.

These cover:
  - Serialization (`to_dict`, `to_alignment_dict`) on public result objects.
  - `Phonemizer.phoneme_inventory()` stability + matches docs/phoneme-spec.md.
  - `Phonemizer.phonemize_many()` batch helper.
  - The new CLI flags: --json, --rules-only, --waqf, --cross-ayah, --no-pause,
    --file, stdin via '-', and --print-inventory.

All additions are additive: they must not change phoneme outputs for any
existing input. The recovered-seed test still pins reproducibility separately.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tilavet_phonemizer import (
    Phonemizer,
    RuleHit,
    WordSpan,
    __version__,
)
from tilavet_phonemizer.cli import main


class SerializationTests(unittest.TestCase):
    def setUp(self):
        self.phonemizer = Phonemizer()

    def test_rule_hit_to_dict_round_trip(self):
        hit = RuleHit(symbol_index=3, symbol="aa6", rule="madd_lazim", source="ٱلضَّآلِّينَ")
        self.assertEqual(
            hit.to_dict(),
            {
                "symbol_index": 3,
                "symbol": "aa6",
                "rule": "madd_lazim",
                "source": "ٱلضَّآلِّينَ",
            },
        )
        # JSON-serializable (non-ASCII Arabic must survive ensure_ascii=False)
        payload = json.dumps(hit.to_dict(), ensure_ascii=False)
        self.assertIn("ٱلضَّآلِّينَ", payload)

    def test_word_span_to_dict(self):
        span = WordSpan(token="بِسْمِ", start=0, end=5)
        self.assertEqual(span.to_dict(), {"token": "بِسْمِ", "start": 0, "end": 5})

    def test_phonemization_result_to_dict_default(self):
        result = self.phonemizer.phonemize("بِسْمِ ٱللَّهِ")
        data = result.to_dict()
        self.assertEqual(set(data.keys()), {"symbols", "text", "words", "rules"})
        self.assertEqual(data["text"], "b i s m i l l aa h i")
        self.assertEqual(data["symbols"], result.symbols)
        # words round-trip
        self.assertEqual(data["words"][0]["token"], "بِسْمِ")
        self.assertEqual(data["words"][0]["start"], 0)
        # rules included by default; all entries shaped correctly
        self.assertTrue(len(data["rules"]) > 0)
        for r in data["rules"]:
            self.assertEqual(
                set(r.keys()), {"symbol_index", "symbol", "rule", "source"}
            )

    def test_phonemization_result_to_dict_skip_rules(self):
        result = self.phonemizer.phonemize("بِسْمِ")
        data = result.to_dict(include_rules=False)
        self.assertNotIn("rules", data)
        self.assertIn("symbols", data)

    def test_phonemization_result_clean_symbols(self):
        # هُدًى لِّلْمُتَّقِينَ produces an empty-string entry (idgham_no_ghunna
        # elides the tanwin n). `clean_symbols` should hide that empty entry.
        result = self.phonemizer.phonemize("هُدًۭى لِّلْمُتَّقِينَ")
        self.assertIn("", result.symbols, "expected at least one elided entry in raw symbols")
        clean = result.clean_symbols
        self.assertNotIn("", clean)
        # clean_symbols joins to the same canonical text
        self.assertEqual(" ".join(clean), result.text)

    def test_phonemization_result_word_symbols_slicing(self):
        result = self.phonemizer.phonemize("بِسْمِ ٱللَّهِ")
        # word 0 = بِسْمِ → b i s m i (5 symbols)
        self.assertEqual(result.word_symbols(0), ["b", "i", "s", "m", "i"])
        # word 1 = ٱللَّهِ → l l aa h i (5 symbols)
        self.assertEqual(result.word_symbols(1), ["l", "l", "aa", "h", "i"])

    def test_full_json_serializable(self):
        # An ayah with PAUSE, tanwin, idgham, qalqalah, madd lazim — exercising
        # many rule branches at once.
        text = "ذَٰلِكَ ٱلْكِتَٰبُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًۭى لِّلْمُتَّقِينَ"
        result = self.phonemizer.phonemize(text)
        payload = json.dumps(result.to_dict(), ensure_ascii=False)
        # round-trip: parsing it back gives us back the same text
        back = json.loads(payload)
        self.assertEqual(back["text"], result.text)

    def test_alignment_dict_drops_empty_elisions_and_remaps_words(self):
        result = self.phonemizer.phonemize("هُدًۭى لِّلْمُتَّقِينَ")
        self.assertIn("", result.symbols, "raw symbols should preserve silent elision")

        data = result.to_alignment_dict()
        self.assertNotIn("", data["symbols"])
        self.assertEqual(data["text"], " ".join(data["symbols"]))
        self.assertEqual(len(data["words"]), len(result.words))

        for word in data["words"]:
            word_symbols = data["symbols"][word["start"] : word["end"]]
            self.assertTrue(word_symbols)
            self.assertNotIn("", word_symbols)

    def test_alignment_dict_tracks_pause_as_metadata(self):
        result = self.phonemizer.phonemize("رَيْبَ ۛ فِيهِ")
        self.assertIn("PAUSE", result.symbols)

        data = result.to_alignment_dict()
        self.assertNotIn("PAUSE", data["symbols"])
        self.assertEqual(len(data["pauses"]), 1)
        self.assertEqual(data["pauses"][0]["raw_index"], result.symbols.index("PAUSE"))
        self.assertEqual(data["pauses"][0]["target_index"], 5)

        with_pause = result.to_alignment_dict(include_pause=True)
        self.assertIn("PAUSE", with_pause["symbols"])
        self.assertEqual(with_pause["pauses"][0]["target_index"], 5)

    def test_alignment_dict_rules_keep_raw_symbol_index_base(self):
        result = self.phonemizer.phonemize("بِسْمِ")
        data = result.to_alignment_dict(include_rules=True)
        self.assertIn("rules", data)
        self.assertEqual(data["rule_index_base"], "raw_symbols")


class PhonemeInventoryTests(unittest.TestCase):
    def test_inventory_returns_stable_list(self):
        inv1 = Phonemizer.phoneme_inventory()
        inv2 = Phonemizer.phoneme_inventory()
        self.assertEqual(inv1, inv2)
        # Returned lists are independent (mutating one must not affect the other)
        inv1.append("BOGUS")
        self.assertNotIn("BOGUS", Phonemizer.phoneme_inventory())

    def test_inventory_omits_pause_by_default(self):
        # docs/waqf-pause-decision.md: PAUSE is metadata, not a CTC class.
        self.assertNotIn("PAUSE", Phonemizer.phoneme_inventory())

    def test_inventory_includes_pause_when_requested(self):
        inv = Phonemizer.phoneme_inventory(include_metadata=True)
        self.assertIn("PAUSE", inv)

    def test_inventory_contains_all_documented_symbols(self):
        # Spec-required symbols from docs/phoneme-spec.md
        inv = set(Phonemizer.phoneme_inventory())
        # Consonants
        for sym in ["'", "b", "t", "th", "j", "H", "kh", "d", "dh", "r", "z", "s",
                    "sh", "S", "D", "T", "Z", "3", "gh", "f", "q", "k", "l", "L",
                    "m", "n", "h", "w", "y"]:
            self.assertIn(sym, inv, f"missing consonant {sym!r}")
        # Vowels (short + 3 madd lengths)
        for sym in ["a", "i", "u", "aa", "ii", "uu", "aa4", "ii4", "uu4",
                    "aa6", "ii6", "uu6"]:
            self.assertIn(sym, inv, f"missing vowel {sym!r}")
        # Variants
        for sym in ["n_g", "m_g", "q_qal", "T_qal", "b_qal", "j_qal", "d_qal"]:
            self.assertIn(sym, inv, f"missing variant {sym!r}")

    def test_inventory_no_duplicates(self):
        inv = Phonemizer.phoneme_inventory(include_metadata=True)
        self.assertEqual(len(inv), len(set(inv)), "phoneme inventory has duplicates")

    def test_inventory_count_matches_ctc_class_file(self):
        # data/ctc_classes.txt is the persisted version; cross-verify.
        ctc_path = Path(__file__).resolve().parents[1] / "data" / "ctc_classes.txt"
        if not ctc_path.exists():
            self.skipTest("ctc_classes.txt not present")
        on_disk = [line.strip() for line in ctc_path.read_text().splitlines() if line.strip()]
        inv = set(Phonemizer.phoneme_inventory(include_metadata=True))
        # Every symbol our inventory advertises must exist in the CTC class file
        # (the file may have blank/extras at fixed positions; we only assert
        # subset, not equality, to stay tolerant of CTC-specific entries).
        on_disk_set = set(on_disk)
        missing = inv - on_disk_set
        self.assertFalse(
            missing,
            f"inventory exposes symbols not present in ctc_classes.txt: {missing}",
        )


class BatchAPITests(unittest.TestCase):
    def test_phonemize_many_matches_loop(self):
        p = Phonemizer()
        inputs = ["بِسْمِ", "ٱللَّهِ", "هُوَ"]
        batched = p.phonemize_many(inputs)
        single = [p.phonemize(t) for t in inputs]
        self.assertEqual(len(batched), len(single))
        for b, s in zip(batched, single):
            self.assertEqual(b.text, s.text)
            self.assertEqual(b.symbols, s.symbols)

    def test_phonemize_many_accepts_generator(self):
        p = Phonemizer()
        gen = (t for t in ["بِسْمِ", "هُوَ"])
        out = p.phonemize_many(gen)
        self.assertEqual(len(out), 2)


class VersionTests(unittest.TestCase):
    def test_version_string_present(self):
        # Should be a PEP 440-ish version string; we only validate shape.
        self.assertIsInstance(__version__, str)
        self.assertTrue(__version__[0].isdigit())


class CliNewFlagsTests(unittest.TestCase):
    def _run_cli(self, argv: list[str], stdin: str = "") -> str:
        out = io.StringIO()
        with patch.object(sys, "argv", ["tilavet-phonemize"] + argv):
            with patch.object(sys, "stdin", io.StringIO(stdin)):
                with redirect_stdout(out):
                    main()
        return out.getvalue()

    def test_cli_json_flag_emits_json_object(self):
        # Default --json output: phoneme + words, no rule trace (rules can be
        # large; opt-in via --rules to keep the default lean).
        text = self._run_cli(["--json", "بِسْمِ"])
        payload = json.loads(text.strip())
        self.assertIn("symbols", payload)
        self.assertIn("text", payload)
        self.assertIn("words", payload)
        self.assertNotIn("rules", payload)
        self.assertEqual(payload["text"], "b i s m i")

    def test_cli_json_with_rules_flag_includes_rules(self):
        text = self._run_cli(["--json", "--rules", "بِسْمِ"])
        payload = json.loads(text.strip())
        self.assertIn("rules", payload)
        self.assertTrue(len(payload["rules"]) > 0)

    def test_cli_rules_only_suppresses_phoneme_line(self):
        text = self._run_cli(["--rules-only", "هُوَ"])
        lines = text.splitlines()
        self.assertTrue(lines)
        self.assertNotEqual(lines[0], "h u w a")
        self.assertTrue(all("\t" in line for line in lines))
        self.assertTrue(any("letter" in line for line in lines))

    def test_cli_json_rules_only_emits_only_rules(self):
        text = self._run_cli(["--json", "--rules-only", "هُوَ"])
        payload = json.loads(text.strip())
        self.assertEqual(set(payload.keys()), {"rules"})
        self.assertTrue(payload["rules"])
        self.assertEqual(payload["rules"][0]["rule"], "letter")

    def test_cli_waqf_flag_applies_waqf_transform(self):
        text = self._run_cli(["--waqf", "ٱلرَّحِيمِ ۝"]).strip()
        self.assertEqual(text, "' a r r a H ii6 m PAUSE")

    def test_cli_no_pause_flag_suppresses_pause(self):
        text = self._run_cli(["--no-pause", "رَيْبَ ۛ فِيهِ"]).strip()
        # Without PAUSE the marker should be gone.
        self.assertNotIn("PAUSE", text)

    def test_cli_cross_ayah_flag(self):
        text = self._run_cli(["--cross-ayah", "أَحَدٌ ۚ ٱللَّهُ"]).strip()
        self.assertNotIn("PAUSE", text)

    def test_cli_print_inventory(self):
        text = self._run_cli(["--print-inventory"])
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        # Must include PAUSE (we pass include_metadata=True in the CLI)
        self.assertIn("PAUSE", lines)
        # And core symbols
        for sym in ["'", "b", "aa", "n_g", "m_g", "q_qal"]:
            self.assertIn(sym, lines)

    def test_cli_stdin_dash(self):
        text = self._run_cli(["-"], stdin="هُوَ\nبِسْمِ\n").strip().splitlines()
        self.assertEqual(text, ["h u w a", "b i s m i"])

    def test_cli_file_input(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("هُوَ\nبِسْمِ\n")
            path = fh.name
        try:
            text = self._run_cli(["--file", path]).strip().splitlines()
            self.assertEqual(text, ["h u w a", "b i s m i"])
        finally:
            Path(path).unlink()

    def test_cli_no_input_exits(self):
        with patch.object(sys, "argv", ["tilavet-phonemize"]):
            with self.assertRaises(SystemExit):
                main()


if __name__ == "__main__":
    unittest.main()
