import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2058_graph_control_app_rawkernel_pod_followup_2026-05-15.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2058_graph_rawkernel_cupy_optix_l4_512.json"


class Goal2058GraphControlAppRawkernelPodFollowupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_graph_artifact_records_bounded_speedup_and_parity(self):
        self.assertTrue(self.artifact["all_match_v1_8_python_rtdl_oracle"])
        self.assertEqual(self.artifact["candidate_backend"], "optix")
        row = self.artifact["results"][0]
        self.assertEqual(row["app"], "graph_analytics")
        self.assertEqual(row["copies"], 512)
        self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])
        self.assertLess(row["v2_vs_v1_8_ratio"], 1.0)

    def test_report_blocks_general_graph_overclaim(self):
        required = [
            "not to claim that v2.0 has a reusable general graph primitive yet",
            "closed-form/rawkernel continuation for the authored app shape",
            "reusable general graph primitive readiness",
            "v2.0 release readiness",
            "graph `copies=4096` completion",
            "broad RT-core speedup",
            "`accept-with-boundary`",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
