from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4733_triangle_focused_20260626" / "summary.json"
EVIDENCE = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4733_triangle_v3_regression_resolution_2026-06-26.json"
)


class V4Goal4733TriangleFocusedRerunTest(unittest.TestCase):
    def test_focused_summary_clears_v3_regression_with_parity(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        analysis = payload["analysis"]

        self.assertTrue(analysis["all_rows_parity"])
        self.assertTrue(analysis["v4_residency_metadata_pass"])
        self.assertGreaterEqual(analysis["v4_vs_v3_0_2_hot"], 0.98)
        self.assertGreater(analysis["v4_vs_v2_14_hot"], 1.0)
        self.assertEqual(
            analysis["classification_hint"],
            "v3_regression_cleared_by_high_repeat_focused_rerun",
        )

    def test_structured_evidence_preserves_non_authorization(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4733")
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["old_goal4669_row_erased"])
        self.assertTrue(payload["claim_boundary"]["focused_delta_may_update_next_matrix"])

    def test_raw_rows_remain_available_for_external_review(self) -> None:
        raw_dir = SUMMARY.parent / "raw"
        for version in ("v2_14", "v3_0_2", "v4_current"):
            self.assertTrue((raw_dir / f"{version}_triangle_counting.json").exists())


if __name__ == "__main__":
    unittest.main()
