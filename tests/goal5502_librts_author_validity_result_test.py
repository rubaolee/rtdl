from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5502" / "author_validity_gate.json"


class Goal5502AuthorValidityResultTest(unittest.TestCase):
    def test_existing_prefixes_choose_the_non_core_author_divergence_path(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "author_validity_gate_completed")
        self.assertTrue(payload["policy"]["author_wrong_is_not_inferred_from_count_difference"])
        self.assertFalse(payload["claim_boundary"]["author_validity_proven_for_full_inputs"])
        self.assertFalse(payload["claim_boundary"]["author_specific_rtdl_core_behavior_authorized"])
        self.assertEqual(payload["summary"]["rtdl_matches_author_diverges_count"], 4)
        self.assertEqual(payload["summary"]["both_match_count"], 1)
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(
            payload["summary"]["rtdl_matches_author_diverges_count"]
            + payload["summary"]["both_match_count"],
            5,
        )
        self.assertEqual(
            sorted(item["sample_geometry_count"] for item in payload["classifications"]),
            [100_000, 100_000, 100_000, 250_000, 250_000],
        )
        decisions = {item["decision"] for item in payload["classifications"]}
        self.assertIn("preserve_generic_rtdl_do_not_copy_author_divergence", decisions)


if __name__ == "__main__":
    unittest.main()
