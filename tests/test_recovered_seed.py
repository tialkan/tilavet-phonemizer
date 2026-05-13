import json
import unittest
from pathlib import Path

from tilavet_phonemizer import Phonemizer

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "validation" / "recovered_seed.jsonl"


class RecoveredSeedTests(unittest.TestCase):
    def test_recovered_batch_has_35_examples(self):
        with SEED.open(encoding="utf-8") as handle:
            examples = [json.loads(line) for line in handle if line.strip()]

        self.assertEqual(len(examples), 35)
        self.assertEqual(examples[0]["ayah"], "1:1")
        self.assertEqual(examples[-1]["ayah"], "114:6")

    def test_candidate_outputs_stay_reproducible(self):
        phonemizer = Phonemizer()
        with SEED.open(encoding="utf-8") as handle:
            examples = [json.loads(line) for line in handle if line.strip()]

        for example in examples:
            with self.subTest(ayah=example["ayah"]):
                result = phonemizer.phonemize(example["arabic"])
                self.assertEqual(result.text, example["candidate_v1"])


if __name__ == "__main__":
    unittest.main()
