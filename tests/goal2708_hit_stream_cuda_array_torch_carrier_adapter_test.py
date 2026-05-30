import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


def _raw_native_hit_columns() -> rt.RtdlHitStreamColumnHandoff:
    return rt.prepare_native_device_hit_stream_columns_from_abi(
        ray_ids_device_ptr=0x1000,
        primitive_ids_device_ptr=0x2000,
        row_count=2,
        capacity=2,
        overflow=False,
        hit_event_count=2,
        device_id=0,
    )


def _raw_payload_columns() -> rt.RtdlTypedPrimitivePayloadColumns:
    return rt.RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=rt.RtdlRawCudaColumn(
            "primitive_group_ids",
            "int64",
            0x3000,
            2,
        ),
        primitive_values=rt.RtdlRawCudaColumn(
            "primitive_values",
            "float64",
            0x4000,
            2,
        ),
        primitive_count=2,
        group_count=2,
        source_mode="typed_payload_columns",
        group_id_bounds_validation="deferred_device_check",
    )


class Goal2708HitStreamCudaArrayTorchCarrierAdapterTest(unittest.TestCase):
    def test_raw_cuda_columns_have_explicit_torch_carrier_adapter_plan(self) -> None:
        plan = rt.describe_v2_5_hit_stream_torch_carrier_adapter(
            _raw_native_hit_columns(),
            _raw_payload_columns(),
        )

        self.assertTrue(plan["all_columns_adaptable_to_torch_carrier"])
        self.assertTrue(plan["all_columns_no_copy_torch_carrier_candidates"])
        self.assertTrue(plan["raw_cuda_adapter_required"])
        self.assertTrue(plan["requires_torch_runtime"])
        self.assertTrue(plan["requires_cupy_for_cuda_array_interface_without_dlpack"])
        self.assertFalse(plan["host_copy_required"])
        self.assertFalse(plan["true_zero_copy_authorized"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertFalse(plan["adapter_execution_proven_on_hardware"])

        modes = {column["adapter_mode"] for column in plan["columns"]}
        self.assertEqual(modes, {"cuda_array_interface_to_torch_via_dlpack"})
        self.assertEqual(
            [column["data_ptr"] for column in plan["columns"]],
            [0x2000, 0x3000, 0x4000],
        )

    def test_host_columns_require_explicit_copy_for_triton_carrier(self) -> None:
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=(0, 1),
            primitive_ids=(0, 1),
            row_count=2,
            capacity=2,
            backend="optix",
        )
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            (0, 1),
            (10.0, 20.0),
            group_count=2,
        )

        plan = rt.describe_v2_5_hit_stream_torch_carrier_adapter(hit_columns, payload_columns)

        self.assertTrue(plan["all_columns_adaptable_to_torch_carrier"])
        self.assertFalse(plan["all_columns_no_copy_torch_carrier_candidates"])
        self.assertTrue(plan["host_copy_required"])
        self.assertTrue(plan["explicit_copy_required"])
        self.assertEqual(
            {column["adapter_mode"] for column in plan["columns"]},
            {"host_column_requires_explicit_copy"},
        )

        with self.assertRaisesRegex(ValueError, "pass allow_explicit_copy=True"):
            rt.gather_typed_payload_columns_for_hit_stream(
                hit_columns,
                payload_columns,
                partner="triton",
            )

    def test_adapter_runtime_uses_dlpack_and_cupy_without_public_export(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "hit_stream_handoff.py").read_text()

        self.assertIn("torch.from_dlpack", source)
        self.assertIn("cupy.asarray", source)
        self.assertIn("cuda_array_interface_to_torch_via_dlpack", source)
        self.assertTrue(hasattr(rt, "describe_v2_5_hit_stream_torch_carrier_adapter"))
        self.assertNotIn("describe_v2_5_hit_stream_torch_carrier_adapter", rt.__all__)


if __name__ == "__main__":
    unittest.main()
