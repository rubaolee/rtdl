from __future__ import annotations

import unittest

import rtdsl as rt


def _descriptor(*, native: bool = False) -> rt.RtdlNeutralBufferSeamDescriptor:
    buffer = rt.RtdlBufferDescriptor(
        name="ray_ids",
        dtype="int64",
        shape=(2,),
        device_type="cuda",
        data_ptr=0xABCD,
        source_protocol="cuda_array_interface",
        lifetime="session_retained" if native else "caller_retained",
    )
    return rt.neutral_buffer_descriptor_from_rtdl_buffer(
        buffer,
        producer="native_optix_future" if native else "python_reference",
        consumer="triton",
        lifetime_state="native_owned_pending_state_machine" if native else "producer_retained",
        native_producer=native,
    )


class Goal2703NeutralBufferLeaseStateMachineTest(unittest.TestCase):
    def test_producer_retained_lease_borrow_complete_release(self) -> None:
        lease = rt.create_neutral_buffer_lease(
            _descriptor(),
            owner_state="producer_retained",
        )
        borrowed = lease.begin_partner_borrow()
        returned = borrowed.complete_partner_borrow()
        released = returned.release()

        self.assertEqual(lease.state, "producer_retained")
        self.assertTrue(borrowed.is_borrowed)
        self.assertEqual(returned.state, "producer_retained")
        self.assertTrue(released.is_released)
        self.assertEqual(released.event_log, ("handoff_begin", "continuation_complete", "release"))
        self.assertFalse(released.to_metadata()["true_zero_copy_authorized"])

    def test_native_pending_lease_marks_state_machine_required(self) -> None:
        lease = rt.create_neutral_buffer_lease(_descriptor(native=True))
        borrowed = lease.begin_partner_borrow()
        returned = borrowed.complete_partner_borrow()

        self.assertEqual(lease.state, "native_owned_pending_state_machine")
        self.assertEqual(lease.retain_until, "state_machine_defined")
        self.assertTrue(lease.native_state_machine_required)
        self.assertTrue(returned.native_state_machine_required)
        self.assertEqual(returned.event_log, ("handoff_begin", "continuation_complete"))

    def test_invalid_lifetime_actions_fail_closed(self) -> None:
        lease = rt.create_neutral_buffer_lease(
            _descriptor(),
            owner_state="producer_retained",
        )
        borrowed = lease.begin_partner_borrow()

        with self.assertRaisesRegex(ValueError, "invalid neutral buffer lifetime transition"):
            borrowed.release()
        cleaned = borrowed.failure_cleanup()
        with self.assertRaisesRegex(ValueError, "invalid neutral buffer lifetime transition"):
            cleaned.begin_partner_borrow()

    def test_lease_cannot_start_borrowed_or_released(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot start in partner_borrowed"):
            rt.create_neutral_buffer_lease(_descriptor(), owner_state="partner_borrowed")
        with self.assertRaisesRegex(ValueError, "cannot start released"):
            rt.create_neutral_buffer_lease(_descriptor(), owner_state="released")

    def test_lease_symbols_are_experimental_not_star_exports(self) -> None:
        self.assertTrue(hasattr(rt, "RtdlNeutralBufferLease"))
        self.assertTrue(hasattr(rt, "create_neutral_buffer_lease"))
        self.assertNotIn("RtdlNeutralBufferLease", rt.__all__)
        self.assertNotIn("create_neutral_buffer_lease", rt.__all__)


if __name__ == "__main__":
    unittest.main()
