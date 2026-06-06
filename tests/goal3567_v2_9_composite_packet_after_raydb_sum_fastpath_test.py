from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "reports"
    / "goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_a5000"
    / "summary.json"
)
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_2026-06-06.md"
)


def _payload() -> dict[str, object]:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def _rows_by_case() -> dict[str, dict[str, object]]:
    return {row["case_id"]: row for row in _payload()["comparisons"]}


class Goal3567V29CompositePacketAfterRaydbFastPathTest(unittest.TestCase):
    def test_composite_packet_has_explicit_provenance(self) -> None:
        payload = _payload()
        summary = payload["summary"]

        self.assertEqual(payload["schema"], "rtdl.goal3567.v2_9_composite_packet_after_raydb_sum_fastpath.v1")
        self.assertEqual(payload["packet_kind"], "composite_packet_with_explicit_row_provenance")
        self.assertEqual(summary["row_count"], 11)
        self.assertEqual(summary["reused_goal3558_full_10s_rows"], 9)
        self.assertEqual(summary["goal3565_targeted_replacement_rows"], 2)
        self.assertEqual(
            set(summary["replaced_case_ids"]),
            {"raydb_optix_partner_resident_sum", "raydb_optix_partner_resident_count"},
        )
        self.assertEqual(summary["observed_target_miss_count_for_reused_rows"], 0)

    def test_raydb_rows_are_replaced_with_goal3565_fast_path_evidence(self) -> None:
        rows = _rows_by_case()
        sum_row = rows["raydb_optix_partner_resident_sum"]
        count_row = rows["raydb_optix_partner_resident_count"]

        self.assertTrue(sum_row["targeted_replacement_for_stale_goal3558_row"])
        self.assertTrue(count_row["targeted_replacement_for_stale_goal3558_row"])
        self.assertEqual(sum_row["evidence_source"], "goal3565_targeted_raydb_fastpath_a5000")
        self.assertEqual(count_row["evidence_source"], "goal3565_targeted_raydb_fastpath_a5000")
        self.assertAlmostEqual(sum_row["v28_speedup_vs_v23"], 1.585627471690698)
        self.assertAlmostEqual(count_row["v28_speedup_vs_v23"], 1.0090850848071564)
        self.assertLess(sum_row["v28_speedup_vs_v23_before_goal3565"], 0.95)
        self.assertLess(count_row["v28_speedup_vs_v23_before_goal3565"], 0.98)
        self.assertEqual(sum_row["targeted_trial_count_per_lane"], 5)
        self.assertEqual(count_row["targeted_trial_count_per_lane"], 3)

    def test_summary_reflects_repaired_raydb_packet(self) -> None:
        summary = _payload()["summary"]

        self.assertGreater(summary["geomean_speedup"], 1.06)
        self.assertAlmostEqual(summary["median_speedup"], 1.0090850848071564)
        self.assertAlmostEqual(summary["min_speedup"], 0.9876185889015384)
        self.assertAlmostEqual(summary["max_speedup"], 1.585627471690698)

    def test_no_claim_boundary_is_authorized(self) -> None:
        payload = _payload()
        self.assertTrue(payload["claim_boundary"]["internal_results_only"])
        for key, value in payload["claim_boundary"].items():
            if key != "internal_results_only":
                self.assertFalse(value, key)

        for row in payload["comparisons"]:
            boundary = row["claim_boundary"]
            self.assertTrue(boundary["internal_results_only"])
            for key, value in boundary.items():
                if key != "internal_results_only":
                    self.assertFalse(value, row["case_id"])

    def test_report_explains_composite_method_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("explicit composite packet", text)
        self.assertIn("9 unchanged rows", text)
        self.assertIn("2 RayDB rows", text)
        self.assertIn("RayDB `sum`: `0.944269x` became `1.585627x`", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
