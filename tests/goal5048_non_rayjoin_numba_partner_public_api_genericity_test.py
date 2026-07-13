from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest import mock

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class _FakeCudaUInt32Column:
    dtype = "uint32"
    shape = (4,)

    def __init__(self, ptr: int) -> None:
        self._ptr = int(ptr)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<u4",
            "data": (self._ptr, False),
            "version": 3,
            "device": 0,
        }


def _optix_cuda_available() -> bool:
    if not os.environ.get("RTDL_OPTIX_LIBRARY") and not (ROOT / "build/librtdl_optix.so").exists():
        return False
    try:
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal5048NonRayJoinNumbaPartnerPublicApiGenericityTest(unittest.TestCase):
    def test_public_api_accepts_non_rayjoin_hit_stream_columns(self) -> None:
        buffer = rt.device_column_buffer(
            {
                "ray_ids": _FakeCudaUInt32Column(0x504800),
                "primitive_ids": _FakeCudaUInt32Column(0x504880),
            },
            producer="ray_triangle_hit_stream",
            producer_consumer_stream_ordering="same_stream",
            native_device_column_output_proven_on_hardware=True,
        )

        plan = rt.numba_partner_continuation(
            operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
            input_buffer=buffer,
            input_bindings={"values": "primitive_ids"},
            scalar_inputs={"target": 7},
        )
        metadata = plan.to_metadata()

        self.assertEqual("ray_triangle_hit_stream", metadata["input_buffer"]["producer"])
        self.assertEqual({"values": "primitive_ids"}, metadata["input_bindings"])
        self.assertEqual(rt.NUMBA_UINT32_EQUAL_MASK_OPERATION, metadata["operation"])
        self.assertTrue(metadata["device_resident_candidate"])
        self.assertFalse(metadata["materializes_host_rows_for_bridge"])
        self.assertFalse(metadata["app_specific_semantics_allowed"])

        fake_output = _FakeCudaUInt32Column(0x5048C0)
        with mock.patch("rtdsl.numba_partner_api._numba_ops.numba_partner_available", return_value=True):
            with mock.patch(
                "rtdsl.numba_partner_api._RUNNERS",
                {
                    rt.NUMBA_UINT32_EQUAL_MASK_OPERATION: mock.Mock(
                        return_value={
                            "outputs": {"mask": fake_output},
                            "elapsed_sec": 0.001,
                            "host_column_materialization_used": False,
                        }
                    )
                },
            ) as runners:
                result = rt.run_numba_partner_continuation(plan)

        runners[rt.NUMBA_UINT32_EQUAL_MASK_OPERATION].assert_called_once_with(
            values=buffer.columns["primitive_ids"],
            target=7,
        )
        self.assertEqual("completed", result.status)
        self.assertFalse(result.to_metadata()["host_fallback_used"])

    def test_legacy_grouped_exports_are_not_public_partner_continuation_operations(self) -> None:
        legacy_operation_values = (
            rt.NUMBA_SEGMENTED_COUNT_I64_OPERATION,
            rt.NUMBA_SEGMENTED_SUM_F64_OPERATION,
            rt.NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION,
            rt.NUMBA_GROUPED_ARGMIN_F64_OPERATION,
            rt.NUMBA_GROUPED_ARGMAX_F64_OPERATION,
            rt.NUMBA_GROUPED_TOPK_F64_OPERATION,
        )
        public_ops = set(rt.NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS)

        for operation in legacy_operation_values:
            self.assertNotIn(operation, public_ops)
            with self.assertRaisesRegex(ValueError, "unsupported public Numba"):
                rt.numba_partner_continuation(
                    operation=operation,
                    input_buffer=rt.device_column_buffer(
                        {"values": _FakeCudaUInt32Column(0x504900)},
                        producer="generic_values",
                    ),
                    input_bindings={"values": "values"},
                )

        self.assertFalse(hasattr(rt, "device_group_by"))
        self.assertNotIn("device_group_by", rt.__all__)

    def test_ray_triangle_hit_stream_public_wrapper_executes_when_cuda_available(self) -> None:
        if not _optix_cuda_available():
            self.skipTest("OptiX + Numba CUDA runtime is not available")
        from rtdsl.reference import Ray3D, Triangle3D

        triangles = (
            Triangle3D(0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
            Triangle3D(1, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0),
            Triangle3D(2, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0),
        )
        rays = (
            Ray3D(0, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
            Ray3D(1, 2.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
            Ray3D(2, 10.0, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
        )

        with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
            hit_columns = scene.ray_triangle_hit_stream_device_columns(
                rays,
                max_rows=8,
                deduplicate_primitives=False,
            )
            row_buffer = rt.device_column_row_buffer_from_hit_stream_handoff(
                hit_columns,
                producer="goal5048_ray_triangle_hit_stream",
            )
            buffer = rt.device_column_buffer_from_row_buffer(row_buffer)
            plan = rt.numba_partner_continuation(
                operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
                input_buffer=buffer,
                input_bindings={"values": "primitive_ids"},
                scalar_inputs={"target": 1},
            )
            result = rt.run_numba_partner_continuation(plan)

        mask = result.outputs["mask"].copy_to_host().tolist()
        self.assertEqual(3, buffer.row_count)
        self.assertEqual(1, sum(bool(value) for value in mask))
        self.assertFalse(result.to_metadata()["host_fallback_used"])
        self.assertFalse(result.to_metadata()["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
