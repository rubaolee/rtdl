from __future__ import annotations

import pathlib
import unittest
import json

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal1831_optix_ray_column_true_zero_copy_slice_2026-05-13.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1831_optix_ray_column_true_zero_copy_pod_validation.json"


class _CudaColumn:
    __module__ = "torch"
    requires_grad = False
    shape = (3,)
    strides = (1,)

    def __init__(self, ptr: int, dtype: str) -> None:
        self._ptr = ptr
        self.dtype = dtype

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)

    def data_ptr(self):
        return self._ptr


def _ray_columns() -> dict[str, _CudaColumn]:
    base = 0xA000
    return {
        "ids": _CudaColumn(base, "uint32"),
        "ox": _CudaColumn(base + 8, "float64"),
        "oy": _CudaColumn(base + 16, "float64"),
        "dx": _CudaColumn(base + 24, "float64"),
        "dy": _CudaColumn(base + 32, "float64"),
        "tmax": _CudaColumn(base + 40, "float64"),
    }


class Goal1831OptixRayColumnTrueZeroCopySliceTest(unittest.TestCase):
    def test_python_metadata_authorizes_only_ray_column_zero_copy(self) -> None:
        packet = rt.pack_optix_ray_any_hit_2d_device_ray_inputs(_ray_columns())
        metadata = packet["metadata"]
        self.assertEqual(metadata["transfer_mode"], "device_ray_columns_zero_copy")
        self.assertTrue(metadata["ray_columns_true_zero_copy_authorized"])
        self.assertFalse(metadata["triangle_scene_true_zero_copy_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    def test_native_device_ray_entrypoint_uses_column_raygen_not_pack_kernel(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("g_rayanyhit_count_device_ray_columns", core)
        self.assertIn("RayAnyHitCountDeviceRayColumnsLaunchParams", workloads)
        self.assertIn("load_ray_column(idx)", workloads)
        self.assertIn("load_ray_column(ridx)", workloads)
        function_start = workloads.index("static void count_prepared_ray_anyhit_2d_device_rays_optix")
        function_end = workloads.index("static void group_flags_prepared_ray_anyhit_2d_packed_optix")
        function_body = workloads[function_start:function_end]
        self.assertIn("ensure_ray_anyhit_count_device_ray_columns_2d_pipeline", function_body)
        self.assertIn("g_rayanyhit_count_device_ray_columns.pipe->pipeline", function_body)
        self.assertNotIn("ensure_pack_ray2d_device_columns_kernel", function_body)
        self.assertNotIn("g_partner_ray2d_pack.fn", function_body)
        self.assertNotIn("DevPtr d_rays", function_body)

    def test_runtime_and_report_preserve_whole_primitive_boundary(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("ray-side true zero-copy path", runtime)
        self.assertIn("whole-primitive zero-copy is not implied", runtime)
        self.assertIn("`accept-with-boundary`", report)
        self.assertIn("ray-side true zero-copy", report)
        self.assertIn("whole-primitive true zero-copy", report)
        self.assertIn("v2.0 release readiness", report)

    def test_pod_artifact_records_ray_column_zero_copy_without_broad_claim(self) -> None:
        artifact = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal1831")
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["device"], "NVIDIA RTX A4500")
        self.assertEqual(artifact["observed_count"], artifact["expected_count"])
        self.assertTrue(artifact["claim_boundary"]["direct_device_column_execution_observed"])
        self.assertTrue(artifact["claim_boundary"]["ray_column_true_zero_copy_observed"])
        self.assertFalse(artifact["claim_boundary"]["whole_primitive_true_zero_copy_authorized"])
        self.assertFalse(artifact["claim_boundary"]["true_zero_copy_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])
        self.assertEqual(artifact["ray_metadata"]["transfer_mode"], "device_ray_columns_zero_copy")
        self.assertTrue(artifact["ray_metadata"]["ray_columns_true_zero_copy_authorized"])
        self.assertFalse(artifact["ray_metadata"]["triangle_scene_true_zero_copy_authorized"])
        self.assertEqual(artifact["triangle_metadata"]["transfer_mode"], "device_columns_gpu_pack_gas_build")


if __name__ == "__main__":
    unittest.main()
