from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class Goal2115HausdorffXhdPrePodDesignReviewTest(unittest.TestCase):
    def test_review_records_xhd_boundary_and_pod_plan(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal2115_hausdorff_xhd_guided_pre_pod_design_review_2026-05-16.md"
        ).read_text()
        self.assertIn("accept-with-boundary", report)
        self.assertIn("not yet an X-HD-level performance implementation", report)
        self.assertIn("rtdl_rt_nearest_witness_oracle_radius", report)
        self.assertIn("Pod Run Recommendation", report)
        self.assertIn("does not authorize", report)

    def test_oracle_radius_artifact_is_diagnostic_and_exact(self) -> None:
        artifact = ROOT / "docs" / "reports" / "hausdorff_v2_language_lab_local_optix_8192_oracle_radius.json"
        data = json.loads(artifact.read_text())
        result = data["results"]["rtdl_rt_nearest_witness_oracle_radius"]
        self.assertTrue(result["ok"])
        self.assertTrue(result["matches_exact_reference"])
        self.assertEqual(result["method"], "rtdl_rt_nearest_witness_oracle_radius")
        self.assertEqual(result["base_method"], "rtdl_rt_nearest_witness")
        self.assertEqual(result["metadata"]["role"], "diagnostic_lower_bound")
        self.assertEqual(result["threshold_iterations"], 0)
        self.assertGreater(result["oracle_radius"], data["exact_reference"]["distance"])


if __name__ == "__main__":
    unittest.main()
