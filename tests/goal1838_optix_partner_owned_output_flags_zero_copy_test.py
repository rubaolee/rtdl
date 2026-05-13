from __future__ import annotations

import json
import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "run_goal1828_optix_device_column_pod_validation.py"
REPORT = ROOT / "docs" / "reports" / "goal1838_optix_partner_owned_output_flags_zero_copy_2026-05-13.md"
CUPY_ARTIFACT = ROOT / "docs" / "reports" / "goal1838_optix_partner_owned_output_flags_pod_validation.json"
TORCH_ARTIFACT = ROOT / "docs" / "reports" / "goal1838_optix_partner_owned_output_flags_torch_pod_validation.json"


class _CuPyCudaColumn:
    __module__ = "cupy"

    def __init__(self, ptr: int, dtype: str, *, shape=(1,), strides=(4,)) -> None:
        self._ptr = ptr
        self.dtype = dtype
        self.shape = shape
        self.strides = strides
        self.__cuda_array_interface__ = {
            "shape": shape,
            "strides": strides,
            "typestr": "|u1",
            "data": (ptr, False),
            "version": 3,
        }

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)


def _cupy_ray_columns() -> dict[str, _CuPyCudaColumn]:
    base = 0xF000
    return {
        "ids": _CuPyCudaColumn(base, "uint32", strides=(4,)),
        "ox": _CuPyCudaColumn(base + 8, "float64", strides=(8,)),
        "oy": _CuPyCudaColumn(base + 16, "float64", strides=(8,)),
        "dx": _CuPyCudaColumn(base + 24, "float64", strides=(8,)),
        "dy": _CuPyCudaColumn(base + 32, "float64", strides=(8,)),
        "tmax": _CuPyCudaColumn(base + 40, "float64", strides=(8,)),
    }


class Goal1838OptixPartnerOwnedOutputFlagsZeroCopyTest(unittest.TestCase):
    def test_native_and_python_surface_define_partner_owned_output_path(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("g_rayanyhit_flags_device_columns", core)
        self.assertIn("RayAnyHitFlagsDeviceColumnsLaunchParams", workloads)
        self.assertIn("params.any_hit_flags[idx] = p1 ? 1u : 0u;", workloads)
        self.assertIn("write_prepared_ray_anyhit_2d_device_flags_optix", workloads)
        self.assertIn("rtdl_optix_write_prepared_ray_anyhit_2d_device_flags", api)
        self.assertIn("rtdl_optix_write_prepared_ray_anyhit_2d_device_flags", prelude)
        self.assertIn("pack_optix_ray_any_hit_2d_device_output_flags", runtime)
        self.assertIn("write_device_any_hit_flags", runtime)
        self.assertIn("--output-flags", script)

    def test_output_packet_accepts_only_same_device_contiguous_uint32(self) -> None:
        output = _CuPyCudaColumn(0xFA00, "uint32", shape=(1,), strides=(4,))
        packet = rt.pack_optix_ray_any_hit_2d_device_output_flags(_cupy_ray_columns(), output)
        metadata = packet["metadata"]

        self.assertEqual(metadata["source_protocols"], ("cupy",))
        self.assertEqual(metadata["transfer_mode"], "device_ray_triangle_columns_output_flags_zero_copy")
        self.assertTrue(metadata["output_flags_true_zero_copy_authorized"])

        bad_output = _CuPyCudaColumn(0xFB00, "float32", shape=(1,), strides=(4,))
        with self.assertRaisesRegex(ValueError, "uint32"):
            rt.pack_optix_ray_any_hit_2d_device_output_flags(_cupy_ray_columns(), bad_output)

        bad_output = _CuPyCudaColumn(0xFC00, "uint32", shape=(1,), strides=(8,))
        with self.assertRaisesRegex(ValueError, "contiguous"):
            rt.pack_optix_ray_any_hit_2d_device_output_flags(_cupy_ray_columns(), bad_output)

    def test_pod_artifacts_record_torch_and_cupy_output_zero_copy(self) -> None:
        for artifact_path, partner in ((CUPY_ARTIFACT, "cupy"), (TORCH_ARTIFACT, "torch")):
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
            self.assertEqual(artifact["status"], "pass")
            self.assertEqual(artifact["partner"], partner)
            self.assertEqual(artifact["observed_flags"], [1, 0])
            self.assertEqual(artifact["observed_count"], artifact["expected_count"])
            self.assertEqual(artifact["output_metadata"]["source_protocols"], [partner])
            self.assertTrue(artifact["claim_boundary"]["ray_column_true_zero_copy_observed"])
            self.assertTrue(artifact["claim_boundary"]["triangle_scene_true_zero_copy_observed"])
            self.assertTrue(artifact["claim_boundary"]["output_flags_true_zero_copy_observed"])
            self.assertTrue(artifact["claim_boundary"]["true_zero_copy_authorized"])
            self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
            self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

    def test_report_preserves_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("`accept-with-boundary`", report)
        self.assertIn("partner-owned output", report)
        self.assertIn("observed_flags", report)
        self.assertIn("v2.0 release readiness", report)
        self.assertIn("needs-more-evidence", report)


if __name__ == "__main__":
    unittest.main()
