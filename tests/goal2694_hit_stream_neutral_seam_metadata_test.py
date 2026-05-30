from __future__ import annotations

import unittest

import rtdsl as rt


class _FakeCudaDevice:
    type = "cuda"
    index = 0


class _FakeCudaInt64Column:
    dtype = "int64"
    shape = (2,)
    device = _FakeCudaDevice()

    def __init__(self, values) -> None:
        self._values = tuple(values)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (0xA000, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0xA000

    def tolist(self):
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


class _FakeCudaFloat64Column:
    dtype = "float64"
    shape = (2,)
    device = _FakeCudaDevice()

    def __init__(self, values) -> None:
        self._values = tuple(values)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (0xB000, False),
            "version": 3,
        }

    def data_ptr(self):
        return 0xB000

    def tolist(self):
        return list(self._values)

    def __iter__(self):
        return iter(self._values)


class Goal2694HitStreamNeutralSeamMetadataTest(unittest.TestCase):
    def test_host_bridge_hit_stream_records_host_stage_neutral_seams(self) -> None:
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=(0, 1),
            primitive_ids=(0, 1),
            row_count=2,
            capacity=2,
            backend="cpu",
        )
        bridged = rt.RtdlHitStreamColumnHandoff(
            ray_ids=hit_columns.ray_ids,
            primitive_ids=hit_columns.primitive_ids,
            row_count=2,
            capacity=2,
            overflow=False,
            backend="cpu",
            source_mode="host_rows_to_columns_bridge",
            phase_timing_seconds={},
            materializes_host_rows_for_bridge=True,
        )
        metadata = bridged.to_metadata()
        seams = metadata["neutral_buffer_seams"]

        self.assertEqual(metadata["neutral_buffer_seam_contract_version"], rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION)
        self.assertEqual({seam["transfer_status"] for seam in seams}, {"host_stage"})
        self.assertTrue(all(seam["host_materialized_before_handoff"] for seam in seams))
        self.assertFalse(any(seam["zero_copy_claim_authorized"] for seam in seams))
        self.assertFalse(metadata["removes_host_materialization_bottleneck"])

    def test_cuda_native_hit_stream_records_borrowed_unmeasured_not_zero_copy(self) -> None:
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=_FakeCudaInt64Column((0, 1)),
            primitive_ids=_FakeCudaInt64Column((0, 1)),
            row_count=2,
            capacity=2,
            backend="optix",
        )
        metadata = hit_columns.to_metadata()
        seams = metadata["neutral_buffer_seams"]

        self.assertEqual({seam["transfer_status"] for seam in seams}, {"borrowed_device_pointer_unmeasured"})
        self.assertTrue(all(seam["device_resident"] for seam in seams))
        self.assertTrue(all(seam["native_producer"] for seam in seams))
        self.assertEqual({seam["lifetime_state"] for seam in seams}, {"native_owned_pending_state_machine"})
        self.assertFalse(any(seam["zero_copy_claim_authorized"] for seam in seams))
        self.assertFalse(any(seam["native_device_output_promotion_ready"] for seam in seams))
        self.assertFalse(metadata["removes_host_materialization_bottleneck"])

    def test_payload_columns_and_gather_publish_neutral_handoff_summary(self) -> None:
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=_FakeCudaInt64Column((0, 1)),
            primitive_ids=_FakeCudaInt64Column((0, 1)),
            row_count=2,
            capacity=2,
            backend="optix",
        )
        payload_columns = rt.RtdlTypedPrimitivePayloadColumns(
            primitive_group_ids=_FakeCudaInt64Column((3, 4)),
            primitive_values=_FakeCudaFloat64Column((10.0, 20.0)),
            primitive_count=2,
            group_count=5,
            source_mode="typed_payload_columns",
            group_id_bounds_validation="caller_asserted",
        )

        payload_metadata = payload_columns.to_metadata()
        self.assertEqual(payload_metadata["neutral_buffer_seam_contract_version"], rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION)
        self.assertEqual(
            {seam["transfer_status"] for seam in payload_metadata["neutral_buffer_seams"]},
            {"borrowed_device_pointer_unmeasured"},
        )
        self.assertFalse(any(seam["zero_copy_claim_authorized"] for seam in payload_metadata["neutral_buffer_seams"]))

        continuation_inputs, metadata = rt.gather_typed_payload_columns_for_hit_stream(
            hit_columns,
            payload_columns,
        )
        summary = metadata["neutral_buffer_handoff_summary"]

        self.assertEqual(continuation_inputs["group_ids"], (3, 4))
        self.assertEqual(summary["contract_version"], rt.V2_5_NEUTRAL_BUFFER_SEAM_VERSION)
        self.assertEqual(summary["hit_stream_transfer_statuses"], ("borrowed_device_pointer_unmeasured",) * 2)
        self.assertEqual(summary["payload_transfer_statuses"], ("borrowed_device_pointer_unmeasured",) * 2)
        self.assertFalse(summary["any_zero_copy_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
