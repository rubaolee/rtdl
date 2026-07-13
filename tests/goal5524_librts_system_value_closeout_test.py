from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5524_librts_system_value_closeout.json"


class Goal5524LibrtsSystemValueCloseoutTest(unittest.TestCase):
    def test_scoped_completion_and_evidence_matrix(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertTrue(payload["completion_scope"]["librts_scoped_correctness_and_system_extraction_complete"])
        self.assertEqual(payload["evidence_matrix"]["point_contains"]["exact_count_matches"], 14)
        self.assertEqual(payload["evidence_matrix"]["range_contains"]["exact_count_matches"], 14)
        self.assertEqual(payload["evidence_matrix"]["range_intersects"]["exact_count_matches"], 14)
        self.assertEqual(payload["evidence_matrix"]["range_intersects"]["author_capacity_failures"], 2)
        self.assertEqual(payload["evidence_matrix"]["range_intersects"]["not_checkpointed"], 26)
        self.assertEqual(payload["evidence_matrix"]["pip"]["canonical_pair_rows_matched"], 71626)
        self.assertEqual(payload["evidence_matrix"]["mutation"]["author_rtdl_counts"], [2, 1, 0, 1, 0])

    def test_stop_loss_freezes_app_only_matrix_work(self):
        stop = json.loads(RESULT.read_text(encoding="utf-8"))["stop_loss"]
        self.assertEqual(stop["decision"], "freeze_exhaustive_range_intersects_enumeration")
        self.assertFalse(stop["generic_capability_produced_by_more_matrix_rows"])
        self.assertFalse(stop["unique_unresolved_semantic_question"])
        self.assertTrue(stop["preserve_uncheckpointed_as_uncheckpointed"])

    def test_system_and_app_ownership_are_separate(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertIn("generic Aabb2DColumns public front door", payload["system_improvements"])
        self.assertIn("WKT parsing and derived cache construction", payload["app_owned_work"])

    def test_forbidden_claims_remain_closed(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertFalse(payload["completion_scope"]["full_all_dataset_all_figure_paper_reproduction_complete"])
        self.assertFalse(payload["completion_scope"]["performance_parity_complete"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
