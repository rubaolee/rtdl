from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3617_rayjoin_lsi_repair_dataset_diversity_probe_2026-06-06.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3617_rayjoin_lsi_repair_dataset_diversity_a5000" / "start0_4096_fast_mixed.json"


class Goal3617RayJoinLsiRepairDatasetDiversityProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_start0_4096_slice_matches_all_counts(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3609.rayjoin_recommended_mixed_route_composite.v1")
        self.assertEqual(payload["git_commit"], "5dd0c6ea4b3569bd74207214951caf07710867aa")
        self.assertEqual(payload["start"], 0)
        self.assertEqual(payload["counts"], [4096])
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertGreater(payload["summary"]["geomean_recommended_mixed_speedup_vs_all_cupy"], 160.0)

    def test_lsi_and_overlay_remain_repaired_and_fast(self):
        workloads = {entry["workload"]: entry for entry in self.payload["rows"][0]["workloads"]}
        self.assertEqual(workloads["lsi"]["all_cupy_baseline"]["row_count"], 5612)
        self.assertEqual(workloads["lsi"]["recommended_route"]["row_count"], 5612)
        self.assertGreater(workloads["lsi"]["recommended_speedup_vs_cupy"], 1500.0)
        self.assertEqual(workloads["overlay_seed"]["all_cupy_baseline"]["row_count"], 4678)
        self.assertEqual(workloads["overlay_seed"]["recommended_route"]["row_count"], 4678)
        self.assertGreater(workloads["overlay_seed"]["recommended_speedup_vs_cupy"], 20.0)

    def test_report_keeps_diversity_boundary(self):
        self.assertIn("does not close dataset diversity completely", self.report)
        self.assertIn("documented generic segment-pair primitive tolerance policy", self.report)
        self.assertIn("not a release packet", self.report)
        self.assertIn("not a public claim packet", self.report)


if __name__ == "__main__":
    unittest.main()
