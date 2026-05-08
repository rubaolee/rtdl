from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1536_v1_5_4_optix_collect_k_late_level_compact_intake_2026-05-08.md"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json"
FINAL_JSON = ROOT / "docs" / "reports" / "goal1535_v1_5_4_optix_collect_k_parallel_final_compact_probe_2026-05-08.json"
LATE_JSON = ROOT / "docs" / "reports" / "goal1536_v1_5_4_optix_collect_k_late_level_compact_probe_2026-05-08.json"


class Goal1536V154OptixCollectKLateLevelCompactIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_clean_pod_evidence(self) -> None:
        data = json.loads(LATE_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "58e82b3dfaf0b5ac59d8397eb1b0d771eabf3c2e")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])

    def test_long_counts_improve_over_final_only_compact(self) -> None:
        baseline = {case["candidate_count"]: case for case in json.loads(BASELINE_JSON.read_text(encoding="utf-8"))["cases"]}
        final = {case["candidate_count"]: case for case in json.loads(FINAL_JSON.read_text(encoding="utf-8"))["cases"]}
        late = {case["candidate_count"]: case for case in json.loads(LATE_JSON.read_text(encoding="utf-8"))["cases"]}

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                baseline_stage = baseline[count]["stage_profile"]["stage_median_ms"]
                final_stage = final[count]["stage_profile"]["stage_median_ms"]
                late_stage = late[count]["stage_profile"]["stage_median_ms"]
                self.assertLess(late_stage["total_ms"], baseline_stage["total_ms"] * 0.35)
                self.assertLess(late_stage["total_ms"], final_stage["total_ms"] * 0.85)
                self.assertLess(late_stage["merge_sync_ms"], final_stage["merge_sync_ms"] * 0.65)

    def test_short_count_tradeoff_is_explicit(self) -> None:
        data = json.loads(LATE_JSON.read_text(encoding="utf-8"))
        case_4097 = next(case for case in data["cases"] if case["candidate_count"] == 4097)

        self.assertEqual(case_4097["stage_profile"]["topology"]["merge_launches"], 1)
        self.assertEqual(case_4097["stage_profile"]["topology"]["final_copies"], 1)
        self.assertGreater(case_4097["stage_profile"]["stage_median_ms"]["total_ms"], 1.5)

    def test_intake_keeps_claim_boundary_and_next_direction(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("strongest long-count result so far", text)
        self.assertIn("small `4097` case regresses", text)
        self.assertIn("dominated more by tile sort", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
