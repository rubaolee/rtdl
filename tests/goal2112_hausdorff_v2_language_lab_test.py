from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HAUSDORFF_BENCH = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd"


class Goal2112HausdorffV2LanguageLabTest(unittest.TestCase):
    def test_report_states_language_claim_and_boundary(self) -> None:
        report = (ROOT / "docs" / "reports" / "goal2112_hausdorff_v2_language_lab_2026-05-15.md").read_text()
        self.assertIn("RTDL v2.0 can express and validate exact Hausdorff Distance programs", report)
        self.assertIn("does not support", report)
        self.assertIn("broad RT-core Hausdorff speedup claim", report)
        self.assertIn("X-HD", report)

    def test_language_lab_artifacts_match_exact_reference(self) -> None:
        for size in (512, 2048, 8192):
            artifact = (
                ROOT
                / "docs"
                / "reports"
                / f"hausdorff_v2_language_lab_local_optix_{size}.json"
            )
            data = json.loads(artifact.read_text())
            self.assertEqual(data["scenario"]["points_a"], size)
            self.assertEqual(data["scenario"]["points_b"], size)
            for method in ("openmp_cpu", "cuda_cpp", "cupy_rawkernel", "rtdl_v2_user_cuda", "rtdl_rt_nearest_witness"):
                result = data["results"][method]
                self.assertTrue(result["ok"], method)
                self.assertTrue(result["matches_exact_reference"], method)
                self.assertTrue(result["metadata"]["exact_value"], method)
            threshold = data["results"]["rtdl_rt_threshold_search"]
            self.assertTrue(threshold["ok"])
            self.assertTrue(threshold["matches_exact_reference"])
            self.assertFalse(threshold["metadata"]["exact_value"])

    def test_lab_distinguishes_rtdl_partner_and_rt_core_paths(self) -> None:
        data = json.loads(
            (
                ROOT
                / "docs"
                / "reports"
                / "hausdorff_v2_language_lab_local_optix_8192.json"
            ).read_text()
        )
        self.assertTrue(data["results"]["rtdl_v2_user_cuda"]["metadata"]["uses_rtdl"])
        self.assertTrue(data["results"]["rtdl_v2_user_cuda"]["metadata"]["uses_partner"])
        self.assertFalse(data["results"]["rtdl_v2_user_cuda"]["metadata"]["uses_rt_cores"])
        self.assertTrue(data["results"]["rtdl_rt_nearest_witness"]["metadata"]["uses_rtdl"])
        self.assertFalse(data["results"]["rtdl_rt_nearest_witness"]["metadata"]["uses_partner"])
        self.assertTrue(data["results"]["rtdl_rt_nearest_witness"]["metadata"]["uses_rt_cores"])

    def test_language_lab_has_oracle_radius_diagnostic(self) -> None:
        source = (HAUSDORFF_BENCH / "rtdl_hausdorff_v2_language_lab.py").read_text()
        self.assertIn("rtdl_rt_nearest_witness_oracle_radius", source)
        self.assertIn("diagnostic_lower_bound", source)
        self.assertIn("exact_reference_plus_slack", source)
        self.assertIn("base_method", source)
        self.assertIn("oracle_radius_slack", source)


if __name__ == "__main__":
    unittest.main()
