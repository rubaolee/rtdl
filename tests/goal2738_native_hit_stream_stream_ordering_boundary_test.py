import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2738NativeHitStreamStreamOrderingBoundaryTest(unittest.TestCase):
    def test_default_native_output_stream_ordering_is_not_proven(self) -> None:
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

        self.assertEqual(output_metadata["producer_consumer_stream_ordering"], "not_proven")
        self.assertFalse(output_metadata["stream_synchronization_proven"])
        self.assertTrue(output_metadata["true_zero_copy_requires_stream_synchronization"])
        self.assertEqual(handoff_metadata["producer_consumer_stream_ordering"], "not_proven")
        self.assertFalse(handoff_metadata["stream_synchronization_proven"])
        self.assertFalse(handoff_metadata["true_zero_copy_authorized"])

    def test_stream_ordering_state_can_record_future_proof_without_authorizing_zero_copy(self) -> None:
        hit_columns = rt.prepare_native_device_hit_stream_columns_from_abi(
            ray_ids_device_ptr=4096,
            primitive_ids_device_ptr=8192,
            row_count=2,
            capacity=2,
            overflow=False,
            hit_event_count=2,
            native_device_column_output_proven_on_hardware=True,
            producer_consumer_stream_ordering="producer_event_waited_by_consumer",
        )
        metadata = hit_columns.to_metadata()

        self.assertEqual(
            metadata["producer_consumer_stream_ordering"],
            "producer_event_waited_by_consumer",
        )
        self.assertTrue(metadata["stream_synchronization_proven"])
        self.assertTrue(metadata["true_zero_copy_requires_stream_synchronization"])
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_invalid_stream_ordering_state_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "stream ordering"):
            rt.RtdlNativeDeviceHitStreamOutput(
                ray_ids_device_ptr=1024,
                primitive_ids_device_ptr=2048,
                row_count=1,
                capacity=1,
                overflow=False,
                hit_event_count=1,
                producer_consumer_stream_ordering="trust_me",
            )

    def test_optix_runtime_preserves_stream_ordering_when_rebuilding_handoff(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text()

        self.assertIn(
            "producer_consumer_stream_ordering=handoff.producer_consumer_stream_ordering",
            source,
        )


if __name__ == "__main__":
    unittest.main()
