import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "docs" / "reports" / "goal1568_v1_5_4_optix_collect_k_post_fusion_longcase_profile_2026-05-08.json"
REPORT = ROOT / "docs" / "reports" / "goal1568_v1_5_4_optix_collect_k_post_fusion_bottleneck_direction_2026-05-08.md"


class Goal1568V154OptixCollectKPostFusionBottleneckDirectionTest(unittest.TestCase):
    def test_profile_is_accepted_current_evidence(self) -> None:
        data = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertTrue(data["accepted_goal1506_evidence"])
        self.assertEqual(data["git_commit"][:8], "fe0570bf")
        self.assertEqual([case["candidate_count"] for case in data["cases"]], [65537, 131072])
        for case in data["cases"]:
            self.assertTrue(case["same_candidate_rows"])
            self.assertTrue(case["same_valid_count"])
            self.assertTrue(case["profile_topology_matches_expected"])

    def test_report_records_split_bottleneck_not_pure_launch_problem(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not a pure launch-count problem", text)
        self.assertIn("merge launch", text)
        self.assertIn("merge sync", text)
        self.assertIn("Do not continue compact-level fusion", text)

    def test_report_selects_carry_copy_elimination_as_next_odd_tile_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("carry-copy elimination", text)
        self.assertIn("segment descriptor aliasing", text)
        self.assertIn("odd tile counts", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
