from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4735_barnes_hut_focused_20260626" / "summary.json"
EVIDENCE = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4736_barnes_hut_complete_workflow_focused_pod_2026-06-26.json"
)


class V4Goal4736BarnesHutCompleteWorkflowTest(unittest.TestCase):
    def test_focused_pod_result_passes_frozen_gates(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        ratios = summary["ratios"]
        pass_fail = summary["pass_fail"]

        self.assertGreaterEqual(ratios["v4_full_hot_over_v2_14"], 1.20)
        self.assertGreaterEqual(ratios["v4_full_wall_over_v2_14"], 1.10)
        self.assertGreaterEqual(ratios["v4_full_hot_over_v3_0_2_control"], 0.98)
        self.assertTrue(pass_fail["correctness_companion_ok"])
        self.assertFalse(pass_fail["v4_host_frontier_materialization_in_hot_path"])
        self.assertFalse(pass_fail["partner_migration_counted_as_speed"])

    def test_structured_evidence_classifies_bounded_candidate_row(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4736")
        self.assertEqual(
            payload["classification"]["goal4736_row"],
            "complete_app_candidate_win_vs_v2_14__v3_no_regression__not_rt_core_force_law",
        )
        self.assertFalse(payload["classification"]["old_row_erased"])
        self.assertTrue(payload["classification"]["may_update_next_matrix"])

    def test_non_authorization_boundaries_block_overclaiming(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_core_force_law_speedup_claim_authorized"])
        self.assertFalse(boundary["native_barnes_hut_kernel_claim_authorized"])
        self.assertFalse(boundary["broad_v4_over_v3_speedup_wording_authorized"])

    def test_raw_rows_exist_for_external_review(self) -> None:
        raw_dir = SUMMARY.parent
        for stem in (
            "v2_14_serious",
            "v3_0_2_serious",
            "v4_current_serious",
            "v2_14_correctness",
            "v3_0_2_correctness",
            "v4_current_correctness",
        ):
            self.assertTrue((raw_dir / f"{stem}.json").exists())


if __name__ == "__main__":
    unittest.main()
