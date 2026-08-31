from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5298_author_graphics_precheck_summary_pod.json"
)
RAW_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "goal5298_raw"


class Goal5298AuthorGraphicsPrecheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.by_case = {case["case_id"]: case for case in cls.summary["cases"]}

    def test_goal5298_is_author_only_and_not_a_paper_claim(self) -> None:
        self.assertEqual(
            self.summary["schema"],
            "rtdl.paper_reproduction.xhd.goal5298.author_graphics_precheck.v1",
        )
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["author_only_precheck_claimed"])
        self.assertTrue(boundary["level_b_same_source_candidate_claimed"])
        self.assertFalse(boundary["rtdl_route_run"])
        self.assertFalse(boundary["rtdl_author_performance_ratio_claimed"])
        self.assertFalse(boundary["figure_reproduction_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])

    def test_three_of_four_public_graphics_cases_match_paper_log_value(self) -> None:
        self.assertEqual(self.summary["case_count"], 4)
        self.assertEqual(self.summary["matched_paper_log_value_count"], 3)
        self.assertFalse(self.summary["all_cases_matched_paper_log_value"])

        matched = {
            case_id
            for case_id, case in self.by_case.items()
            if case["matched_paper_log_value"]
        }
        self.assertEqual(
            matched,
            {"dragon_happy", "thai_happy_scaled", "thai_asian_scaled"},
        )

    def test_dragon_asian_scaled_remains_no_go_against_paper_log_value(self) -> None:
        case = self.by_case["dragon_asian_scaled"]
        self.assertFalse(case["matched_paper_log_value"])
        self.assertAlmostEqual(case["author_hd_result"], 0.06545527279376984)
        self.assertAlmostEqual(case["paper_log_hd_result"], 0.06536811590194702)
        self.assertGreater(case["paper_log_abs_diff"], case["tolerance"])

    def test_matched_cases_have_expected_counts_and_small_abs_diff(self) -> None:
        expectations = {
            "dragon_happy": ([437645, 543652], 0.12572988867759705),
            "thai_happy_scaled": ([4999996, 543652], 0.21912431716918945),
            "thai_asian_scaled": ([4999996, 3609600], 0.28763842582702637),
        }
        for case_id, (counts, author_hd) in expectations.items():
            with self.subTest(case_id=case_id):
                case = self.by_case[case_id]
                self.assertTrue(case["matched_paper_log_value"])
                self.assertEqual(case["author_input_point_counts"], counts)
                self.assertAlmostEqual(case["author_hd_result"], author_hd)
                self.assertLessEqual(case["paper_log_abs_diff"], case["tolerance"])

    def test_raw_author_json_files_are_preserved_locally(self) -> None:
        for raw_name in [
            "dragon_happy_author.json",
            "dragon_asian_scaled_author.json",
            "thai_happy_scaled_author.json",
            "thai_asian_scaled_author.json",
        ]:
            with self.subTest(raw_name=raw_name):
                payload = json.loads((RAW_DIR / raw_name).read_text(encoding="utf-8"))
                self.assertIn("HDResult", payload)
                self.assertIn("Running", payload)
                self.assertIn("Input", payload)


if __name__ == "__main__":
    unittest.main()
