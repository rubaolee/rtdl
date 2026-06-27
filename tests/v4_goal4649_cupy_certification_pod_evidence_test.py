from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "future"
    / "v4"
    / "evidence"
    / "v4_goal4649_cupy_grouped_reduction_gate_2026-06-25"
    / "pod_live_summary.json"
)


class V4Goal4649CuPyCertificationPodEvidenceTest(unittest.TestCase):
    def payload(self) -> dict[str, object]:
        return json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_pod_live_gate_passes_two_ready_cupy_targets(self) -> None:
        payload = self.payload()

        self.assertEqual("goal4649_cupy_gate_passed_pending_review", payload["status"])
        self.assertEqual("goal4649_cupy_frontdoor_certification_gate", payload["gate_status"])
        self.assertEqual(2, payload["summary"]["ready_target_count"])
        self.assertEqual(2, payload["summary"]["live_rows_passed"])
        self.assertEqual(0, payload["summary"]["live_rows_failed"])
        self.assertTrue(payload["summary"]["all_correctness_parity"])
        self.assertTrue(payload["summary"]["all_no_hot_host_materialization"])
        self.assertGreaterEqual(payload["summary"]["min_representative_speedup"], 1.20)

    def test_environment_and_claim_boundaries_are_recorded(self) -> None:
        payload = self.payload()
        env = payload["environment"]

        self.assertEqual("NVIDIA RTX A5000", env["gpu_name"])
        self.assertEqual("14.1.1", env["cupy"])
        self.assertEqual("3.12.3", env["python"])
        self.assertIn("570.195.03", env["nvidia_smi"])
        self.assertFalse(payload["cupy_performance_claim_authorized"])
        self.assertFalse(payload["partner_migration_counts_as_v4_speed_win"])
        self.assertFalse(payload["partner_parity_counts_as_v4_speed_win"])
        self.assertFalse(payload["pod_spend_authorized_by_this_file"])

    def test_each_row_uses_frozen_bars_and_preserves_no_public_claims(self) -> None:
        payload = self.payload()

        for row in payload["rows"]:
            self.assertTrue(row["pass"], row["candidate_id"])
            self.assertEqual("grouped_vector_sum_f64x2", row["operator"])
            self.assertEqual(100, row["repeat"])
            self.assertEqual(3, row["warmup"])
            self.assertEqual(1.20, row["speedup_floor"])
            self.assertTrue(row["correctness_parity"])
            self.assertEqual(0.0, row["max_err_x"])
            self.assertEqual(0.0, row["max_err_y"])
            self.assertFalse(row["host_materialization_in_hot_path"])
            self.assertFalse(row["public_claim_authorized"])
            self.assertGreaterEqual(row["representative_speedup"], row["speedup_floor"])
            self.assertIn("partner_continuation", row["metadata"]["phase_timing"]["phases_sec"])
            self.assertFalse(row["metadata"]["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["metadata"]["whole_app_speedup_claim_authorized"])
            self.assertFalse(row["metadata"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
