from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class Goal2114HausdorffPrePodPerfTuningTest(unittest.TestCase):
    def test_report_keeps_pre_pod_claim_narrow(self) -> None:
        report = (ROOT / "docs" / "reports" / "goal2114_hausdorff_pre_pod_perf_tuning_2026-05-16.md").read_text()
        self.assertIn("ready for a serious pod run", report)
        self.assertIn("remaining performance gap is algorithmic", report)
        self.assertIn("Do not claim broad RT-core HD speedup", report)

    def test_prepare_reuse_artifact_preserves_exactness(self) -> None:
        artifact = ROOT / "docs" / "reports" / "hausdorff_v2_language_lab_local_optix_8192_prepare_reuse.json"
        data = json.loads(artifact.read_text())
        result = data["results"]["rtdl_rt_nearest_witness"]
        self.assertTrue(result["ok"])
        self.assertTrue(result["matches_exact_reference"])
        self.assertTrue(result["rt_core_accelerated"])
        self.assertEqual(result["radius_strategy"], "rt_threshold_upper_bound")

    def test_tolerance_probe_artifacts_preserve_exactness(self) -> None:
        for suffix in ("1e-2", "1e-3", "1e-4"):
            artifact = ROOT / "docs" / "reports" / f"hausdorff_v2_language_lab_local_optix_8192_rt_tol_{suffix}.json"
            data = json.loads(artifact.read_text())
            result = data["results"]["rtdl_rt_nearest_witness"]
            self.assertTrue(result["ok"], suffix)
            self.assertTrue(result["matches_exact_reference"], suffix)
            self.assertGreater(result["threshold_iterations"], 0)


if __name__ == "__main__":
    unittest.main()
