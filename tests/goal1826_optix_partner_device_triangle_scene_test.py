from __future__ import annotations

import ctypes
import pathlib
import unittest

import rtdsl as rt
from rtdsl import optix_runtime


ROOT = pathlib.Path(__file__).resolve().parents[1]


class _CudaColumn:
    __module__ = "torch"
    requires_grad = False
    shape = (2,)
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


def _triangle_columns() -> dict[str, _CudaColumn]:
    base = 0x8000
    return {
        "ids": _CudaColumn(base, "uint32"),
        "x0": _CudaColumn(base + 8, "float64"),
        "y0": _CudaColumn(base + 16, "float64"),
        "x1": _CudaColumn(base + 24, "float64"),
        "y1": _CudaColumn(base + 32, "float64"),
        "x2": _CudaColumn(base + 40, "float64"),
        "y2": _CudaColumn(base + 48, "float64"),
    }


class _FakeOptixLibrary:
    def __init__(self, *, with_symbol: bool) -> None:
        self.calls = []
        if with_symbol:
            self.rtdl_optix_prepare_ray_anyhit_2d_device_triangles = self._prepare

    def _prepare(self, ids, x0, y0, x1, y1, x2, y2, triangle_count, prepared_out, error, error_size):
        self.calls.append((ids, x0, y0, x1, y1, x2, y2, triangle_count, error_size))
        prepared_out._obj.value = 0xD00D
        return 0


class Goal1826OptixPartnerDeviceTriangleSceneTest(unittest.TestCase):
    def test_device_triangle_packet_authorizes_partial_handoff_but_not_zero_copy(self) -> None:
        packet = rt.pack_optix_ray_any_hit_2d_device_triangle_inputs(_triangle_columns())
        metadata = packet["metadata"]
        self.assertEqual(metadata["backend"], "optix")
        self.assertEqual(metadata["transfer_mode"], "device_columns_gpu_pack_gas_build")
        self.assertEqual(metadata["native_symbol"], "rtdl_optix_prepare_ray_anyhit_2d_device_triangles")
        self.assertEqual(metadata["triangle_count"], 2)
        self.assertTrue(metadata["direct_device_pointer_observed"])
        self.assertTrue(metadata["direct_device_handoff_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    def test_device_triangle_packet_rejects_dtype_stride_and_device_drift(self) -> None:
        columns = _triangle_columns()
        columns["ids"].dtype = "float64"
        with self.assertRaisesRegex(ValueError, "ids"):
            rt.pack_optix_ray_any_hit_2d_device_triangle_inputs(columns)

        columns = _triangle_columns()
        columns["x0"].strides = (2,)
        with self.assertRaisesRegex(ValueError, "contiguous"):
            rt.pack_optix_ray_any_hit_2d_device_triangle_inputs(columns)

        class OtherDeviceColumn(_CudaColumn):
            def __dlpack_device__(self):
                return (2, 1)

        columns = _triangle_columns()
        columns["y2"] = OtherDeviceColumn(0x9000, "float64")
        with self.assertRaisesRegex(ValueError, "same CUDA device"):
            rt.pack_optix_ray_any_hit_2d_device_triangle_inputs(columns)

    def test_prepare_device_triangle_scene_fails_closed_without_native_symbol(self) -> None:
        original_loader = optix_runtime._load_optix_library
        try:
            optix_runtime._load_optix_library = lambda: _FakeOptixLibrary(with_symbol=False)
            with self.assertRaisesRegex(RuntimeError, "Direct device-triangle partner scene preparation remains blocked"):
                rt.prepare_optix_ray_triangle_any_hit_2d_device_triangles(_triangle_columns())
        finally:
            optix_runtime._load_optix_library = original_loader

    def test_prepare_device_triangle_scene_wires_to_native_symbol_when_present(self) -> None:
        fake_lib = _FakeOptixLibrary(with_symbol=True)
        original_loader = optix_runtime._load_optix_library
        try:
            optix_runtime._load_optix_library = lambda: fake_lib
            prepared = rt.prepare_optix_ray_triangle_any_hit_2d_device_triangles(_triangle_columns())
        finally:
            optix_runtime._load_optix_library = original_loader
        self.assertEqual(prepared._handle.value, 0xD00D)
        self.assertEqual(prepared._packed_triangles.count, 2)
        self.assertEqual(len(fake_lib.calls), 1)
        self.assertEqual(fake_lib.calls[0][7], 2)
        prepared._handle = ctypes.c_void_p()
        prepared._closed = True

    def test_native_sources_and_report_record_device_triangle_boundary(self) -> None:
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text(encoding="utf-8")
        report = (ROOT / "docs/reports/goal1826_optix_partner_device_triangle_scene_2026-05-13.md").read_text(
            encoding="utf-8"
        )
        review = (ROOT / "docs/reviews/goal1827_gemini_review_goal1826_optix_device_triangle_scene_2026-05-13.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("rtdl_optix_prepare_ray_anyhit_2d_device_triangles", api)
        self.assertIn("rtdl_optix_prepare_ray_anyhit_2d_device_triangles", prelude)
        self.assertIn("prepare_ray_anyhit_2d_device_triangles_optix", workloads)
        self.assertIn("pack_triangle2d_device_columns", core)
        self.assertIn("build_custom_accel_from_device_aabbs", core)
        self.assertIn("not true zero-copy", report.lower())
        self.assertIn("RTX pod validation remains required", report)
        self.assertIn("I am Gemini", review)
        self.assertIn("Verdict for Goal1826:** `accept-with-boundary`", review)
        self.assertIn("`needs-more-evidence`", review)


if __name__ == "__main__":
    unittest.main()
