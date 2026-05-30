import unittest

import rtdsl as rt
from rtdsl import optix_runtime


class Goal2704NativeHitStreamOutputAbiContractTest(unittest.TestCase):
    def test_native_output_abi_is_generic_and_claim_bounded(self) -> None:
        contract = rt.describe_v2_5_native_hit_stream_output_abi("optix")

        self.assertEqual(contract["contract_version"], rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION)
        self.assertEqual(
            contract["native_output_abi_symbol"],
            "rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns",
        )
        self.assertEqual(
            tuple(contract["native_output_abi_fields"]),
            rt.GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_FIELDS,
        )
        self.assertEqual(tuple(contract["hit_stream_columns"]), rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS)
        self.assertEqual(contract["overflow_policy"], "fail_closed_bounded_columns")
        self.assertTrue(contract["requires_native_release_entrypoint"])
        self.assertTrue(contract["requires_same_pointer_no_host_stage_measurement"])
        self.assertTrue(contract["requires_sm70_pod_validation_for_triton"])
        self.assertFalse(contract["native_engine_app_specific_vocab_allowed"])
        self.assertFalse(contract["host_row_materialization_allowed_for_promotion"])
        self.assertFalse(contract["true_zero_copy_claim_authorized"])
        self.assertFalse(contract["public_speedup_claim_authorized"])

        serialized = repr(contract).lower()
        for forbidden in ("raydb", "sql", "database", "table", "dbscan", "hausdorff"):
            self.assertNotIn(forbidden, serialized)

    def test_raw_cuda_abi_output_wraps_as_native_device_columns_without_promotion(self) -> None:
        hit_columns = rt.prepare_native_device_hit_stream_columns_from_abi(
            ray_ids_device_ptr=0x1000,
            primitive_ids_device_ptr=0x2000,
            row_count=3,
            capacity=4,
            overflow=False,
            hit_event_count=5,
            device_id=0,
            traversal_seconds=0.001,
        )
        metadata = hit_columns.to_metadata()

        self.assertEqual(hit_columns.source_mode, "native_device_columns")
        self.assertTrue(metadata["device_resident"])
        self.assertFalse(metadata["materializes_host_rows_for_bridge"])
        self.assertFalse(metadata["host_hit_rows_materialized_before_handoff"])
        self.assertTrue(metadata["device_resident_but_unproven_native_output"])
        self.assertFalse(metadata["native_device_column_output_proven_on_hardware"])
        self.assertFalse(metadata["removes_host_materialization_bottleneck"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertEqual(metadata["phase_timing_seconds"]["rt_traversal"], 0.001)

        seams = metadata["neutral_buffer_seams"]
        self.assertEqual({seam["transfer_status"] for seam in seams}, {"borrowed_device_pointer_unmeasured"})
        self.assertTrue(all(seam["native_producer"] for seam in seams))
        self.assertTrue(all(seam["device_resident"] for seam in seams))
        self.assertTrue(all(seam["lifetime_state"] == "native_owned_pending_state_machine" for seam in seams))
        self.assertFalse(any(seam["zero_copy_claim_authorized"] for seam in seams))

    def test_hardware_proof_flag_still_requires_cuda_columns(self) -> None:
        hit_columns = rt.prepare_native_device_hit_stream_columns_from_abi(
            ray_ids_device_ptr=0x3000,
            primitive_ids_device_ptr=0x4000,
            row_count=1,
            capacity=1,
            overflow=False,
            native_device_column_output_proven_on_hardware=True,
        )

        self.assertTrue(hit_columns.to_metadata()["native_device_column_output_proven_on_hardware"])
        self.assertTrue(hit_columns.to_metadata()["removes_host_materialization_bottleneck"])
        self.assertFalse(hit_columns.to_metadata()["true_zero_copy_authorized"])

    def test_abi_wrapper_fails_closed_for_bad_or_overflowed_outputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "row_count cannot exceed capacity"):
            rt.prepare_native_device_hit_stream_columns_from_abi(
                ray_ids_device_ptr=0x1000,
                primitive_ids_device_ptr=0x2000,
                row_count=5,
                capacity=4,
                overflow=False,
            )
        with self.assertRaisesRegex(ValueError, "fail closed"):
            rt.prepare_native_device_hit_stream_columns_from_abi(
                ray_ids_device_ptr=0x1000,
                primitive_ids_device_ptr=0x2000,
                row_count=1,
                capacity=1,
                overflow=True,
            )
        with self.assertRaisesRegex(ValueError, "ray_ids_device_ptr must be non-zero"):
            rt.prepare_native_device_hit_stream_columns_from_abi(
                ray_ids_device_ptr=0,
                primitive_ids_device_ptr=0x2000,
                row_count=1,
                capacity=1,
                overflow=False,
            )

    def test_empty_overflowed_output_can_be_described_without_pointers(self) -> None:
        hit_columns = rt.prepare_native_device_hit_stream_columns_from_abi(
            ray_ids_device_ptr=0,
            primitive_ids_device_ptr=0,
            row_count=0,
            capacity=8,
            overflow=True,
        )

        self.assertTrue(hit_columns.overflow)
        self.assertEqual(hit_columns.row_count, 0)
        self.assertEqual(hit_columns.capacity, 8)

    def test_native_output_owner_close_delegates_to_runtime_owner(self) -> None:
        class _Owner:
            def __init__(self) -> None:
                self.closed = False

            def close(self) -> None:
                self.closed = True

        owner = _Owner()
        native_output = rt.RtdlNativeDeviceHitStreamOutput(
            ray_ids_device_ptr=0x5000,
            primitive_ids_device_ptr=0x6000,
            row_count=1,
            capacity=1,
            overflow=False,
            hit_event_count=1,
            owner=owner,
        )
        handoff = native_output.to_handoff()

        self.assertIs(handoff.owner, native_output)
        handoff.owner.close()
        self.assertTrue(owner.closed)

    def test_optix_runtime_names_the_future_symbol_but_does_not_bind_it_yet(self) -> None:
        self.assertEqual(
            optix_runtime.OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_DEVICE_COLUMNS_SYMBOL,
            rt.GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS["optix"],
        )
        self.assertNotIn("prepare_native_device_hit_stream_columns_from_abi", rt.__all__)
        self.assertNotIn("RtdlNativeDeviceHitStreamOutput", rt.__all__)
        self.assertNotIn("RtdlRawCudaColumn", rt.__all__)


if __name__ == "__main__":
    unittest.main()
