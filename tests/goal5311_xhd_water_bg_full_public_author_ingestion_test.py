import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5311_water_bg_full_public_author_ingestion_summary_pod.json"
)
AUTHOR_JSON = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "goal5311_raw"
    / "author_water_bg_full_public.json"
)


class Goal5311XhdWaterBgFullPublicAuthorIngestionTest(unittest.TestCase):
    def _summary(self) -> dict:
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_author_hd_exec_succeeded_on_full_public_wkt_candidate(self) -> None:
        payload = self._summary()
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5311.water_bg_full_public_author_ingestion.v1",
        )
        self.assertEqual(
            payload["status"],
            "author_hd_exec_full_public_water_bg_succeeded__not_paper_value_match",
        )
        self.assertTrue(payload["decision"]["author_ingestion_passed"])
        self.assertEqual(payload["author_result"]["input_point_counts"], [22_824_823, 52_271_467])
        self.assertEqual(
            payload["author_result"]["input_point_counts"],
            payload["author_result"]["expected_goal5310_point_counts"],
        )

    def test_author_result_is_not_paper_log_value_match(self) -> None:
        result = self._summary()["author_result"]
        self.assertAlmostEqual(result["hd_result"], 0.8970130085945129, places=12)
        self.assertAlmostEqual(result["paper_log_hd_result"], 0.8964367508888245, places=12)
        self.assertGreater(result["hd_result_abs_delta_vs_paper_log"], 5.0e-4)
        self.assertFalse(self._summary()["decision"]["paper_value_matched"])
        self.assertTrue(self._summary()["decision"]["exact_paper_dataset_reproduction_blocked"])

    def test_claim_boundary_blocks_figure5_correctness_and_ratio_claims(self) -> None:
        boundary = self._summary()["claim_boundary"]
        self.assertTrue(boundary["full_public_author_ingestion_claimed"])
        self.assertFalse(boundary["paper_value_match_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])

    def test_raw_author_json_is_present_and_has_expected_flags(self) -> None:
        payload = json.loads(AUTHOR_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["Input"]["NumDims"], 2)
        self.assertFalse(payload["Input"]["Normalize"])
        self.assertEqual(payload["Running"]["Repeats"][0]["Algorithm"], "XHD")
        self.assertEqual(payload["Running"]["Repeats"][0]["Execution"], "GPU")


if __name__ == "__main__":
    unittest.main()
