import unittest

import rtdsl as rt


def host_descriptor() -> dict:
    return rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
        buffer_kind="pinned_host_staging",
        backend="optix",
        device="cpu",
        dtype="int64",
        shape=(16, 2),
        lifetime="session",
        byte_count=256,
    )


def device_descriptor() -> dict:
    return rt.prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
        buffer_kind="rtdl_device_resident",
        backend="optix",
        device="cuda:0",
        dtype="int64",
        shape=(16, 2),
        lifetime="explicit_release",
        byte_count=256,
        pointer=123456,
        transfer_count_state="instrumentation_planned",
    )


class Goal1483PythonRtdlManagedBufferLifecycleTest(unittest.TestCase):
    def test_begins_rtdl_owned_lifecycle_without_zero_copy_claims(self) -> None:
        lifecycle = rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
            host_descriptor(),
            allocation_id="host-buffer-1",
        )

        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle)

        self.assertEqual(validated["owner"], "rtdl")
        self.assertEqual(validated["lifecycle_state"], "active_unmeasured")
        self.assertEqual(validated["host_to_rtdl_transfers"], 0)
        self.assertFalse(validated["measured_transfer_count"])
        self.assertFalse(validated["true_zero_copy_authorized"])
        self.assertIn("not a native allocator", validated["claim_boundary"])

    def test_records_transfer_counts_and_event_log(self) -> None:
        lifecycle = rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
            device_descriptor(),
            allocation_id="device-buffer-1",
        )

        lifecycle = rt.record_v1_5_4_python_rtdl_managed_buffer_transfer(
            lifecycle,
            direction="host_to_rtdl",
            count=2,
            note="synthetic upload boundary",
        )
        lifecycle = rt.record_v1_5_4_python_rtdl_managed_buffer_transfer(
            lifecycle,
            direction="rtdl_internal",
            count=1,
        )
        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle)

        self.assertEqual(validated["host_to_rtdl_transfers"], 2)
        self.assertEqual(validated["rtdl_internal_transfers"], 1)
        self.assertTrue(validated["measured_transfer_count"])
        self.assertEqual(len(validated["event_log"]), 3)
        self.assertFalse(validated["true_zero_copy_evidence_candidate"])
        self.assertFalse(validated["managed_buffer_zero_copy_authorized"])

    def test_release_marks_lifecycle_released_and_blocks_more_transfers(self) -> None:
        lifecycle = rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
            device_descriptor(),
            allocation_id="device-buffer-2",
        )

        released = rt.release_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle)
        validated = rt.validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(released)

        self.assertEqual(validated["status"], "v1_5_4_python_rtdl_managed_buffer_lifecycle_released")
        self.assertEqual(validated["lifecycle_state"], "released")
        self.assertEqual(validated["event_log"][-1]["event"], "release_lifecycle")
        with self.assertRaisesRegex(ValueError, "active lifecycle"):
            rt.record_v1_5_4_python_rtdl_managed_buffer_transfer(
                validated,
                direction="rtdl_to_host",
                count=1,
            )

    def test_rejects_invalid_lifecycle_or_claim_expansion(self) -> None:
        with self.assertRaisesRegex(ValueError, "allocation_id"):
            rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
                host_descriptor(),
                allocation_id="",
            )

        lifecycle = rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
            host_descriptor(),
            allocation_id="host-buffer-2",
        )
        lifecycle["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized=False"):
            rt.validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle)

    def test_rejects_negative_or_unknown_transfer_direction(self) -> None:
        lifecycle = rt.begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
            host_descriptor(),
            allocation_id="host-buffer-3",
        )

        with self.assertRaisesRegex(ValueError, "unsupported"):
            rt.record_v1_5_4_python_rtdl_managed_buffer_transfer(
                lifecycle,
                direction="partner_to_rtdl",
                count=1,
            )
        with self.assertRaisesRegex(ValueError, "non-negative"):
            rt.record_v1_5_4_python_rtdl_managed_buffer_transfer(
                lifecycle,
                direction="host_to_rtdl",
                count=-1,
            )


if __name__ == "__main__":
    unittest.main()
