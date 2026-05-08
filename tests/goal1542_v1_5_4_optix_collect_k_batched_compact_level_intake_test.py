from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1542_v1_5_4_optix_collect_k_batched_compact_level_intake_2026-05-08.md"
GOAL1541_JSON = ROOT / "docs" / "reports" / "goal1541_v1_5_4_optix_collect_k_batched_cub_sort_probe_2026-05-08.json"
GOAL1542_JSON = ROOT / "docs" / "reports" / "goal1542_v1_5_4_optix_collect_k_batched_compact_level_probe_2026-05-08.json"


class Goal1542V154OptixCollectKBatchedCompactLevelIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_clean_pod_evidence(self) -> None:
        data = json.loads(GOAL1542_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "3600b67343a93c08bda474c7d05e5115c6c9a77a")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertEqual(case["stage_profile"]["topology"]["sort_launches"], 1)

    def test_batched_compact_level_improves_long_counts_over_goal1541(self) -> None:
        goal1541 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1541_JSON.read_text(encoding="utf-8"))["cases"]
        }
        goal1542 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1542_JSON.read_text(encoding="utf-8"))["cases"]
        }

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                old_stage = goal1541[count]["stage_profile"]["stage_median_ms"]
                new_stage = goal1542[count]["stage_profile"]["stage_median_ms"]
                old_topology = goal1541[count]["stage_profile"]["topology"]
                new_topology = goal1542[count]["stage_profile"]["topology"]

                self.assertLess(new_stage["total_ms"], old_stage["total_ms"])
                self.assertLess(new_stage["merge_launch_ms"], old_stage["merge_launch_ms"])
                self.assertLess(new_topology["merge_launches"], old_topology["merge_launches"])
                self.assertEqual(new_topology["merge_launches"], 18)

    def test_intake_records_short_count_tradeoff_and_claim_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("flat/slightly slower tradeoff", text)
        self.assertIn("host-side launch orchestration", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
