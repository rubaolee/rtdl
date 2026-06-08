import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08"
    / "goal3962_collect_k_api_smoke.json"
)


class Goal3962CollectKDirectCudaCubinLoaderHardeningTest(unittest.TestCase):
    def test_collect_k_direct_cuda_loaders_use_cubin(self) -> None:
        text = API.read_text(encoding="utf-8")
        for source_name, file_name, module_prefix in (
            (
                "kCollectKCooperativeLaunchSmokeKernelSrc",
                "collect_k_cooperative_launch_smoke_kernel.cu",
                "g_collect_k_cooperative_launch_smoke",
            ),
            (
                "kCollectKBoundedI64RowWidth2SortKernelSrc",
                "collect_k_bounded_i64_row_width2_sort_kernel.cu",
                "g_collect_k_i64_row_width2_sort",
            ),
            (
                "kCollectKBoundedI64RowWidth2CubSortKernelSrc",
                "collect_k_bounded_i64_row_width2_cub_sort_kernel.cu",
                "g_collect_k_i64_row_width2_cub_sort",
            ),
            (
                "kCollectKBoundedI64RowWidth2MergeTwoKernelSrc",
                "collect_k_bounded_i64_row_width2_merge_two_kernel.cu",
                "g_collect_k_i64_row_width2_merge_two",
            ),
            (
                "kCollectKBoundedI64RowWidth2MergeLevelKernelSrc",
                "collect_k_bounded_i64_row_width2_merge_level_kernel.cu",
                "g_collect_k_i64_row_width2_merge_level",
            ),
            (
                "kCollectKBoundedI64RowWidth2FinalCompactKernelSrc",
                "collect_k_bounded_i64_row_width2_final_compact_kernel.cu",
                "g_collect_k_i64_row_width2_final_materialize",
            ),
            (
                "kCollectKBoundedI64KernelSrc",
                "collect_k_bounded_i64_kernel.cu",
                "g_collect_k_i64",
            ),
        ):
            pattern = (
                rf"compile_to_cubin\(\s*{source_name},\s*\"{re.escape(file_name)}\""
                r"[\s\S]{0,180}?\)"
                rf"[\s\S]{{0,320}}?cuModuleLoadData\(&{module_prefix}\.module,\s*cubin\.data\(\)\)"
            )
            self.assertRegex(text, pattern)

    def test_collect_k_cooperative_cubin_does_not_use_ptx_rdc_option(self) -> None:
        text = API.read_text(encoding="utf-8")
        pattern = (
            r"compile_to_cubin\(\s*kCollectKCooperativeLaunchSmokeKernelSrc,\s*"
            r"\"collect_k_cooperative_launch_smoke_kernel\.cu\"\s*\)"
        )
        self.assertRegex(text, pattern)
        self.assertNotIn(
            'compile_to_cubin(\n                kCollectKCooperativeLaunchSmokeKernelSrc,\n'
            '                "collect_k_cooperative_launch_smoke_kernel.cu",\n'
            '                {"--relocatable-device-code=true"})',
            text,
        )

    def test_collect_k_left_direct_ptx_debt_inventory(self) -> None:
        text = API.read_text(encoding="utf-8")
        for file_name in (
            "collect_k_cooperative_launch_smoke_kernel.cu",
            "collect_k_bounded_i64_row_width2_sort_kernel.cu",
            "collect_k_bounded_i64_row_width2_cub_sort_kernel.cu",
            "collect_k_bounded_i64_row_width2_merge_two_kernel.cu",
            "collect_k_bounded_i64_row_width2_merge_level_kernel.cu",
            "collect_k_bounded_i64_row_width2_final_compact_kernel.cu",
            "collect_k_bounded_i64_kernel.cu",
        ):
            load_blocks = re.findall(
                rf"compile_to_ptx\([^)]*\"{re.escape(file_name)}\"[^)]*\)"
                r"[\s\S]{0,320}?cuModuleLoadData\([^,]+,\s*ptx\.c_str\(\)\)",
                text,
            )
            self.assertEqual([], load_blocks)

    def test_collect_k_pod_api_smoke_passed(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual("Goal3962", data["goal"])
        self.assertEqual("e704d1d8", data["source_commit_short"])
        self.assertEqual([" M src/native/optix/rtdl_optix_api.cpp"], data["git_status_short"])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", data["gpu"])
        self.assertTrue(data["all_checks_pass"])
        expected_cases = {
            "row_width2_small_bitonic": 1024,
            "row_width2_tiled_cub_merge_final": 8192,
            "dynamic_row_width3_fallback": 257,
        }
        cases = {case["case"]: case for case in data["collect_cases"]}
        self.assertEqual(set(expected_cases), set(cases))
        for case_name, expected_count in expected_cases.items():
            with self.subTest(case=case_name):
                case = cases[case_name]
                self.assertTrue(case["all_checks_pass"])
                self.assertEqual(expected_count, case["valid_count"])
                for check_name, check_value in case["checks"].items():
                    self.assertTrue(check_value, check_name)

        cooperative = data["cooperative_smoke"]
        self.assertTrue(cooperative["all_checks_pass"])
        self.assertEqual(0, cooperative["status"])
        self.assertEqual(2, cooperative["observed_blocks"])
        self.assertEqual(2, cooperative["sync_observed_blocks"])
        self.assertEqual("", cooperative["error"])
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(data[flag])


if __name__ == "__main__":
    unittest.main()
