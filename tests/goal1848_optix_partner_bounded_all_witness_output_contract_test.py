from __future__ import annotations

import pathlib
import json
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
RUNNER = ROOT / "scripts" / "run_goal1828_optix_device_column_pod_validation.py"
REPORT = ROOT / "docs" / "reports" / "goal1848_optix_partner_bounded_all_witness_output_contract_2026-05-13.md"
CUPY_ARTIFACT = ROOT / "docs" / "reports" / "goal1848_optix_partner_all_witness_cupy_pod_validation.json"
TORCH_ARTIFACT = ROOT / "docs" / "reports" / "goal1848_optix_partner_all_witness_torch_pod_validation.json"


class _CuPyCudaColumn:
    __module__ = "cupy"

    def __init__(self, ptr: int, dtype: str, *, shape=(1,), strides=(4,), device_id: int = 0) -> None:
        self._ptr = ptr
        self.dtype = dtype
        self.shape = shape
        self.strides = strides
        self.__cuda_array_interface__ = {
            "shape": shape,
            "strides": strides,
            "typestr": "<u4" if dtype == "uint32" else "<f8",
            "data": (ptr, False),
            "version": 3,
        }
        self._device_id = device_id

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, self._device_id)


def _cupy_ray_columns() -> dict[str, _CuPyCudaColumn]:
    base = 0x22000
    return {
        "ids": _CuPyCudaColumn(base, "uint32", shape=(2,), strides=(4,)),
        "ox": _CuPyCudaColumn(base + 8, "float64", shape=(2,), strides=(8,)),
        "oy": _CuPyCudaColumn(base + 16, "float64", shape=(2,), strides=(8,)),
        "dx": _CuPyCudaColumn(base + 24, "float64", shape=(2,), strides=(8,)),
        "dy": _CuPyCudaColumn(base + 32, "float64", shape=(2,), strides=(8,)),
        "tmax": _CuPyCudaColumn(base + 40, "float64", shape=(2,), strides=(8,)),
    }


class Goal1848OptixPartnerBoundedAllWitnessOutputContractTest(unittest.TestCase):
    def test_native_surface_defines_bounded_all_witness_contract(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        self.assertIn("g_rayanyhit_all_witnesses_device_columns", core)
        self.assertIn("RayAnyHitAllWitnessesDeviceColumnsLaunchParams", workloads)
        self.assertIn("witness_capacity", workloads)
        params_struct = workloads[
            workloads.index("struct RayAnyHitAllWitnessesDeviceColumnsLaunchParams")
            : workloads.index("struct RayAnyHitGroupFlagsLaunchParams")
        ]
        self.assertLess(
            params_struct.index("uint32_t               witness_capacity;"),
            params_struct.index("uint32_t               ray_count;"),
        )
        self.assertIn("atomicAdd(params.emitted_count, 1u)", workloads)
        self.assertIn("atomicExch(params.overflowed, 1u)", workloads)
        self.assertIn("optixIgnoreIntersection()", workloads)
        self.assertIn("rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses", api)
        self.assertIn("rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses", prelude)

    def test_python_packet_requires_matching_uint32_output_capacity_columns(self) -> None:
        rays = _cupy_ray_columns()
        witness_ray_ids = _CuPyCudaColumn(0x23000, "uint32", shape=(4,), strides=(4,))
        witness_primitive_ids = _CuPyCudaColumn(0x24000, "uint32", shape=(4,), strides=(4,))

        packet = rt.pack_optix_ray_any_hit_2d_device_all_witness_outputs(
            rays,
            witness_ray_ids,
            witness_primitive_ids,
        )
        metadata = packet["metadata"]
        self.assertEqual(metadata["transfer_mode"], "device_ray_triangle_columns_bounded_all_witness_rows_zero_copy")
        self.assertEqual(metadata["witness_row_capacity"], 4)
        self.assertIn("bounded all-hit", metadata["witness_contract"])
        self.assertTrue(metadata["witness_outputs_true_zero_copy_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

        bad_dtype = _CuPyCudaColumn(0x25000, "float32", shape=(4,), strides=(4,))
        with self.assertRaisesRegex(ValueError, "uint32"):
            rt.pack_optix_ray_any_hit_2d_device_all_witness_outputs(
                rays,
                bad_dtype,
                witness_primitive_ids,
            )

        bad_shape = _CuPyCudaColumn(0x26000, "uint32", shape=(3,), strides=(4,))
        with self.assertRaisesRegex(ValueError, "matching shapes"):
            rt.pack_optix_ray_any_hit_2d_device_all_witness_outputs(
                rays,
                witness_ray_ids,
                bad_shape,
            )

        bad_device = _CuPyCudaColumn(0x27000, "uint32", shape=(4,), strides=(4,), device_id=1)
        with self.assertRaisesRegex(ValueError, "same CUDA device"):
            rt.pack_optix_ray_any_hit_2d_device_all_witness_outputs(
                rays,
                bad_device,
                witness_primitive_ids,
            )

    def test_python_runtime_runner_and_report_keep_release_boundary(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pack_optix_ray_any_hit_2d_device_all_witness_outputs", runtime)
        self.assertIn("write_device_any_hit_all_witnesses", runtime)
        self.assertIn("pack_optix_ray_any_hit_2d_device_all_witness_outputs", init)
        self.assertIn("--output-all-witnesses", runner)
        self.assertIn("observed_all_witness_pairs_sorted", runner)
        self.assertIn("bounded_all_hit_witness_identity_observed", runner)
        self.assertIn("pass-with-boundary", report)
        self.assertIn("NVIDIA RTX A4500", report)
        self.assertIn("CuPy status: pass", report)
        self.assertIn("Torch status: pass", report)
        self.assertIn("not a v2.0 release gate pass", report)
        self.assertIn("bounded all-hit witness contract", report)

    def test_pod_artifacts_record_bounded_all_witness_identity_without_release_claim(self) -> None:
        for partner, artifact in (("cupy", CUPY_ARTIFACT), ("torch", TORCH_ARTIFACT)):
            with self.subTest(partner=partner):
                data = json.loads(artifact.read_text(encoding="utf-8"))
                self.assertEqual(data["status"], "pass")
                self.assertEqual(data["partner"], partner)
                self.assertEqual(data["device"], "NVIDIA RTX A4500")
                self.assertEqual(data["observed_count"], 2)
                self.assertEqual(data["expected_count"], 2)
                self.assertEqual(
                    data["observed_all_witness_pairs_sorted"],
                    [[101, 11], [101, 12]],
                )
                self.assertEqual(
                    data["expected_all_witness_pairs_sorted"],
                    [[101, 11], [101, 12]],
                )

                output_metadata = data["output_metadata"]
                self.assertEqual(
                    output_metadata["native_symbol"],
                    "rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses",
                )
                self.assertEqual(output_metadata["emitted_count"], 2)
                self.assertIs(output_metadata["overflowed"], False)
                self.assertIs(output_metadata["exact_row_semantics_authorized"], True)
                self.assertEqual(output_metadata["witness_row_capacity"], 4)

                boundary = data["claim_boundary"]
                self.assertIs(boundary["bounded_all_hit_witness_identity_observed"], True)
                self.assertIs(boundary["ray_column_true_zero_copy_observed"], True)
                self.assertIs(boundary["triangle_scene_true_zero_copy_observed"], True)
                self.assertIs(boundary["witness_outputs_true_zero_copy_observed"], True)
                self.assertIs(boundary["rt_core_speedup_claim_authorized"], False)
                self.assertIs(boundary["v2_0_release_authorized"], False)


if __name__ == "__main__":
    unittest.main()
