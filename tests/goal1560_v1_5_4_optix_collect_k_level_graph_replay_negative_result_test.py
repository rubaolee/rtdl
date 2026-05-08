from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1560_v1_5_4_optix_collect_k_level_graph_replay_negative_result_2026-05-08.md"
CANDIDATE_JSON = ROOT / "docs" / "reports" / "goal1560_v1_5_4_optix_collect_k_level_graph_replay_candidate_2026-05-08.json"
CONTROL_JSON = ROOT / "docs" / "reports" / "goal1560_v1_5_4_optix_collect_k_level_graph_replay_control_2026-05-08.json"


class Goal1560V154OptixCollectKLevelGraphReplayNegativeResultTest(unittest.TestCase):
    def test_candidate_preserved_parity_but_regressed_long_cases(self) -> None:
        control = {
            case["candidate_count"]: case
            for case in json.loads(CONTROL_JSON.read_text(encoding="utf-8"))["cases"]
        }
        candidate = {
            case["candidate_count"]: case
            for case in json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))["cases"]
        }

        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                self.assertTrue(candidate[count]["same_candidate_rows"])
                self.assertTrue(candidate[count]["same_valid_count"])
                self.assertTrue(candidate[count]["same_overflowed_flag"])

        self.assertGreater(
            candidate[65537]["stage_profile"]["stage_median_ms"]["total_ms"],
            control[65537]["stage_profile"]["stage_median_ms"]["total_ms"],
        )
        self.assertGreater(
            candidate[131072]["stage_profile"]["stage_median_ms"]["total_ms"],
            control[131072]["stage_profile"]["stage_median_ms"]["total_ms"],
        )

    def test_rejected_env_flag_is_not_left_in_runtime(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY", text)
        self.assertNotIn("collect_k_use_level_graph_replay", text)
        self.assertNotIn("CollectKLevelGraphReplayState", text)

    def test_report_records_rejection_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Rejected as a production implementation path", text)
        self.assertIn("preserved parity", text)
        self.assertIn("regressed both long target cases", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
