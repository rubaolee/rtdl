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
    base = 0x4000
    return {
        "ids": _CudaColumn(base, "uint32"),
        "ox": _CudaColumn(base + 8, "float64"),
        "oy": _CudaColumn(base + 16, "float64"),
        "dx": _CudaColumn(base + 24, "float64"),
        "dy": _CudaColumn(base + 32, "float64"),
        "tmax": _CudaColumn(base + 40, "float64"),
    }


class _PackedTriangles:
    count = 2


class _FakeOptixLibrary:
    def __init__(self, *, with_symbol: bool) -> None:
        self.calls = []
        if with_symbol:
            self.rtdl_optix_count_prepared_ray_anyhit_2d_device_rays = self._count

    def _count(self, handle, ids, ox, oy, dx, dy, tmax, ray_count, hit_count_out, error, error_size):
        self.calls.append((handle, ids, ox, oy, dx, dy, tmax, ray_count, error_size))
        self._ptr_value(ids)
        self._ptr_value(ox)
        self._ptr_value(oy)
        self._ptr_value(dx)
        self._ptr_value(dy)
        self._ptr_value(tmax)
        hit_count_out._obj.value = 7
        return 0

    @staticmethod
    def _ptr_value(value) -> int:
        if isinstance(value, ctypes.c_void_p):
            return int(value.value)
        return int(value)


def _prepared_scene() -> rt.PreparedOptixRayTriangleAnyHit2D:
    prepared = rt.PreparedOptixRayTriangleAnyHit2D.__new__(rt.PreparedOptixRayTriangleAnyHit2D)
    prepared._closed = False
    prepared._packed_triangles = _PackedTriangles()
    prepared._handle = ctypes.c_void_p(0xABCD)
    return prepared


class Goal1823OptixPartnerDeviceRayColumnsPartialAbiTest(unittest.TestCase):
    def test_device_ray_packet_authorizes_partial_handoff_but_not_zero_copy(self) -> None:
        packet = rt.pack_optix_ray_any_hit_2d_device_ray_inputs(_ray_columns())
        metadata = packet["metadata"]
        self.assertEqual(metadata["backend"], "optix")
        self.assertEqual(metadata["transfer_mode"], "device_ray_columns_zero_copy")
        self.assertEqual(metadata["native_symbol"], "rtdl_optix_count_prepared_ray_anyhit_2d_device_rays")
        self.assertEqual(metadata["ray_count"], 3)
        self.assertEqual(metadata["triangle_scene_transfer_mode"], "prepared_scene_existing_path")
        self.assertTrue(metadata["direct_device_pointer_observed"])
        self.assertTrue(metadata["direct_device_handoff_authorized"])
        self.assertTrue(metadata["ray_columns_true_zero_copy_authorized"])
        self.assertFalse(metadata["triangle_scene_true_zero_copy_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    def test_device_ray_packet_rejects_dtype_stride_and_device_drift(self) -> None:
        columns = _ray_columns()
        columns["ids"].dtype = "float64"
        with self.assertRaisesRegex(ValueError, "ids"):
            rt.pack_optix_ray_any_hit_2d_device_ray_inputs(columns)

        columns = _ray_columns()
        columns["ox"].strides = (2,)
        with self.assertRaisesRegex(ValueError, "contiguous"):
            rt.pack_optix_ray_any_hit_2d_device_ray_inputs(columns)

        class OtherDeviceColumn(_CudaColumn):
            def __dlpack_device__(self):
                return (2, 1)

        columns = _ray_columns()
        columns["tmax"] = OtherDeviceColumn(0x5000, "float64")
        with self.assertRaisesRegex(ValueError, "same CUDA device"):
            rt.pack_optix_ray_any_hit_2d_device_ray_inputs(columns)

    def test_prepared_scene_method_fails_closed_without_native_symbol(self) -> None:
        original_loader = optix_runtime._load_optix_library
        try:
            optix_runtime._load_optix_library = lambda: _FakeOptixLibrary(with_symbol=False)
            with self.assertRaisesRegex(RuntimeError, "Direct device-ray partner execution remains blocked"):
                _prepared_scene().count_device_rays(_ray_columns())
        finally:
            optix_runtime._load_optix_library = original_loader

    def test_prepared_scene_method_wires_to_native_symbol_when_present(self) -> None:
        fake_lib = _FakeOptixLibrary(with_symbol=True)
        original_loader = optix_runtime._load_optix_library
        try:
            optix_runtime._load_optix_library = lambda: fake_lib
            self.assertEqual(_prepared_scene().count_device_rays(_ray_columns()), 7)
        finally:
            optix_runtime._load_optix_library = original_loader
        self.assertEqual(len(fake_lib.calls), 1)
        call = fake_lib.calls[0]
        self.assertEqual(call[0].value, 0xABCD)
        self.assertEqual(call[7], 3)

    def test_native_sources_and_report_record_partial_boundary(self) -> None:
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text(encoding="utf-8")
        report = (
            ROOT / "docs/reports/goal1823_optix_partner_device_ray_columns_partial_abi_2026-05-13.md"
        ).read_text(encoding="utf-8")
        review = (
            ROOT / "docs/reviews/goal1824_gemini_review_goal1823_optix_device_ray_columns_2026-05-13.md"
        ).read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_count_prepared_ray_anyhit_2d_device_rays", api)
        self.assertIn("rtdl_optix_count_prepared_ray_anyhit_2d_device_rays", prelude)
        self.assertIn("count_prepared_ray_anyhit_2d_device_rays_optix", workloads)
        self.assertIn("pack_ray2d_device_columns", core)
        self.assertIn("true zero-copy", report.lower())
        self.assertIn("remain blocked", report)
        self.assertIn("independent audit by Gemini", review)
        self.assertIn("Goal1823: `accept-with-boundary`", review)
        self.assertIn("v2.0 Release Readiness: `needs-more-evidence`", review)


if __name__ == "__main__":
    unittest.main()
