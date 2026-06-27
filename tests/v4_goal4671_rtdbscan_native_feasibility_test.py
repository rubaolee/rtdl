from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "future" / "v4" / "v4_goal4671_rtdbscan_native_grouped_union_feasibility_2026-06-25.md"
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4671_rtdbscan_grouped_union_telemetry_20260625" / "summary.json"
DEBT = ROOT / "future" / "v4" / "reviews" / "goal4671_completion_review_debt_no_release_authorization_2026-06-25.md"


class V4Goal4671RtDbscanNativeFeasibilityTest(unittest.TestCase):
    def test_report_records_no_go_not_release(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("rt_dbscan_grouped_union_no_go__pivot_required_for_second_true_v4_app_win", text)
        self.assertIn("direct side effect plus disabled same-root culling", text)
        self.assertIn("`1.166x` vs V2.14 hot", text)
        self.assertIn("does not authorize", text.lower())
        self.assertIn("Pivot away from RTDBSCAN", text)

    def test_evidence_preserves_best_generic_telemetry_shape(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4671")
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["claim_boundary"]["performance_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        row = payload["rows"][0]
        self.assertEqual(row["point_count"], 262144)
        variants = {variant["label"]: variant for variant in row["variants"]}
        best = variants["same_root_off_direct_on"]
        self.assertTrue(best["direct_side_effect"])
        self.assertFalse(best["same_root_culling"])
        self.assertLess(
            best["median_native_elapsed_sec"],
            variants["same_root_on_direct_off"]["median_native_elapsed_sec"],
        )
        telemetry = best["last_telemetry"]
        self.assertEqual(telemetry[4], 34359607296)
        self.assertEqual(telemetry[6], 34359607296)
        self.assertEqual(telemetry[7], 0)
        links_per_root = telemetry[9] / float(telemetry[8])
        self.assertLess(links_per_root, 1.05)

    def test_review_debt_blocks_release_authorization(self) -> None:
        text = DEBT.read_text(encoding="utf-8")
        self.assertIn("complete_as_diagnostic_no_go__rt_dbscan_not_second_true_v4_win", text)
        self.assertIn("known weekly limit until Jun 28, 2026 7pm America/New_York", text)
        self.assertIn("V4 release", text)
        self.assertIn("formal high-performance V4 wording", text)


if __name__ == "__main__":
    unittest.main()
