from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal1845_optix_partner_witness_output_contract_2026-05-13.md"


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
    base = 0x12000
    return {
        "ids": _CuPyCudaColumn(base, "uint32", shape=(2,), strides=(4,)),
        "ox": _CuPyCudaColumn(base + 8, "float64", shape=(2,), strides=(8,)),
        "oy": _CuPyCudaColumn(base + 16, "float64", shape=(2,), strides=(8,)),
        "dx": _CuPyCudaColumn(base + 24, "float64", shape=(2,), strides=(8,)),
        "dy": _CuPyCudaColumn(base + 32, "float64", shape=(2,), strides=(8,)),
        "tmax": _CuPyCudaColumn(base + 40, "float64", shape=(2,), strides=(8,)),
    }


class Goal1845OptixPartnerWitnessOutputContractTest(unittest.TestCase):
    def test_native_surface_defines_partner_owned_witness_output_contract(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        self.assertIn("g_rayanyhit_witness_device_columns", core)
        self.assertIn("RayAnyHitWitnessDeviceColumnsLaunchParams", workloads)
        self.assertIn("witness_ray_ids", workloads)
        self.assertIn("witness_primitive_ids", workloads)
        self.assertIn("optixSetPayload_2(t.id)", workloads)
        self.assertIn("0xFFFFFFFFu", workloads)
        self.assertIn("rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses", api)
        self.assertIn("rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses", prelude)

    def test_python_packet_requires_two_uint32_same_device_output_columns(self) -> None:
        rays = _cupy_ray_columns()
        witness_ray_ids = _CuPyCudaColumn(0x13000, "uint32", shape=(2,), strides=(4,))
        witness_primitive_ids = _CuPyCudaColumn(0x14000, "uint32", shape=(2,), strides=(4,))

        packet = rt.pack_optix_ray_any_hit_2d_device_witness_outputs(
            rays,
            witness_ray_ids,
            witness_primitive_ids,
        )
        metadata = packet["metadata"]
        self.assertEqual(metadata["transfer_mode"], "device_ray_triangle_columns_witness_rows_zero_copy")
        self.assertEqual(metadata["witness_row_capacity"], 2)
        self.assertEqual(metadata["witness_no_hit_primitive_id"], 0xFFFFFFFF)
        self.assertIn("not all-hit collection", metadata["witness_contract"])
        self.assertTrue(metadata["witness_outputs_true_zero_copy_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

        bad_dtype = _CuPyCudaColumn(0x15000, "float32", shape=(2,), strides=(4,))
        with self.assertRaisesRegex(ValueError, "uint32"):
            rt.pack_optix_ray_any_hit_2d_device_witness_outputs(
                rays,
                bad_dtype,
                witness_primitive_ids,
            )

        bad_shape = _CuPyCudaColumn(0x16000, "uint32", shape=(1,), strides=(4,))
        with self.assertRaisesRegex(ValueError, "shape"):
            rt.pack_optix_ray_any_hit_2d_device_witness_outputs(
                rays,
                witness_ray_ids,
                bad_shape,
            )

    def test_python_runtime_exposes_method_and_report_keeps_boundary(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pack_optix_ray_any_hit_2d_device_witness_outputs", runtime)
        self.assertIn("write_device_any_hit_witnesses", runtime)
        self.assertIn("first-hit witness", report)
        self.assertIn("not the full multi-hit", report)
        self.assertIn("segment/polygon row collector", report)
        self.assertIn("v2.0 release readiness", report)
        self.assertIn("needs-more-evidence", report)


if __name__ == "__main__":
    unittest.main()
