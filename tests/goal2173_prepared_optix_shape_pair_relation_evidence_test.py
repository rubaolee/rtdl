from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2173_prepared_optix_shape_pair_relation_2026-05-16.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2173_prepared_overlay_seed_pod_2026-05-16.json"

EXPECTED_COMMIT = "7ab56c1fe382c58f2500ce7aed98696c065d9323"


class Goal2173PreparedOptixShapePairRelationEvidenceTest(unittest.TestCase):
    def test_report_records_prepared_overlay_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_prepare_shape_pair_relation_flags", text)
        self.assertIn("optix_prepared_overlay_seed", text)
        self.assertIn("1.293x", text)
        self.assertIn("1.138x", text)
        self.assertIn("app-agnostic", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release authorization", text)

    def test_artifact_records_prepared_overlay_win_and_parity(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = artifact["cases"]["overlay_county128_soil128"]
        embree = case["backends"]["embree"]
        optix = case["backends"]["optix"]
        prepared = case["backends"]["optix_prepared_overlay_seed"]

        self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
        self.assertEqual(case["workload"], "overlay_seed")
        self.assertEqual(prepared["baseline_kind"], "prepared_optix_shape_pair_relation_reused_build_side")
        self.assertTrue(prepared["prepared_build_side_reused"])
        self.assertTrue(prepared["rt_core_accelerated"])
        self.assertFalse(prepared["partner_accelerated"])
        self.assertTrue(prepared["all_parity_vs_cpu_python_reference"])
        self.assertEqual(prepared["row_counts"], [14036, 14036, 14036, 14036, 14036])
        self.assertEqual(embree["row_counts"], prepared["row_counts"])
        self.assertEqual(optix["row_counts"], prepared["row_counts"])

        prepared_sec = prepared["app_elapsed_sec_median"]
        self.assertLess(prepared_sec, optix["app_elapsed_sec_median"])
        self.assertLess(prepared_sec, embree["app_elapsed_sec_median"])
        self.assertGreater(optix["app_elapsed_sec_median"] / prepared_sec, 1.25)
        self.assertGreater(embree["app_elapsed_sec_median"] / prepared_sec, 1.1)

    def test_artifact_keeps_broad_claims_blocked(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = artifact["claim_boundary"]

        self.assertFalse(boundary["full_rayjoin_reproduction"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_rayjoin_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
