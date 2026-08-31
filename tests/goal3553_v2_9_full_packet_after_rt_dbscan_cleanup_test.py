from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "reports"
    / "goal3553_v2_9_full_packet_after_rt_dbscan_a5000_cap250k"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3553_v2_9_full_packet_after_rt_dbscan_cleanup_2026-06-06.md"


def _payload(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _by_case(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {row["case_id"]: row for row in payload["comparisons"]}


class Goal3553V29FullPacketAfterRTDBSCANCleanupTest(unittest.TestCase):
    def test_full_packet_is_all_target_compliant(self) -> None:
        payload = _payload(PACKET)
        summary = payload["summary"]

        self.assertEqual(payload["gpu"], "NVIDIA RTX A5000, 580.126.09, 24564 MiB")
        self.assertEqual(summary["row_count"], 11)
        self.assertEqual(summary["ratio_count"], 11)
        self.assertEqual(summary["target_met_by_plan_pair_count"], 11)
        self.assertEqual(summary["target_met_by_observed_pair_count"], 11)
        self.assertEqual(summary["observed_target_miss_count"], 0)
        self.assertEqual(summary["observed_target_misses"], [])
        self.assertGreater(summary["geomean_speedup"], 0.99)
        self.assertLess(summary["geomean_speedup"], 1.01)

        for row in payload["comparisons"]:
            self.assertTrue(row["v23_target_met_by_plan"], row["case_id"])
            self.assertTrue(row["v28_target_met_by_plan"], row["case_id"])
            self.assertTrue(row["v23_target_met_by_observed_sum"], row["case_id"])
            self.assertTrue(row["v28_target_met_by_observed_sum"], row["case_id"])
            self.assertGreater(row["v23_observed_measured_sec"], 10.0, row["case_id"])
            self.assertGreater(row["v28_observed_measured_sec"], 10.0, row["case_id"])
            self.assertFalse(row["claim_boundary"]["release_authorized"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["whole_app_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_key_row_interpretation_matches_report(self) -> None:
        rows = _by_case(_payload(PACKET))

        self.assertGreater(rows["hausdorff_optix_threshold"]["v28_speedup_vs_v23"], 1.09)
        self.assertGreater(rows["raydb_optix_partner_resident_count"]["v28_speedup_vs_v23"], 1.09)
        self.assertGreater(rows["spatial_rayjoin_optix_prepared_full_route"]["v28_speedup_vs_v23"], 1.05)
        self.assertGreater(rows["rt_dbscan_optix_grouped_stream"]["v28_speedup_vs_v23"], 0.99)
        self.assertLess(rows["contact_manifold_optix_aabb_broadphase_collect_k"]["v28_speedup_vs_v23"], 0.86)
        self.assertLess(rows["rtnn_optix_prepared_3d_ranked_summary"]["v28_speedup_vs_v23"], 0.97)

    def test_final_plan_uses_higher_rayjoin_cap(self) -> None:
        payload = _payload(PACKET)
        rows = [
            row
            for row in payload["rows"]
            if row["case_id"] == "spatial_rayjoin_optix_prepared_full_route"
        ]
        self.assertEqual(len(rows), 2)
        for row in rows:
            plan = row["plan"]
            self.assertEqual(plan["method"], "internal_repeat_knob")
            self.assertEqual(plan["repeat_flag"], "--repeat")
            self.assertGreater(plan["planned_repeat"], 50000)
            self.assertTrue(plan["target_met_by_plan"])

    def test_report_states_boundary_and_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("geomean speedup: `1.000293x`", text)
        self.assertIn("Contact manifold: `0.846x`", text)
        self.assertIn("RT-DBSCAN", text)
        self.assertIn("internal benchmark evidence only", text)
        self.assertIn("Goal3554 should focus on the contact-manifold row", text)


if __name__ == "__main__":
    unittest.main()
