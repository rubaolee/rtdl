from __future__ import annotations

import json
import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "run_goal1828_optix_device_column_pod_validation.py"
REPORT = ROOT / "docs" / "reports" / "goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1836_optix_cupy_whole_primitive_input_zero_copy_pod_validation.json"


class _CuPyCudaColumn:
    __module__ = "cupy"

    def __init__(self, ptr: int, dtype: str, *, stride: int) -> None:
        self._ptr = ptr
        self.dtype = dtype
        self.shape = (1,)
        self.strides = (stride,)
        self.__cuda_array_interface__ = {
            "shape": self.shape,
            "strides": self.strides,
            "typestr": "|u1",
            "data": (ptr, False),
            "version": 3,
        }

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)


class _CuPyCudaAabb:
    __module__ = "cupy"
    dtype = "float32"
    shape = (1, 6)
    strides = (24, 4)

    def __init__(self, ptr: int) -> None:
        self.__cuda_array_interface__ = {
            "shape": self.shape,
            "strides": self.strides,
            "typestr": "<f4",
            "data": (ptr, False),
            "version": 3,
        }

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)


def _cupy_ray_columns() -> dict[str, _CuPyCudaColumn]:
    base = 0xC000
    return {
        "ids": _CuPyCudaColumn(base, "uint32", stride=4),
        "ox": _CuPyCudaColumn(base + 8, "float64", stride=8),
        "oy": _CuPyCudaColumn(base + 16, "float64", stride=8),
        "dx": _CuPyCudaColumn(base + 24, "float64", stride=8),
        "dy": _CuPyCudaColumn(base + 32, "float64", stride=8),
        "tmax": _CuPyCudaColumn(base + 40, "float64", stride=8),
    }


def _cupy_triangle_columns() -> dict[str, _CuPyCudaColumn]:
    base = 0xD000
    return {
        "ids": _CuPyCudaColumn(base, "uint32", stride=4),
        "x0": _CuPyCudaColumn(base + 8, "float64", stride=8),
        "y0": _CuPyCudaColumn(base + 16, "float64", stride=8),
        "x1": _CuPyCudaColumn(base + 24, "float64", stride=8),
        "y1": _CuPyCudaColumn(base + 32, "float64", stride=8),
        "x2": _CuPyCudaColumn(base + 40, "float64", stride=8),
        "y2": _CuPyCudaColumn(base + 48, "float64", stride=8),
    }


class Goal1836OptixCuPyWholePrimitiveInputZeroCopyConformanceTest(unittest.TestCase):
    def test_runtime_accepts_cupy_byte_strides_without_copying(self) -> None:
        ray_packet = rt.pack_optix_ray_any_hit_2d_device_ray_inputs(_cupy_ray_columns())
        triangle_packet = rt.pack_optix_ray_any_hit_2d_device_triangle_zero_copy_scene_inputs(
            _cupy_triangle_columns(),
            _CuPyCudaAabb(0xE000),
        )

        self.assertEqual(ray_packet["metadata"]["source_protocols"], ("cupy",))
        self.assertEqual(triangle_packet["metadata"]["source_protocols"], ("cupy",))
        self.assertTrue(ray_packet["metadata"]["ray_columns_true_zero_copy_authorized"])
        self.assertTrue(triangle_packet["metadata"]["triangle_scene_true_zero_copy_authorized"])
        self.assertEqual(
            triangle_packet["metadata"]["transfer_mode"],
            "device_triangle_columns_aabb_zero_copy_gas_build",
        )

    def test_script_exposes_cupy_partner_mode(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("--partner", script)
        self.assertIn("_cupy_device_columns", script)
        self.assertIn('"partner": args.partner', script)
        self.assertIn("(itemsize,)", runtime)
        self.assertIn("(24, 4)", runtime)

    def test_pod_artifact_records_cupy_conformance_but_keeps_release_blocked(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], "Goal1836")
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["partner"], "cupy")
        self.assertEqual(artifact["observed_count"], artifact["expected_count"])
        self.assertEqual(artifact["ray_metadata"]["source_protocols"], ["cupy"])
        self.assertEqual(artifact["triangle_metadata"]["source_protocols"], ["cupy"])
        self.assertTrue(artifact["claim_boundary"]["ray_column_true_zero_copy_observed"])
        self.assertTrue(artifact["claim_boundary"]["triangle_scene_true_zero_copy_observed"])
        self.assertTrue(artifact["claim_boundary"]["true_zero_copy_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

    def test_report_preserves_partner_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("CuPy conformance", report)
        self.assertIn("byte strides", report)
        self.assertIn("`accept-with-boundary`", report)
        self.assertIn("v2.0 release readiness", report)
        self.assertIn("needs-more-evidence", report)


if __name__ == "__main__":
    unittest.main()
