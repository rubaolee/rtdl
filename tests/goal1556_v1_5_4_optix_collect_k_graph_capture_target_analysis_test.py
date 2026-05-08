from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1556_v1_5_4_optix_collect_k_graph_capture_target_analysis_2026-05-08.md"
PROFILE = ROOT / "docs" / "reports" / "goal1556_v1_5_4_optix_collect_k_current_profile_2026-05-08.json"


class Goal1556V154OptixCollectKGraphCaptureTargetAnalysisTest(unittest.TestCase):
    def test_profile_preserves_current_long_case_topology(self) -> None:
        data = json.loads(PROFILE.read_text(encoding="utf-8"))
        by_count = {case["candidate_count"]: case for case in data["cases"]}

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                topology = by_count[count]["stage_profile"]["topology"]
                self.assertEqual(topology["merge_launches"], 23)
                self.assertEqual(topology["merge_levels"], 6)
                self.assertTrue(by_count[count]["profile_topology_matches_expected"])

    def test_report_targets_only_the_graphable_merge_window(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("batched compact-level merge window", text)
        self.assertIn("materialize -> mark -> device-prefix -> compact", text)
        self.assertIn("data dependency stays on device", text)
        self.assertIn("not capture across host-visible steps", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
