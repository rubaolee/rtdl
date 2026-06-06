import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3657_v2_9_rayjoin_lsi_10s_integration_2026-06-06.md"
GOAL3654 = (
    ROOT
    / "docs"
    / "reports"
    / "goal3654_rayjoin_lsi_10s_prepared_left_a5000"
    / "lsi_4096_10s_summary.json"
)


class Goal3657V29RayJoinLsi10sIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.goal3654 = json.loads(GOAL3654.read_text(encoding="utf-8"))

    def test_report_integrates_goal3654_numbers(self):
        lsi = self.goal3654["comparisons"][0]
        self.assertEqual(lsi["rayjoin_visible_count"], 4977)
        self.assertEqual(lsi["rtdl_count"], 4977)
        for phrase in (
            "Goal3654",
            "10-second-class long run",
            "count `4977 == 4977`",
            "RTDL query `0.100411ms`",
            "RayJoin query `0.353115ms`",
            "ratio `0.284x`",
            "RayJoin process wall median `12.94s`",
            "RTDL hot-loop total median `10.31s`",
        ):
            self.assertIn(phrase, self.report)

    def test_report_keeps_rayjoin_as_contract_specific_not_whole_app(self):
        for phrase in (
            "not a single whole-app speedup claim",
            "do not collapse PIP, LSI, and overlay into one RayJoin scalar speedup",
            "Goal3658",
            "PIP scalar membership no",
            "longer belongs to CuPy",
            "still trails RayJoin `query_exec`",
            "first-class generic",
            "automatic partner/backend selection",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, self.report)

    def test_goal3654_claim_flags_remain_false(self):
        for flag, value in self.goal3654["claim_boundary"].items():
            self.assertFalse(value, flag)


if __name__ == "__main__":
    unittest.main()
