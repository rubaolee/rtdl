from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1529_v1_5_4_optix_collect_k_one_pass_merge_intake_2026-05-08.md"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json"
ONE_PASS_JSON = ROOT / "docs" / "reports" / "goal1529_v1_5_4_optix_collect_k_one_pass_merge_probe_2026-05-08.json"
CORE_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE_H = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"


class Goal1529V154OptixCollectKOnePassMergeIntakeTest(unittest.TestCase):
    def test_probe_keeps_goal1506_accepted_shape(self) -> None:
        data = json.loads(ONE_PASS_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        self.assertEqual([case["candidate_count"] for case in data["cases"]], [4097, 65537, 131072])
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertEqual(case["expected_native_path"], "row_width2_bounded_multi_tile_sort_merge")
                self.assertIs(case["profile_native_path_matches_expected"], True)
                self.assertIs(case["profile_topology_matches_expected"], True)
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])

    def test_long_count_merge_and_total_time_improve_against_baseline(self) -> None:
        baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
        one_pass = json.loads(ONE_PASS_JSON.read_text(encoding="utf-8"))

        by_count = {case["candidate_count"]: case for case in one_pass["cases"]}
        for baseline_case in baseline["cases"]:
            count = baseline_case["candidate_count"]
            if count < 65537:
                continue
            with self.subTest(candidate_count=count):
                one_pass_case = by_count[count]
                baseline_stage = baseline_case["stage_profile"]["stage_median_ms"]
                one_pass_stage = one_pass_case["stage_profile"]["stage_median_ms"]
                self.assertLess(one_pass_stage["total_ms"], baseline_stage["total_ms"] * 0.70)
                self.assertLess(one_pass_stage["merge_sync_ms"], baseline_stage["merge_sync_ms"] * 0.60)

    def test_source_uses_one_pass_merge_without_thrust_experiment(self) -> None:
        core = CORE_CPP.read_text(encoding="utf-8")
        api = API_CPP.read_text(encoding="utf-8")
        prelude = PRELUDE_H.read_text(encoding="utf-8")

        self.assertIn("rows_out[unique_count * 2] = value0;", core)
        self.assertIn("*overflowed = unique_count > row_capacity ? 1u : 0u;", core)
        self.assertNotIn("row_width2_thrust_sort_unique_experimental", api)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_USE_THRUST_SORT_UNIQUE", api)
        self.assertNotIn("#include <thrust/", prelude)

    def test_intake_records_boundary_and_next_bottleneck(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("count-and-write in one pass", text)
        self.assertIn("does not publish Goal 69/70-era speedup wording", text)
        self.assertIn("remaining long-count bottleneck is still merge synchronization time", text)
        self.assertIn("genuinely parallel merge/compact design", text)


if __name__ == "__main__":
    unittest.main()
