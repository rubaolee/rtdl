from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m72_barnes_hut_blocker_bound_pod_20260624_091320"
)
SUMMARY = EVIDENCE_DIR / "summary.json"


class V3PhoenixM72BarnesHutBlockerBoundPodEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.summary = cls.payload["summary"]

    def test_packet_completed_with_all_checks_green(self) -> None:
        self.assertEqual(
            self.payload["status"],
            "barnes_hut_runner_parity_pod_ab_collected_not_release",
        )
        self.assertEqual(self.payload["failed_checks"], [])
        self.assertTrue(all(self.payload["checks"].values()))

    def test_m72_scorecard_binding_and_incumbent_declaration_are_present(self) -> None:
        scorecard = self.summary["scorecard_blocker"]
        self.assertEqual(scorecard["id"], "set_a_barnes_hut_app_geomean_0_844x")
        self.assertEqual(scorecard["app"], "barnes_hut")
        self.assertEqual(scorecard["route_kind"], "trunk_fix_candidate")
        self.assertTrue(self.summary["m72_blocker_metadata_ready"])

        declaration = self.summary["incumbent_route_declaration"]
        self.assertEqual(
            declaration["baseline_mode"],
            "fused_frontier_force_sum_bucketized_numba_cuda",
        )
        self.assertEqual(
            declaration["candidate_mode"],
            "prepared_execution_fused_vector_sum_numba_cuda",
        )
        self.assertEqual(declaration["body_counts"], [32768, 65536, 131072])
        self.assertEqual(declaration["query_repeat"], 11)
        self.assertEqual(declaration["warmup"], 3)
        self.assertEqual(declaration["samples"], 5)

    def test_runner_is_parity_with_current_control_not_a_new_speedup_claim(self) -> None:
        geomean = float(self.summary["runner_vs_existing_fused_control_geomean"])
        self.assertGreaterEqual(geomean, 0.98)
        self.assertLess(geomean, 1.02)
        self.assertAlmostEqual(geomean, 0.9997602284020717)
        self.assertTrue(self.summary["runner_parity_with_existing_fused_partner"])
        self.assertFalse(
            self.summary["wrapper_itself_faster_than_existing_fused_partner_claim_authorized"]
        )
        self.assertFalse(self.summary["public_speedup_claim_authorized"])
        self.assertFalse(self.summary["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(self.summary["full_all_app_rerun_authorized_by_this_packet"])

    def test_historical_optix_reference_is_large_but_not_primary_claim(self) -> None:
        self.assertGreater(float(self.summary["historical_optix_over_runner_geomean"]), 12.0)
        self.assertFalse(self.summary["historical_optix_reference_is_primary_claim"])
        self.assertIn(
            "not a wrapper-faster-than-current-control claim",
            self.summary["runtime_sourced_material_gain_scope"],
        )


if __name__ == "__main__":
    unittest.main()
