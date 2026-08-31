from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3609_rayjoin_recommended_mixed_route_composite_2026-06-06.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3609_rayjoin_recommended_mixed_route_composite_a5000" / "summary.json"


class Goal3609RayJoinRecommendedMixedRouteCompositeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_records_512_mixed_composite_win(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3609.rayjoin_recommended_mixed_route_composite.v1")
        self.assertEqual(payload["goal"], 3609)
        self.assertEqual(payload["counts"], [512])
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertGreater(payload["summary"]["geomean_recommended_mixed_speedup_vs_all_cupy"], 20.0)

    def test_route_mix_is_explicit(self):
        row = self.payload["rows"][0]
        workloads = {entry["workload"]: entry for entry in row["workloads"]}
        self.assertEqual(workloads["pip"]["recommended_backend"], "cupy")
        self.assertEqual(workloads["pip"]["recommended_route_kind"], "cupy_dense_cuda_core")
        self.assertEqual(workloads["lsi"]["recommended_backend"], "optix")
        self.assertEqual(workloads["overlay_seed"]["recommended_backend"], "optix")
        self.assertAlmostEqual(workloads["pip"]["recommended_speedup_vs_cupy"], 1.0)
        self.assertGreater(workloads["lsi"]["recommended_speedup_vs_cupy"], 100.0)
        self.assertGreater(workloads["overlay_seed"]["recommended_speedup_vs_cupy"], 10.0)

    def test_report_blocks_large_scale_overclaim(self):
        self.assertIn("4096-chain composite is blocked", self.report)
        self.assertIn("CuPy=4977, recommended RTDL/OptiX=4985", self.report)
        self.assertIn("not a release packet", self.report)
        self.assertIn("not a public claim packet", self.report)
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
