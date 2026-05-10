import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1657_v1_6_x_optix_collect_k_four_way_merge_probe_2026-05-10.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1657_four_way_groups_1_4_16_32_seg2048_repeats1000.json"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"


class Goal1657OptixCollectKFourWayMergeProbeResultTest(unittest.TestCase):
    def test_report_records_rejection_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`four_way_merge_candidate_rejected`", text)
        self.assertIn("`do_not_promote`", text)
        self.assertIn("does not authorize", text)
        self.assertIn("public speedup wording", text)
        self.assertIn("does not alter production", text)

    def test_production_relevant_group_count_is_slower_despite_parity(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        by_group = {case["group_count"]: case for case in payload["cases"]}

        self.assertEqual(by_group[32]["mismatch_count"], 0)
        self.assertLess(by_group[32]["reference_over_four_way_speedup"], 1.0)
        self.assertGreater(by_group[32]["four_way_per_replay_us"], by_group[32]["reference_per_replay_us"])
        self.assertLess(by_group[1]["four_way_per_replay_us"], by_group[1]["reference_per_replay_us"])

    def test_probe_is_not_enabled_by_fastest_candidate(self) -> None:
        api = API.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_four_way_merge_probe", api)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_FOUR_WAY_MERGE", api)
        self.assertNotIn("collect_k_use_four_way_merge", api)


if __name__ == "__main__":
    unittest.main()
