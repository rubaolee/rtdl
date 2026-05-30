import unittest

import rtdsl as rt


class _Owner:
    def __init__(self) -> None:
        self.close_count = 0

    def close(self) -> None:
        self.close_count += 1


class Goal2737NativeHitStreamOwnerLifecycleGuardTest(unittest.TestCase):
    def test_native_output_close_is_idempotent_and_blocks_future_handoff(self) -> None:
        owner = _Owner()
        output = rt.RtdlNativeDeviceHitStreamOutput(
            ray_ids_device_ptr=1024,
            primitive_ids_device_ptr=2048,
            row_count=2,
            capacity=4,
            overflow=False,
            hit_event_count=2,
            owner=owner,
            native_device_column_output_proven_on_hardware=True,
        )

        self.assertEqual(output.to_metadata()["owner_lifetime_state"], "open")
        handoff = output.to_handoff()
        self.assertEqual(handoff.to_metadata()["owner_lifetime_state"], "open")

        output.close()
        output.close()

        self.assertEqual(owner.close_count, 1)
        self.assertEqual(output.to_metadata()["owner_lifetime_state"], "closed")
        with self.assertRaisesRegex(RuntimeError, "closed"):
            output.to_handoff()

    def test_raw_cuda_column_rejects_cuda_array_interface_after_owner_close(self) -> None:
        owner = _Owner()
        output = rt.RtdlNativeDeviceHitStreamOutput(
            ray_ids_device_ptr=4096,
            primitive_ids_device_ptr=8192,
            row_count=1,
            capacity=1,
            overflow=False,
            hit_event_count=1,
            owner=owner,
            native_device_column_output_proven_on_hardware=True,
        )
        handoff = output.to_handoff()

        self.assertEqual(handoff.primitive_ids.__cuda_array_interface__["data"][0], 8192)

        output.close()

        with self.assertRaisesRegex(RuntimeError, "owner is closed"):
            _ = handoff.primitive_ids.__cuda_array_interface__

    def test_lifecycle_metadata_preserves_claim_boundary(self) -> None:
        output = rt.RtdlNativeDeviceHitStreamOutput(
            ray_ids_device_ptr=1024,
            primitive_ids_device_ptr=2048,
            row_count=1,
            capacity=1,
            overflow=False,
            hit_event_count=1,
            native_device_column_output_proven_on_hardware=True,
        )
        output_metadata = output.to_metadata()
        handoff_metadata = output.to_handoff().to_metadata()

        self.assertFalse(output_metadata["true_zero_copy_authorized"])
        self.assertFalse(handoff_metadata["true_zero_copy_authorized"])
        self.assertFalse(output_metadata["handoff_after_close_allowed"])
        self.assertFalse(handoff_metadata["handoff_after_owner_close_allowed"])
        self.assertIn("native_owner_state_machine", handoff_metadata["ownership_lifetime_model"])


if __name__ == "__main__":
    unittest.main()
