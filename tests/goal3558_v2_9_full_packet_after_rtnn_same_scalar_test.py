from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "reports"
    / "goal3558_v2_9_full_packet_after_rtnn_same_scalar_a5000_cap250k"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3558_v2_9_full_packet_after_rtnn_same_scalar_2026-06-06.md"


def _payload() -> dict[str, object]:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def _rows_by_case() -> dict[str, dict[str, object]]:
    return {row["case_id"]: row for row in _payload()["comparisons"]}


class Goal3558V29FullPacketAfterRTNNSameScalarTest(unittest.TestCase):
    def test_full_packet_is_target_compliant(self) -> None:
        payload = _payload()
        summary = payload["summary"]

        self.assertEqual(summary["row_count"], 11)
        self.assertEqual(summary["ratio_count"], 11)
        self.assertEqual(summary["target_met_by_plan_pair_count"], 11)
        self.assertEqual(summary["target_met_by_observed_pair_count"], 11)
        self.assertEqual(summary["observed_target_miss_count"], 0)
        self.assertEqual(summary["observed_target_misses"], [])
        self.assertGreater(summary["geomean_speedup"], 1.01)
        self.assertLess(summary["geomean_speedup"], 1.03)
        self.assertAlmostEqual(summary["median_speedup"], 0.9938217804455728)

        for row in payload["comparisons"]:
            self.assertTrue(row["v23_target_met_by_plan"], row["case_id"])
            self.assertTrue(row["v28_target_met_by_plan"], row["case_id"])
            self.assertTrue(row["v23_target_met_by_observed_sum"], row["case_id"])
            self.assertTrue(row["v28_target_met_by_observed_sum"], row["case_id"])
            self.assertGreater(row["v23_observed_measured_sec"], 10.0, row["case_id"])
            self.assertGreater(row["v28_observed_measured_sec"], 10.0, row["case_id"])

    def test_key_row_interpretation(self) -> None:
        rows = _rows_by_case()
        self.assertAlmostEqual(
            rows["raydb_optix_partner_resident_sum"]["v28_speedup_vs_v23"],
            0.9442693792475817,
        )
        self.assertGreater(rows["rtnn_optix_prepared_3d_ranked_summary"]["v28_speedup_vs_v23"], 1.06)
        self.assertGreater(
            rows["contact_manifold_optix_aabb_broadphase_collect_k"]["v28_speedup_vs_v23"],
            1.21,
        )
        self.assertGreater(rows["rt_dbscan_optix_grouped_stream"]["v28_speedup_vs_v23"], 0.99)
        self.assertLess(rows["raydb_optix_partner_resident_count"]["v28_speedup_vs_v23"], 0.98)

    def test_claim_boundaries_remain_false(self) -> None:
        for row in _payload()["comparisons"]:
            boundary = row["claim_boundary"]
            self.assertTrue(boundary["internal_results_only"])
            for key in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "broad_rt_core_speedup_claim_authorized",
                "true_zero_copy_claim_authorized",
                "package_install_claim_authorized",
                "paper_reproduction_claim_authorized",
            ):
                self.assertFalse(boundary[key], row["case_id"])

    def test_report_names_remaining_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("geomean speedup | 1.016537x", text)
        self.assertIn("RayDB sum", text)
        self.assertIn("internal benchmark evidence only", text)
        self.assertIn("does not authorize", text)
        self.assertIn("Start the next performance goal on RayDB", text)


if __name__ == "__main__":
    unittest.main()
