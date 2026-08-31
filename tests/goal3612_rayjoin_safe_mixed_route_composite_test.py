from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3612_rayjoin_safe_mixed_route_composite_2026-06-06.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3612_rayjoin_safe_mixed_route_composite_a5000" / "summary.json"
SCRIPT = ROOT / "scripts" / "goal3612_rayjoin_safe_mixed_route_composite.py"


class Goal3612RayJoinSafeMixedRouteCompositeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_artifact_records_4096_safe_mixed_composite_win(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3612.rayjoin_safe_mixed_route_composite.v1")
        self.assertEqual(payload["goal"], 3612)
        self.assertEqual(payload["git_commit"], "83eb51dbd11a8dc2e05e26310fd8511ea76c2e2a")
        self.assertEqual(payload["counts"], [4096])
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertGreater(payload["summary"]["geomean_recommended_safe_mixed_speedup_vs_all_cupy"], 190.0)

    def test_safe_route_repairs_lsi_same_contract_mismatch(self):
        row = self.payload["rows"][0]
        workloads = {entry["workload"]: entry for entry in row["workloads"]}
        self.assertEqual(workloads["pip"]["recommended_route_kind"], "cupy_dense_cuda_core")
        self.assertEqual(workloads["lsi"]["recommended_route_kind"], "rtdl_optix_exact_refined_count")
        self.assertEqual(workloads["overlay_seed"]["recommended_route_kind"], "rtdl_optix_active_count")
        self.assertEqual(workloads["lsi"]["all_cupy_baseline"]["row_count"], 4977)
        self.assertEqual(workloads["lsi"]["recommended_route"]["row_count"], 4977)
        self.assertIn("host_double_exact_refine", workloads["lsi"]["recommended_route"]["segment_policy"])
        self.assertGreater(workloads["lsi"]["recommended_speedup_vs_cupy"], 700.0)
        self.assertGreater(workloads["overlay_seed"]["recommended_speedup_vs_cupy"], 30.0)

    def test_report_and_script_keep_claim_boundary(self):
        self.assertIn("not a RayJoin paper reproduction", self.report)
        self.assertIn("not a release packet", self.report)
        self.assertIn("not a public speedup claim packet", self.report)
        self.assertIn("run_rayjoin_prepared_optix_workload", self.script)
        self.assertIn("prepared_optix_exact_segment_pair_count", self.script)
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        for workload in self.payload["rows"][0]["workloads"]:
            for key, value in workload["claim_boundary"].items():
                self.assertFalse(value, f"{workload['workload']}:{key}")


if __name__ == "__main__":
    unittest.main()
