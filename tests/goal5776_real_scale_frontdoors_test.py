from __future__ import annotations

import unittest

from goal5776_real_scale_frontdoors import _combine_receipts


def _receipt(provider: str, launches: int, first: str, last: str):
    return {
        "provider_library_sha256": provider,
        "native_snapshot": {
            "successful_launch_count": launches,
            "complete_context_launch_count": launches,
            "unbound_launch_count": 0,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": first,
            "last_traversable": last,
        },
    }


class Goal5776RealScaleFrontdoorsTest(unittest.TestCase):
    def test_combined_receipt_preserves_provider_and_sums_launches(self):
        combined = _combine_receipts((
            _receipt("a" * 64, 2, "gas:first", "gas:middle"),
            _receipt("a" * 64, 3, "gas:middle", "gas:last"),
        ))
        self.assertEqual(combined["component_receipt_count"], 2)
        self.assertEqual(len(combined["component_receipts"]), 2)
        self.assertEqual(combined["provider_library_sha256"], "a" * 64)
        snapshot = combined["native_snapshot"]
        self.assertEqual(snapshot["successful_launch_count"], 5)
        self.assertEqual(snapshot["complete_context_launch_count"], 5)
        self.assertEqual(snapshot["first_traversable"], "gas:first")
        self.assertEqual(snapshot["last_traversable"], "gas:last")

    def test_combined_receipt_rejects_mixed_native_providers(self):
        with self.assertRaisesRegex(RuntimeError, "multiple native providers"):
            _combine_receipts((
                _receipt("a" * 64, 1, "gas:a", "gas:a"),
                _receipt("b" * 64, 1, "gas:b", "gas:b"),
            ))

    def test_combined_receipt_rejects_empty_sequence(self):
        with self.assertRaisesRegex(RuntimeError, "empty traversal-receipt"):
            _combine_receipts(())


if __name__ == "__main__":
    unittest.main()
