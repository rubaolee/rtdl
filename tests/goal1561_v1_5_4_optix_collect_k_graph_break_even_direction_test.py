from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1561_v1_5_4_optix_collect_k_graph_break_even_direction_2026-05-08.md"
BG_PROFILE = ROOT / "docs" / "reports" / "goal1561_v1_5_4_optix_collect_k_current_longcase_bg_profile_2026-05-08.json"
GOAL1560_CONTROL = ROOT / "docs" / "reports" / "goal1560_v1_5_4_optix_collect_k_level_graph_replay_control_2026-05-08.json"
GOAL1560_CANDIDATE = ROOT / "docs" / "reports" / "goal1560_v1_5_4_optix_collect_k_level_graph_replay_candidate_2026-05-08.json"


class Goal1561V154OptixCollectKGraphBreakEvenDirectionTest(unittest.TestCase):
    def test_background_profile_records_current_long_case_shape(self) -> None:
        data = json.loads(BG_PROFILE.read_text(encoding="utf-8"))
        by_count = {case["candidate_count"]: case for case in data["cases"]}

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                topology = by_count[count]["stage_profile"]["topology"]
                self.assertEqual(topology["merge_launches"], 23)
                self.assertTrue(by_count[count]["same_candidate_rows"])
                self.assertTrue(by_count[count]["same_valid_count"])
                self.assertTrue(by_count[count]["same_overflowed_flag"])

    def test_goal1560_long_cases_remain_negative(self) -> None:
        control = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1560_CONTROL.read_text(encoding="utf-8"))["cases"]
        }
        candidate = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1560_CANDIDATE.read_text(encoding="utf-8"))["cases"]
        }

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                self.assertGreater(
                    candidate[count]["stage_profile"]["stage_median_ms"]["total_ms"],
                    control[count]["stage_profile"]["stage_median_ms"]["total_ms"],
                )

    def test_report_sets_next_direction_and_stop_conditions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Do not continue per-call, per-level graph replay", text)
        self.assertIn("persistent topology reuse", text)
        self.assertIn("kernel fusion", text)
        self.assertIn("rough break-even replays", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
