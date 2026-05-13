from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl import optix_runtime


class _CudaColumn:
    __module__ = "torch"
    requires_grad = False
    dtype = "float64"
    shape = (2,)
    strides = (1,)

    def __init__(self, ptr: int) -> None:
        self._ptr = ptr

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)

    def data_ptr(self):
        return self._ptr


def _device_columns():
    ptr = 0x1000
    rays = {name: _CudaColumn(ptr + index) for index, name in enumerate(("ids", "ox", "oy", "dx", "dy", "tmax"))}
    triangles = {
        name: _CudaColumn(ptr + 100 + index)
        for index, name in enumerate(("ids", "x0", "y0", "x1", "y1", "x2", "y2"))
    }
    return rays, triangles


class _FakeOptixLibrary:
    pass


class Goal1821OptixPartnerDeviceDescriptorFailClosedTest(unittest.TestCase):
    def test_device_descriptor_packet_observes_pointers_without_authorizing_claims(self) -> None:
        rays, triangles = _device_columns()
        packet = rt.pack_optix_ray_triangle_any_hit_2d_device_descriptor_inputs(rays, triangles)
        metadata = packet["metadata"]
        self.assertEqual(metadata["backend"], "optix")
        self.assertEqual(metadata["transfer_mode"], "device_descriptor_only")
        self.assertEqual(metadata["ray_count"], 2)
        self.assertEqual(metadata["triangle_count"], 2)
        self.assertEqual(metadata["source_protocols"], ("torch",))
        self.assertEqual(metadata["source_devices"], ("cuda:0",))
        self.assertTrue(metadata["direct_device_pointer_observed"])
        self.assertFalse(metadata["direct_device_handoff_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertIn("descriptor_validation", metadata["partner_phase_timings_s"])
        self.assertEqual(packet["rays"]["ids"].data_ptr, 0x1000)

    def test_device_descriptor_packet_rejects_cpu_columns_and_shape_drift(self) -> None:
        rays, triangles = _device_columns()

        class CpuColumn(_CudaColumn):
            def __dlpack_device__(self):
                return (1, 0)

        rays["ids"] = CpuColumn(0x2000)
        with self.assertRaisesRegex(ValueError, "requires a CUDA partner tensor"):
            rt.pack_optix_ray_triangle_any_hit_2d_device_descriptor_inputs(rays, triangles)

        rays, triangles = _device_columns()
        rays["ids"].shape = (2, 1)
        rays["ids"].strides = (1, 1)
        with self.assertRaisesRegex(ValueError, "one-dimensional"):
            rt.pack_optix_ray_triangle_any_hit_2d_device_descriptor_inputs(rays, triangles)

    def test_run_path_fails_closed_without_native_device_column_symbol(self) -> None:
        rays, triangles = _device_columns()
        original_loader = optix_runtime._load_optix_library
        try:
            optix_runtime._load_optix_library = lambda: _FakeOptixLibrary()
            with self.assertRaisesRegex(RuntimeError, "Direct device-pointer partner execution remains blocked"):
                rt.run_optix_partner_ray_triangle_any_hit_2d_device_descriptors(rays, triangles)
        finally:
            optix_runtime._load_optix_library = original_loader


if __name__ == "__main__":
    unittest.main()
