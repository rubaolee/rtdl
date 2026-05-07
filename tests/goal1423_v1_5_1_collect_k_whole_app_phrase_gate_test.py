from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1423V151CollectKWholeAppPhraseGateTest(unittest.TestCase):
    def test_release_gate_mechanically_requires_no_whole_app_claims(self) -> None:
        gate = rt.validate_v1_5_1_collect_k_bounded_release_surface_gate()

        self.assertIn("no whole-app claims", gate["required_phrases"])
        self.assertEqual(gate["missing_required_phrases"], ())
        self.assertTrue(gate["release_surface_docs_ready"])

    def test_required_phrase_set_keeps_all_public_claim_boundaries_together(self) -> None:
        phrases = rt.V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES

        for phrase in (
            "not stable primitive promotion",
            "no public speedup wording",
            "no zero-copy wording",
            "no whole-app claims",
            "no release tag action",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, phrases)


if __name__ == "__main__":
    unittest.main()
