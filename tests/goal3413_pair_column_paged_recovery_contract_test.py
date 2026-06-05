from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3413_pair_column_paged_recovery_contract_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3413_pair_column_paged_recovery_probe.py"


class Goal3413PairColumnPagedRecoveryContractTest(unittest.TestCase):
    def test_page_request_generation_is_caller_visible(self):
        from rtdsl.pair_column_paged_recovery import iter_pair_column_page_requests

        pages = iter_pair_column_page_requests(total_count=10, page_size=4, initial_capacity=3)
        self.assertEqual([(page.start, page.stop, page.item_count) for page in pages], [(0, 4, 4), (4, 8, 4), (8, 10, 2)])
        self.assertEqual([page.page_index for page in pages], [0, 1, 2])
        self.assertEqual([page.initial_capacity for page in pages], [3, 3, 3])

    def test_contract_rejects_hidden_or_automatic_behavior(self):
        from rtdsl.pair_column_paged_recovery import PairColumnPagedRecoveryContract

        contract = PairColumnPagedRecoveryContract(page_size=2048, initial_capacity=100)
        metadata = contract.to_metadata()
        self.assertTrue(metadata["windows_are_caller_visible"])
        self.assertEqual(metadata["overflow_policy"], "fail_closed_explicit_retry")
        self.assertEqual(metadata["merge_rule"], "key_addition")
        self.assertFalse(metadata["native_paged_stream_implemented"])
        self.assertFalse(metadata["automatic_retry_authorized"])
        self.assertFalse(metadata["hidden_dispatch_authorized"])
        self.assertFalse(metadata["merge_requires_disjoint_keys"])

        with self.assertRaises(ValueError):
            PairColumnPagedRecoveryContract(page_size=2048, initial_capacity=100, automatic_retry_authorized=True)
        with self.assertRaises(ValueError):
            PairColumnPagedRecoveryContract(page_size=2048, initial_capacity=100, hidden_dispatch_authorized=True)
        with self.assertRaises(ValueError):
            PairColumnPagedRecoveryContract(page_size=2048, initial_capacity=100, merge_requires_disjoint_keys=True)

    def test_merge_uses_key_addition_not_disjoint_concatenation(self):
        from rtdsl.pair_column_paged_recovery import merge_grouped_count_maps

        merged = merge_grouped_count_maps(({1: 2, 2: 5}, {1: 7, 3: 11}))
        self.assertEqual(merged, {1: 9, 2: 5, 3: 11})
        with self.assertRaises(ValueError):
            merge_grouped_count_maps(({1: -1},))

    def test_page_recovery_record_requires_explicit_retry_shape(self):
        from rtdsl.pair_column_paged_recovery import PairColumnPageRecoveryRecord
        from rtdsl.pair_column_paged_recovery import PairColumnPageRequest

        request = PairColumnPageRequest(page_index=0, start=0, stop=4, initial_capacity=3)
        record = PairColumnPageRecoveryRecord(
            request=request,
            first_capacity_status={"capacity": 3, "row_count": 0, "required_capacity": 5, "overflowed": True},
            retry_used=True,
            retry_capacity_hint=5,
            recovered_capacity_status={"capacity": 5, "row_count": 5, "required_capacity": 5, "overflowed": False},
            grouped_source_row_count=5,
            grouped_row_count=4,
            grouped_overflow=False,
            device_group_count=4,
            host_exact_rows=5,
        )
        self.assertEqual(record.to_metadata()["retry_capacity_hint"], 5)

        with self.assertRaises(ValueError):
            PairColumnPageRecoveryRecord(
                request=request,
                first_capacity_status={"overflowed": False},
                retry_used=True,
                retry_capacity_hint=5,
                recovered_capacity_status={"overflowed": False},
                grouped_source_row_count=5,
                grouped_row_count=4,
                grouped_overflow=False,
                device_group_count=4,
            )

    def test_report_and_probe_keep_native_paged_stream_boundary(self):
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("generic contract", report)
        self.assertIn("not", report)
        self.assertIn("about a named application", report)
        self.assertIn("not the native graduation", report)
        self.assertIn("does not implement", report)
        self.assertIn("native paged streams", report)
        self.assertIn("automatic retry", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("release authorization", report)

        self.assertIn("PairColumnPagedRecoveryContract", script)
        self.assertIn("iter_pair_column_page_requests", script)
        self.assertIn("merge_grouped_count_maps", script)
        self.assertIn("page_merge_uses_key_addition", script)
        self.assertIn('"automatic_retry_authorized": False', script)


if __name__ == "__main__":
    unittest.main()
