from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3613_lsi_left_id_dense_count_exact_predicate_2026-06-06.md"
MISMATCH = ROOT / "docs" / "reports" / "goal3613_lsi_left_id_dense_count_exact_predicate_a5000" / "mismatch_after_patch.json"
FAST_MIXED = ROOT / "docs" / "reports" / "goal3613_lsi_left_id_dense_count_exact_predicate_a5000" / "fast_mixed_after_patch.json"


class Goal3613LsiLeftIdDenseCountExactPredicateArtifactTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.mismatch = json.loads(MISMATCH.read_text(encoding="utf-8"))
        cls.fast_mixed = json.loads(FAST_MIXED.read_text(encoding="utf-8"))

    def test_mismatch_probe_is_zero_after_patch(self):
        payload = self.mismatch
        self.assertEqual(payload["schema"], "rtdl.goal3610.rayjoin_lsi_4096_count_mismatch_probe.v1")
        self.assertEqual(payload["git_commit"], "223981f7bd51862b183489976ca1cc661e3fd5a0")
        self.assertEqual(payload["cupy_total"], 4977)
        self.assertEqual(payload["rtdl_optix_total"], 4977)
        self.assertEqual(payload["diff_count"], 0)
        self.assertEqual(payload["delta_sum"], 0)

    def test_fast_mixed_composite_is_exact_and_fast(self):
        payload = self.fast_mixed
        self.assertEqual(payload["schema"], "rtdl.goal3609.rayjoin_recommended_mixed_route_composite.v1")
        self.assertEqual(payload["git_commit"], "223981f7bd51862b183489976ca1cc661e3fd5a0")
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertGreater(payload["summary"]["geomean_recommended_mixed_speedup_vs_all_cupy"], 180.0)
        row = payload["rows"][0]
        workloads = {entry["workload"]: entry for entry in row["workloads"]}
        self.assertEqual(workloads["lsi"]["all_cupy_baseline"]["row_count"], 4977)
        self.assertEqual(workloads["lsi"]["recommended_route"]["row_count"], 4977)
        self.assertGreater(workloads["lsi"]["recommended_speedup_vs_cupy"], 2000.0)

    def test_report_keeps_boundary_and_generic_design(self):
        self.assertIn("No RayJoin or CDB logic enters the engine", self.report)
        self.assertIn("segment-pair count contract", self.report)
        self.assertIn("not a RayJoin paper reproduction", self.report)
        self.assertIn("not a release packet", self.report)
        for key, value in self.fast_mixed["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
