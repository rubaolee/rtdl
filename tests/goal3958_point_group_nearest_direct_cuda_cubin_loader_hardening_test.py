import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_2026-06-08"
    / "goal3958_point_group_nearest_api_smoke.json"
)


class Goal3958PointGroupNearestDirectCudaCubinLoaderHardeningTest(unittest.TestCase):
    def test_point_group_nearest_helper_loaders_use_cubin(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        for file_name in (
            "point_group_nearest_split_columns_kernel.cu",
            "point_group_nearest_max_reduce_kernel.cu",
        ):
            pattern = (
                rf"compile_to_cubin\(\s*kPointGroupNearestMaxReduceKernelSrc,\s*"
                rf"\"{re.escape(file_name)}\"\s*\)"
                r"[\s\S]{0,280}?cuModuleLoadData\(&g_point_group_nearest_[^,]+,\s*cubin\.data\(\)\)"
            )
            self.assertRegex(text, pattern)

    def test_point_group_rt_pipelines_still_use_optix_ptx(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        for source_name, file_name, raygen in (
            (
                "kPointGroupNearestRtKernelSrc",
                "point_group_nearest_rt_kernel.cu",
                "__raygen__point_group_nearest_probe",
            ),
            (
                "kPointGroupThresholdRtKernelSrc",
                "point_group_threshold_rt_kernel.cu",
                "__raygen__point_group_threshold_probe",
            ),
        ):
            pattern = (
                rf"compile_to_ptx\(\s*{source_name},\s*\"{re.escape(file_name)}\"\s*\)"
                r"[\s\S]{0,420}?build_pipeline\("
                r"[\s\S]{0,220}?"
                rf"\"{re.escape(raygen)}\""
            )
            self.assertRegex(text, pattern)

    def test_point_group_nearest_helpers_left_ptx_debt_inventory(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        for file_name in (
            "point_group_nearest_split_columns_kernel.cu",
            "point_group_nearest_max_reduce_kernel.cu",
        ):
            load_blocks = re.findall(
                rf"compile_to_ptx\([^)]*\"{re.escape(file_name)}\"[^)]*\)"
                r"[\s\S]{0,280}?cuModuleLoadData\([^,]+,\s*ptx\.c_str\(\)\)",
                text,
            )
            self.assertEqual([], load_blocks)

    def test_point_group_nearest_pod_api_smoke_passed(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual("Goal3958", data["goal"])
        self.assertEqual("d9c736c5", data["source_commit_short"])
        self.assertEqual([" M src/native/optix/rtdl_optix_workloads.cpp"], data["git_status_short"])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", data["gpu"])
        self.assertEqual("point_group_nearest_split_columns_kernel.cu", data["split_columns_kernel"])
        self.assertEqual("point_group_nearest_max_reduce_kernel.cu", data["reduce_kernel"])
        self.assertTrue(data["all_checks_pass"])
        for name, value in data["checks"].items():
            with self.subTest(check=name):
                self.assertTrue(value)
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(data[flag])
        metadata = data["metadata"]
        self.assertEqual(
            "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns",
            metadata["native_symbol"],
        )
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
