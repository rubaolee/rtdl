import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2056_control_app_rawkernel_pod_followup_2026-05-15.md"
DATABASE = ROOT / "docs" / "reports" / "goal2056_database_rawkernel_cupy_optix_l4_4096.json"
POLYGON = ROOT / "docs" / "reports" / "goal2056_polygon_rawkernel_cupy_optix_l4_1024.json"


class Goal2056ControlAppRawkernelPodFollowupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.database = json.loads(DATABASE.read_text(encoding="utf-8"))
        cls.polygon = json.loads(POLYGON.read_text(encoding="utf-8"))

    def test_database_4096_artifact_records_speedup_and_parity(self):
        self.assertTrue(self.database["all_match_v1_8_python_rtdl_oracle"])
        self.assertEqual(self.database["candidate_backend"], "optix")
        self.assertEqual(self.database["partner"], "cupy")
        row = self.database["results"][0]
        self.assertEqual(row["app"], "database_analytics")
        self.assertEqual(row["copies"], 4096)
        self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])
        self.assertLess(row["v2_vs_v1_8_ratio"], 1.0)

    def test_polygon_1024_artifact_records_modest_speedups_and_parity(self):
        self.assertTrue(self.polygon["all_match_v1_8_python_rtdl_oracle"])
        self.assertEqual(self.polygon["candidate_backend"], "optix")
        apps = {row["app"]: row for row in self.polygon["results"]}
        self.assertEqual(set(apps), {"polygon_pair_overlap_area_rows", "polygon_set_jaccard"})
        for row in apps.values():
            self.assertEqual(row["copies"], 1024)
            self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])
            self.assertLess(row["v2_vs_v1_8_ratio"], 1.0)

    def test_claim_boundaries_and_negative_findings_are_documented(self):
        required = [
            "not absolutely fair",
            "cannot find -lgeos_c",
            "CUDA driver error: out of memory",
            "not yet cleanly scalable to 4096 copies",
            "v2.0 release readiness",
            "broad all-control-app speedup",
            "graph 4096 same-contract completion",
            "package-install readiness",
            "`accept-with-boundary`",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
