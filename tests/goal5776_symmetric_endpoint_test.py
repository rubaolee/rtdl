from __future__ import annotations

import unittest

from goal5776_real_scale_formal_contract import COLD, PREPARED
from goal5776_symmetric_endpoint import measure_symmetric_endpoint


def _receipt():
    return {
        "physical_executor_classification": "optix_traversal_observed",
        "native_snapshot": {
            "successful_launch_count": 1,
            "complete_context_launch_count": 1,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "unbound_launch_count": 0,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": "gas:first",
            "last_traversable": "gas:last",
        },
    }


class _Clock:
    def __init__(self):
        self.value = 10.0

    def __call__(self):
        result = self.value
        self.value += 1.0
        return result


class Goal5776SymmetricEndpointTest(unittest.TestCase):
    def run_lifecycle(self, lifecycle):
        events = []
        owner = object()
        observation = measure_symmetric_endpoint(
            lifecycle=lifecycle,
            load=lambda: events.append("load") or {"loaded": True},
            prepare=lambda loaded: (
                self.assertEqual(loaded, {"loaded": True}),
                events.append("prepare"), owner,
            )[-1],
            execute=lambda actual: (
                self.assertIs(actual, owner), events.append("execute"), {"value": 7}
            )[-1],
            canonicalize_and_bind_output=lambda raw: (
                events.append("canonicalize"), {"value": raw["value"]}
            )[-1],
            finish_traversal_receipt=lambda actual, raw, canonical: (
                self.assertIs(actual, owner), events.append("receipt"), _receipt()
            )[-1],
            compare_outside_timer=lambda canonical: (
                events.append("compare"), canonical == {"value": 7}
            )[-1],
            close=lambda actual: (self.assertIs(actual, owner), events.append("close")),
            clock=_Clock(),
        )
        return observation, events

    def test_cold_includes_load_prepare_output_receipt_and_close(self):
        observation, events = self.run_lifecycle(COLD)
        self.assertEqual(
            events, ["load", "prepare", "execute", "canonicalize", "receipt", "close", "compare"]
        )
        self.assertEqual(observation.registered_complete_endpoint_seconds, 1.0)
        self.assertIsNone(observation.loading_seconds_reported_separately)
        self.assertIsNone(observation.preparation_seconds_reported_separately)
        self.assertTrue(observation.close_inside_registered_timer)
        self.assertFalse(observation.comparator_inside_registered_timer)

    def test_prepared_reports_load_and_prepare_and_excludes_close(self):
        observation, events = self.run_lifecycle(PREPARED)
        self.assertEqual(
            events, ["load", "prepare", "execute", "canonicalize", "receipt", "compare", "close"]
        )
        self.assertEqual(observation.loading_seconds_reported_separately, 1.0)
        self.assertEqual(observation.preparation_seconds_reported_separately, 1.0)
        self.assertEqual(observation.registered_complete_endpoint_seconds, 1.0)
        self.assertFalse(observation.close_inside_registered_timer)
        self.assertFalse(observation.preparation_is_free)

    def test_invalid_receipt_and_mismatch_fail_closed(self):
        bad = _receipt()
        bad["native_snapshot"]["unbound_launch_count"] = 1
        # The schema's explicit unbound field is not a substitute for complete
        # binding.  Make the complete count inconsistent to prove fail-closed.
        bad["native_snapshot"]["complete_context_launch_count"] = 0
        with self.assertRaises(RuntimeError):
            measure_symmetric_endpoint(
                lifecycle=PREPARED,
                load=lambda: object(),
                prepare=lambda loaded: object(),
                execute=lambda owner: 1,
                canonicalize_and_bind_output=lambda raw: raw,
                finish_traversal_receipt=lambda owner, raw, canonical: bad,
                compare_outside_timer=lambda canonical: True,
                close=lambda owner: None,
                clock=_Clock(),
            )
        with self.assertRaises(RuntimeError):
            measure_symmetric_endpoint(
                lifecycle=COLD,
                load=lambda: object(),
                prepare=lambda loaded: object(),
                execute=lambda owner: 1,
                canonicalize_and_bind_output=lambda raw: raw,
                finish_traversal_receipt=lambda owner, raw, canonical: _receipt(),
                compare_outside_timer=lambda canonical: False,
                close=lambda owner: None,
                clock=_Clock(),
            )


if __name__ == "__main__":
    unittest.main()
