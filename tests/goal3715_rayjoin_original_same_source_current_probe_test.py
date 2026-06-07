import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3715_rayjoin_original_same_source_current_probe_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3715_rayjoin_original_same_source_current_a5000" / "summary.json"


class Goal3715RayJoinOriginalSameSourceCurrentProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.comparison = cls.payload["comparison"]

    def test_artifact_is_current_original_rayjoin_probe(self):
        self.assertEqual(self.payload["schema"], "rtdl.goal3691.rayjoin_original_same_source_probe.v1")
        self.assertEqual(self.payload["rtdl_git_commit"], "5951f35853ad09d3873926ad4c2012e0837fa16b")
        self.assertEqual(self.payload["rayjoin_source_commit_short"], "02bf622")
        self.assertIn("NVIDIA RTX A5000", self.payload["gpu"])
        self.assertIn("br_county_clean_25_odyssey_final.txt", self.payload["county"])
        self.assertIn("br_soil_ascii_odyssey_final.txt", self.payload["soil"])

    def test_lsi_correctness_gap_is_fixed_but_perf_gap_remains(self):
        self.assertEqual(self.comparison["rayjoin_lsi_intersections"], 20860)
        self.assertEqual(self.comparison["rayjoin_lsi_check_intersections"], 20860)
        self.assertEqual(self.comparison["rtdl_lsi_row_count"], 20860)
        self.assertEqual(self.comparison["lsi_count_delta_rtdl_minus_rayjoin"], 0)
        self.assertAlmostEqual(self.payload["rayjoin"]["lsi"]["query_sec"], 0.000873963)
        self.assertAlmostEqual(self.payload["rtdl"]["lsi"]["hot_median_sec"], 0.0011009611189365387)
        self.assertLess(self.comparison["lsi_query_speedup_rtdl_vs_rayjoin"], 1.0)
        self.assertGreater(self.comparison["lsi_query_speedup_rtdl_vs_rayjoin"], 0.75)

    def test_pip_query_time_is_promising_but_count_not_comparable(self):
        self.assertFalse(self.comparison["pip_count_comparable_to_rayjoin"])
        self.assertIn("does not print the PIP hit count", self.comparison["pip_count_comparison_note"])
        self.assertAlmostEqual(self.payload["rayjoin"]["pip"]["query_sec"], 0.000872374)
        self.assertAlmostEqual(self.payload["rtdl"]["pip"]["hot_median_sec"], 0.0004691528156399727)
        self.assertGreater(self.comparison["pip_query_speedup_rtdl_vs_rayjoin"], 1.8)

    def test_report_separates_current_original_rayjoin_evidence_from_claims(self):
        self.assertIn("LSI correctness blocker is fixed", self.report)
        self.assertIn("still slower: `0.794x`", self.report)
        self.assertIn("RayJoin PIP count-output path", self.report)
        self.assertIn("does not authorize", self.report)
        self.assertIn("Preserve Goal3713 as the all-CuPy same-contract comparison packet", self.report)

    def test_claim_boundary_flags_remain_false(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
