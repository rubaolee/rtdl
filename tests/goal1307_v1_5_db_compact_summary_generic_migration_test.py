from __future__ import annotations

import unittest

import rtdsl as rt
from examples import rtdl_sales_risk_screening as sales


class _FakePreparedDbDataset:
    row_count = 6

    def __init__(self) -> None:
        self.compact_summary_batch_calls = 0
        self.grouped_count_calls = 0
        self.grouped_sum_calls = 0
        self._dataset = type("_Dataset", (), {"transfer": "columnar"})()

    def compact_summary_batch(self, requests):
        self.compact_summary_batch_calls += 1
        return {
            "risky_scan_count": 3,
            "risky_order_count_by_region": {"east": 1, "west": 1, "central": 1},
            "risky_revenue_by_region": {"east": 310, "west": 280, "central": 260},
        }

    def last_compact_summary_batch_phase_timings(self):
        return {"risky_scan_count": {"traversal": 0.001}}

    def grouped_count(self, _query):
        self.grouped_count_calls += 1
        return ()

    def grouped_sum(self, _query):
        self.grouped_sum_calls += 1
        return ()

    def close(self) -> None:
        pass


class Goal1307V15DbCompactSummaryGenericMigrationTest(unittest.TestCase):
    def test_db_compact_summary_contracts_are_registered_and_validated(self) -> None:
        contracts = rt.validate_v1_5_db_compact_summary_contracts()

        self.assertEqual(
            tuple(contract["operation"] for contract in contracts),
            (
                "conjunctive_scan_count",
                "grouped_count_summary",
                "grouped_sum_summary",
            ),
        )
        self.assertEqual(
            tuple(contract["summary_primitive"] for contract in contracts),
            ("COUNT_HITS", "REDUCE_INT(COUNT)", "REDUCE_INT(SUM)"),
        )
        self.assertTrue(
            set(contract["result_layout"] for contract in contracts).issubset(
                set(rt.V1_5_DB_COMPACT_SUMMARY_RESULT_LAYOUTS)
            )
        )
        self.assertTrue(all(contract["dtype"] == "int64" for contract in contracts))
        self.assertTrue(all(contract["materialization_free"] for contract in contracts))

    def test_generic_db_compact_summary_batch_metadata(self) -> None:
        dataset = _FakePreparedDbDataset()
        result = rt.run_generic_db_compact_summary_batch(
            prepared_dataset=dataset,
            backend="optix",
            requests=(
                {"name": "scan", "operation": "conjunctive_scan_count", "predicates": ()},
                {"name": "count", "operation": "grouped_count_summary", "query": {"group_keys": ("region",)}},
                {
                    "name": "sum",
                    "operation": "grouped_sum_summary",
                    "query": {"group_keys": ("region",), "value_field": "revenue"},
                },
            ),
        )

        self.assertEqual(result["primitive"], "DB_COMPACT_SUMMARY")
        self.assertEqual(
            result["summary_primitives"],
            ("COUNT_HITS", "REDUCE_INT(COUNT)", "REDUCE_INT(SUM)"),
        )
        self.assertEqual(
            tuple(contract["summary_primitive"] for contract in result["summary_contracts"]),
            result["summary_primitives"],
        )
        self.assertEqual(
            tuple(contract["result_layout"] for contract in result["summary_contracts"]),
            (
                "scalar_int64_hit_count",
                "grouped_int64_count_map",
                "grouped_int64_sum_map",
            ),
        )
        self.assertTrue(
            set(contract["result_layout"] for contract in result["summary_contracts"]).issubset(
                set(rt.V1_5_DB_COMPACT_SUMMARY_RESULT_LAYOUTS)
            )
        )
        self.assertTrue(all(contract["materialization_free"] for contract in result["summary_contracts"]))
        self.assertEqual(result["result_layout"], "aggregate_scan_count_and_grouped_integer_maps")
        self.assertTrue(result["materialization_free"])
        self.assertEqual(dataset.compact_summary_batch_calls, 1)

    def test_sales_risk_compact_summary_uses_generic_wrapper(self) -> None:
        dataset = _FakePreparedDbDataset()
        original_prepare = sales._prepare_dataset
        sales._prepare_dataset = lambda _backend, _table: dataset
        try:
            with sales.prepare_session("optix", copies=1) as session:
                payload = session.run(output_mode="compact_summary")
        finally:
            sales._prepare_dataset = original_prepare

        self.assertEqual(dataset.compact_summary_batch_calls, 1)
        self.assertEqual(dataset.grouped_count_calls, 0)
        self.assertEqual(dataset.grouped_sum_calls, 0)
        self.assertEqual(payload["generic_compact_summary"]["primitive"], "DB_COMPACT_SUMMARY")
        self.assertEqual(
            payload["generic_compact_summary"]["summary_primitives"],
            ("COUNT_HITS", "REDUCE_INT(COUNT)", "REDUCE_INT(SUM)"),
        )
        self.assertEqual(payload["native_continuation_backend"], "optix_db_compact_summary")

    def test_generic_db_compact_summary_rejects_frozen_backends(self) -> None:
        for backend in ("vulkan", "hiprt", "apple_rt"):
            with self.subTest(backend=backend):
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    rt.run_generic_db_compact_summary_batch(
                        prepared_dataset=_FakePreparedDbDataset(),
                        backend=backend,
                        requests=({"name": "scan", "operation": "conjunctive_scan_count", "predicates": ()},),
                    )

    def test_generic_db_compact_summary_rejects_bad_request_contracts(self) -> None:
        dataset = _FakePreparedDbDataset()
        cases = (
            (
                (),
                "requires at least one request",
            ),
            (
                ({"name": "", "operation": "conjunctive_scan_count", "predicates": ()},),
                "request name must be non-empty",
            ),
            (
                (
                    {"name": "dup", "operation": "conjunctive_scan_count", "predicates": ()},
                    {"name": "dup", "operation": "grouped_count_summary", "query": {"group_keys": ("region",)}},
                ),
                "duplicate generic DB compact summary request name",
            ),
            (
                ({"name": "bad", "operation": "materialize_rows", "query": {}},),
                "unsupported generic DB compact summary operation",
            ),
            (
                ({"name": "scan", "operation": "conjunctive_scan_count"},),
                "conjunctive_scan_count requires predicates",
            ),
            (
                ({"name": "count", "operation": "grouped_count_summary"},),
                "grouped_count_summary requires query",
            ),
            (
                ({"name": "sum", "operation": "grouped_sum_summary"},),
                "grouped_sum_summary requires query",
            ),
        )

        for requests, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    rt.run_generic_db_compact_summary_batch(
                        prepared_dataset=dataset,
                        backend="optix",
                        requests=requests,
                    )

        self.assertEqual(dataset.compact_summary_batch_calls, 0)


if __name__ == "__main__":
    unittest.main()
