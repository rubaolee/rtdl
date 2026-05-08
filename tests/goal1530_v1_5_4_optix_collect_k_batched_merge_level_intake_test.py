from pathlib import Path
import json
import unittest

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1530_v1_5_4_optix_collect_k_batched_merge_level_intake_2026-05-08.md"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json"
ONE_PASS_JSON = ROOT / "docs" / "reports" / "goal1529_v1_5_4_optix_collect_k_one_pass_merge_probe_2026-05-08.json"
BATCHED_JSON = ROOT / "docs" / "reports" / "goal1530_v1_5_4_optix_collect_k_batched_merge_level_probe_2026-05-08.json"
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal1530V154OptixCollectKBatchedMergeLevelIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_with_batched_level_topology(self) -> None:
        data = json.loads(BATCHED_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        self.assertEqual([case["candidate_count"] for case in data["cases"]], [4097, 65537, 131072])
        self.assertEqual(probe.expected_topology(131072, 2)["merge_launches"], 5)
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertTrue(case["profile_native_path_matches_expected"])
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])

    def test_long_count_total_and_merge_time_improve(self) -> None:
        baseline = {case["candidate_count"]: case for case in json.loads(BASELINE_JSON.read_text(encoding="utf-8"))["cases"]}
        one_pass = {case["candidate_count"]: case for case in json.loads(ONE_PASS_JSON.read_text(encoding="utf-8"))["cases"]}
        batched = {case["candidate_count"]: case for case in json.loads(BATCHED_JSON.read_text(encoding="utf-8"))["cases"]}

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                baseline_stage = baseline[count]["stage_profile"]["stage_median_ms"]
                one_pass_stage = one_pass[count]["stage_profile"]["stage_median_ms"]
                batched_stage = batched[count]["stage_profile"]["stage_median_ms"]
                self.assertLess(batched_stage["total_ms"], baseline_stage["total_ms"] * 0.45)
                self.assertLess(batched_stage["total_ms"], one_pass_stage["total_ms"] * 0.75)
                self.assertLess(batched_stage["merge_sync_ms"], baseline_stage["merge_sync_ms"] * 0.35)
                self.assertLess(batched_stage["merge_sync_ms"], one_pass_stage["merge_sync_ms"] * 0.60)

    def test_source_contains_batched_level_kernel_and_metadata_upload(self) -> None:
        api = API_CPP.read_text(encoding="utf-8")
        core = CORE_CPP.read_text(encoding="utf-8")

        self.assertIn("collect_k_bounded_i64_row_width2_merge_level", core)
        self.assertIn("g_collect_k_i64_row_width2_merge_level", api)
        self.assertIn("upload(merge_first_rows_device.ptr", api)
        self.assertIn("profile.merge_launches += 1;", api)

    def test_intake_keeps_claim_boundary_and_next_target(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("one merge-kernel launch per merge level", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("small `4097` case is slightly slower", text)
        self.assertIn("true parallel merge/compact kernel", text)


if __name__ == "__main__":
    unittest.main()
