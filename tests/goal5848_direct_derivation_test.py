from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.goal5848_render_direct_worker import PARENT, render


class Goal5848DirectDerivationTest(unittest.TestCase):
    def test_derivation_changes_only_frozen_timing_counts(self):
        parent = PARENT.read_bytes()
        derived, receipt = render()
        expected = parent.replace(
            b"constexpr int kSteadyWarmups = 8;",
            b"constexpr int kSteadyWarmups = 16;",
        ).replace(
            b"constexpr int kSteadyRepetitions = 64;",
            b"constexpr int kSteadyRepetitions = 128;",
        )
        self.assertEqual(derived, expected)
        self.assertEqual(
            receipt["derived_sha256"], hashlib.sha256(derived).hexdigest()
        )
        self.assertFalse(receipt["optix_cuda_or_output_logic_changed"])

    def test_parent_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "direct.cpp"
            mutated.write_bytes(PARENT.read_bytes() + b"\n")
            with self.assertRaisesRegex(RuntimeError, "identity"):
                render(mutated)


if __name__ == "__main__":
    unittest.main()
