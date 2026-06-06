from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OLD_PACKET = (
    ROOT
    / "docs"
    / "reports"
    / "goal3548_v2_9_repeat_hook_10s_rerun_a5000_compact_calibrated3"
    / "summary.json"
)
FINAL_PACKET = (
    ROOT
    / "docs"
    / "reports"
    / "goal3551_rt_dbscan_a5000_targeted_calibrated2"
    / "summary.json"
)
FINAL_DRY_PACKET = (
    ROOT
    / "docs"
    / "reports"
    / "goal3551_rt_dbscan_a5000_targeted_calibrated2_dry"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3552_rt_dbscan_a5000_internal_repeat_evidence_2026-06-06.md"


def _payload(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _comparison(payload: dict[str, object]) -> dict[str, object]:
    rows = [
        row
        for row in payload["comparisons"]
        if row["case_id"] == "rt_dbscan_optix_grouped_stream"
    ]
    assert len(rows) == 1
    return rows[0]


class Goal3552RTDBSCANA5000InternalRepeatEvidenceTest(unittest.TestCase):
    def test_final_packet_is_target_compliant_and_near_parity(self) -> None:
        payload = _payload(FINAL_PACKET)
        comparison = _comparison(payload)
        summary = payload["summary"]

        self.assertEqual(payload["gpu"], "NVIDIA RTX A5000, 580.126.09, 24564 MiB")
        self.assertEqual(summary["row_count"], 1)
        self.assertEqual(summary["target_met_by_plan_pair_count"], 1)
        self.assertEqual(summary["target_met_by_observed_pair_count"], 1)
        self.assertEqual(summary["observed_target_miss_count"], 0)
        self.assertEqual(summary["observed_target_misses"], [])

        self.assertTrue(comparison["v23_target_met_by_plan"])
        self.assertTrue(comparison["v28_target_met_by_plan"])
        self.assertTrue(comparison["v23_target_met_by_observed_sum"])
        self.assertTrue(comparison["v28_target_met_by_observed_sum"])
        self.assertGreater(comparison["v23_observed_measured_sec"], 10.0)
        self.assertGreater(comparison["v28_observed_measured_sec"], 10.0)

        speedup = float(comparison["v28_speedup_vs_v23"])
        self.assertGreater(speedup, 0.98)
        self.assertLess(speedup, 1.02)

    def test_final_packet_improves_the_goal3548_weak_row_without_overclaiming(self) -> None:
        old = _comparison(_payload(OLD_PACKET))
        new = _comparison(_payload(FINAL_PACKET))

        self.assertAlmostEqual(float(old["v28_speedup_vs_v23"]), 0.9548167674661263)
        self.assertGreater(float(new["v28_speedup_vs_v23"]), float(old["v28_speedup_vs_v23"]))
        self.assertFalse(new["claim_boundary"]["release_authorized"])
        self.assertFalse(new["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(new["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(new["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(new["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(new["claim_boundary"]["paper_reproduction_claim_authorized"])

    def test_dry_plan_uses_internal_repeat_knob_for_both_lanes(self) -> None:
        payload = _payload(FINAL_DRY_PACKET)
        self.assertEqual(payload["summary"]["target_met_by_plan_pair_count"], 1)
        self.assertEqual(payload["summary"]["row_count"], 1)

        rows = payload["rows"]
        self.assertEqual({row["lane"] for row in rows}, {"v23", "v28"})
        for row in rows:
            plan = row["plan"]
            self.assertEqual(plan["method"], "internal_repeat_knob")
            self.assertEqual(plan["repeat_flag"], "--repeat")
            self.assertTrue(plan["target_met_by_plan"])
            self.assertGreaterEqual(plan["planned_repeat"], 1000)

    def test_report_records_boundary_and_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("0.955x", text)
        self.assertIn("0.992x", text)
        self.assertIn("internal performance evidence only", text)
        self.assertIn("kernel/runtime performance problem", text)
        self.assertIn("public speedup claims", text)


if __name__ == "__main__":
    unittest.main()
