from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4738_raydb_hotpath_20260626" / "summary.json"
EVIDENCE = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4738_raydb_hotpath_materialization_boundary_repair_2026-06-26.json"
)
RAW_V4 = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4738_raydb_hotpath_20260626"
    / "raw"
    / "v4_current_raydb_style.json"
)


class V4Goal4738RaydbHotpathRepairTest(unittest.TestCase):
    def test_focused_rerun_clears_v2_and_v3_regression(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        analysis = payload["analysis"]
        self.assertTrue(analysis["v4_route_metadata_pass"])
        self.assertGreaterEqual(analysis["v4_vs_v2_14_hot"], 0.98)
        self.assertGreaterEqual(analysis["v4_vs_v3_0_2_hot"], 0.98)
        self.assertGreater(analysis["v4_vs_v2_14_hot"], 1.0)
        self.assertGreater(analysis["v4_vs_v3_0_2_hot"], 1.0)

    def test_v4_hot_path_excludes_row_materialization(self) -> None:
        payload = json.loads(RAW_V4.read_text(encoding="utf-8"))
        metadata = payload["metadata"]
        timings = metadata["timings"]
        self.assertEqual(0.0, timings["row_presentation"])
        self.assertFalse(metadata["host_materialization_in_hot_path"])
        self.assertFalse(metadata["group_rows_downloaded_to_host_in_hot_path"])
        self.assertTrue(metadata["result_rows_materialized_after_hot_path"])
        self.assertGreater(metadata["result_materialization_after_hot_path_sec"], 0.0)

    def test_structured_evidence_keeps_claims_bounded(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4738")
        self.assertEqual(
            payload["classification"]["new_row"],
            "modest_device_output_hot_path_win_not_formal_bar",
        )
        self.assertFalse(payload["classification"]["formal_candidate_win"])
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["raydb_high_performance_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertTrue(payload["classification"]["may_update_next_matrix"])


if __name__ == "__main__":
    unittest.main()
