from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2171_rayjoin_overlay_seed_baseline_2026-05-16.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2171_rayjoin_overlay_seed_baseline_pod_2026-05-16.json"

EXPECTED_COMMIT = "7e4f440425b8e19caed147097945504b47aa9b81"


class Goal2171RayjoinOverlaySeedBaselineTest(unittest.TestCase):
    def test_report_records_overlay_seed_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("overlay_county128_soil128", text)
        self.assertIn("14,036", text)
        self.assertIn("6.061x", text)
        self.assertIn("prepared/reused generic OptiX shape-pair relation", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("claims that OptiX beats Embree on overlay seed", text)

    def test_artifact_records_parity_and_bounded_speedups(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = artifact["cases"]["overlay_county128_soil128"]
        cpu = case["backends"]["cpu"]
        embree = case["backends"]["embree"]
        optix = case["backends"]["optix"]

        self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
        self.assertEqual(case["workload"], "overlay_seed")
        self.assertEqual(cpu["row_counts"], [14036, 14036, 14036, 14036, 14036])
        self.assertEqual(embree["row_counts"], cpu["row_counts"])
        self.assertEqual(optix["row_counts"], cpu["row_counts"])
        self.assertTrue(cpu["all_parity_vs_cpu_python_reference"])
        self.assertTrue(embree["all_parity_vs_cpu_python_reference"])
        self.assertTrue(optix["all_parity_vs_cpu_python_reference"])
        self.assertFalse(cpu["rt_core_accelerated"])
        self.assertFalse(embree["rt_core_accelerated"])
        self.assertTrue(optix["rt_core_accelerated"])

        cpu_sec = cpu["app_elapsed_sec_median"]
        embree_sec = embree["app_elapsed_sec_median"]
        optix_sec = optix["app_elapsed_sec_median"]

        self.assertGreater(cpu_sec / embree_sec, 6.8)
        self.assertGreater(cpu_sec / optix_sec, 6.0)
        self.assertGreater(optix_sec / embree_sec, 1.1)

    def test_artifact_keeps_release_and_broad_claims_blocked(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = artifact["claim_boundary"]

        self.assertFalse(boundary["full_rayjoin_reproduction"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_rayjoin_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
