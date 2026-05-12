from __future__ import annotations

import unittest
from unittest import mock
import ctypes


class _BatchDatasetMixin:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self._phase_id = 0

    def conjunctive_scan_count(self, predicates) -> int:
        self.calls.append(("conjunctive_scan_count", predicates))
        return 7

    def grouped_count_summary(self, query) -> dict[str, int]:
        self.calls.append(("grouped_count_summary", query))
        return {"east": 3, "west": 4}

    def grouped_sum_summary(self, query) -> dict[str, int]:
        self.calls.append(("grouped_sum_summary", query))
        return {"east": 30, "west": 40}

    def last_phase_timings(self):
        self._phase_id += 1
        return {"phase_id": self._phase_id}


class _OptixLikeDataset(_BatchDatasetMixin):
    from rtdsl.optix_runtime import PreparedOptixDbDataset

    compact_summary_batch = PreparedOptixDbDataset.compact_summary_batch
    _compact_summary_batch_native = PreparedOptixDbDataset._compact_summary_batch_native
    last_compact_summary_batch_phase_timings = PreparedOptixDbDataset.last_compact_summary_batch_phase_timings


class _EmbreeLikeDataset(_BatchDatasetMixin):
    from rtdsl.embree_runtime import PreparedEmbreeDbDataset

    compact_summary_batch = PreparedEmbreeDbDataset.compact_summary_batch
    last_compact_summary_batch_phase_timings = PreparedEmbreeDbDataset.last_compact_summary_batch_phase_timings


class _FakeInner:
    transfer = "columnar"


class _AppBatchDataset(_BatchDatasetMixin):
    def __init__(self) -> None:
        super().__init__()
        self._dataset = _FakeInner()
        self.row_count = 7

    def compact_summary_batch(self, requests) -> dict[str, object]:
        self.calls.append(("compact_summary_batch", requests))
        return {
            "promo_order_count": 4,
            "open_order_count_by_region": {"east": 2, "west": 2},
            "web_revenue_by_region": {"east": 180, "west": 240},
            "risky_scan_count": 4,
            "risky_order_count_by_region": {"east": 1, "west": 2, "central": 1},
            "risky_revenue_by_region": {"east": 310, "west": 430, "central": 260},
        }

    def last_compact_summary_batch_phase_timings(self) -> dict[str, object]:
        return {"batch": {"phase_id": 1}}

    def close(self) -> None:
        pass


REQUESTS = (
    {"name": "scan_count", "operation": "conjunctive_scan_count", "predicates": (("ship_date", "ge", 12),)},
    {
        "name": "count_by_region",
        "operation": "grouped_count_summary",
        "query": {"predicates": (("quantity", "lt", 20),), "group_keys": ("region",)},
    },
    {
        "name": "revenue_by_region",
        "operation": "grouped_sum_summary",
        "query": {
            "predicates": (("channel", "eq", "web"),),
            "group_keys": ("region",),
            "value_field": "revenue",
        },
    },
)


class Goal1156DbCompactSummaryBatchContractTest(unittest.TestCase):
    def test_optix_batch_contract_dispatches_supported_operations_and_captures_phases(self) -> None:
        dataset = _OptixLikeDataset()

        results = dataset.compact_summary_batch(REQUESTS)

        self.assertEqual(results["scan_count"], 7)
        self.assertEqual(results["count_by_region"], {"east": 3, "west": 4})
        self.assertEqual(results["revenue_by_region"], {"east": 30, "west": 40})
        self.assertEqual(
            [call[0] for call in dataset.calls],
            ["conjunctive_scan_count", "grouped_count_summary", "grouped_sum_summary"],
        )
        self.assertEqual(set(dataset.last_compact_summary_batch_phase_timings()), set(results))

    def test_embree_batch_contract_dispatches_supported_operations(self) -> None:
        dataset = _EmbreeLikeDataset()

        results = dataset.compact_summary_batch(REQUESTS)

        self.assertEqual(results["scan_count"], 7)
        self.assertEqual(results["count_by_region"]["west"], 4)
        self.assertEqual(results["revenue_by_region"]["east"], 30)
        self.assertEqual(set(dataset.last_compact_summary_batch_phase_timings()), set(results))

    def test_batch_rejects_unknown_operation(self) -> None:
        dataset = _OptixLikeDataset()

        with self.assertRaisesRegex(ValueError, "unsupported DB compact-summary batch operation"):
            dataset.compact_summary_batch(({"name": "bad", "operation": "rows"},))

    def test_optix_native_batch_symbol_path_decodes_results(self) -> None:
        from rtdsl import optix_runtime

        class _FakeLib:
            rtdl_optix_columnar_payload_compact_summary_batch = object()

        class _FakeLower:
            library = _FakeLib()

            def __init__(self) -> None:
                self.destroyed = False
                self._count_rows = (optix_runtime._RtdlDbGroupedCountRow * 1)(
                    optix_runtime._RtdlDbGroupedCountRow(1, 9)
                )
                self._sum_rows = (optix_runtime._RtdlDbGroupedSumRow * 1)(
                    optix_runtime._RtdlDbGroupedSumRow(1, 90)
                )
                self._results = (optix_runtime._RtdlDbCompactSummaryResult * 3)()
                self._results[0].operation = optix_runtime._DB_COMPACT_SUMMARY_OP_SCAN_COUNT
                self._results[0].scalar_value = 11
                self._results[0].traversal = 0.1
                self._results[0].emitted_count = 11
                self._results[1].operation = optix_runtime._DB_COMPACT_SUMMARY_OP_GROUPED_COUNT
                self._results[1].count_rows = self._count_rows
                self._results[1].count_row_count = 1
                self._results[1].output_pack = 0.2
                self._results[2].operation = optix_runtime._DB_COMPACT_SUMMARY_OP_GROUPED_SUM
                self._results[2].sum_rows = self._sum_rows
                self._results[2].sum_row_count = 1
                self._results[2].output_pack = 0.3

            def compact_summary_batch_native(self, requests_array, request_count):
                self.request_count = request_count
                return ctypes.cast(self._results, ctypes.POINTER(optix_runtime._RtdlDbCompactSummaryResult)), 3

            def destroy_compact_summary_batch_results(self, results_ptr, result_count: int) -> None:
                self.destroy_count = result_count
                self.destroyed = True

        dataset = object.__new__(optix_runtime.PreparedOptixDbDataset)
        dataset._dataset = _FakeLower()
        dataset._field_maps = {}
        dataset._reverse_maps = {"region": {1: "east"}}

        results = dataset.compact_summary_batch(REQUESTS)

        self.assertEqual(results["scan_count"], 11)
        self.assertEqual(results["count_by_region"], {"east": 9})
        self.assertEqual(results["revenue_by_region"], {"east": 90})
        self.assertEqual(dataset._dataset.request_count, 3)
        self.assertEqual(dataset._dataset.destroy_count, 3)
        self.assertTrue(dataset._dataset.destroyed)
        self.assertEqual(dataset.last_compact_summary_batch_phase_timings()["scan_count"]["traversal"], 0.1)

    def test_regional_app_uses_batch_without_duplicate_group_calls(self) -> None:
        from examples import rtdl_v0_7_db_app_demo as regional

        dataset = _AppBatchDataset()
        with mock.patch.object(regional, "_prepare_dataset", return_value=dataset):
            with regional.prepare_session("optix", copies=1) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual([call[0] for call in dataset.calls], ["compact_summary_batch"])
        self.assertIn("query_compact_summary_batch_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_count_summary_sec", payload["run_phases"])
        self.assertEqual(payload["summary"]["promo_order_count"], 4)

    def test_sales_app_uses_batch_without_duplicate_group_calls(self) -> None:
        from examples import rtdl_sales_risk_screening as sales

        dataset = _AppBatchDataset()
        with mock.patch.object(sales, "_prepare_dataset", return_value=dataset):
            with sales.prepare_session("optix", copies=1) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual([call[0] for call in dataset.calls], ["compact_summary_batch"])
        self.assertIn("query_compact_summary_batch_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_sum_summary_sec", payload["run_phases"])
        self.assertEqual(payload["summary"]["risky_order_count"], 4)

    def test_sales_app_chunks_large_compact_summary_sessions(self) -> None:
        from examples import rtdl_sales_risk_screening as sales

        datasets = [_AppBatchDataset(), _AppBatchDataset(), _AppBatchDataset()]
        with (
            mock.patch.object(sales, "DB_COMPACT_SUMMARY_CHUNK_COPIES", 2),
            mock.patch.object(sales, "_prepare_dataset", side_effect=datasets),
        ):
            with sales.prepare_session("optix", copies=5) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual([dataset.calls[0][0] for dataset in datasets], ["compact_summary_batch"] * 3)
        self.assertTrue(payload["session"]["chunked_compact_summary"])
        self.assertEqual(payload["session"]["chunk_count"], 3)
        self.assertEqual(payload["session"]["chunk_copies"], [2, 2, 1])
        self.assertEqual(payload["prepared_dataset"]["transfer"], "chunked_columnar")
        self.assertEqual(payload["summary"]["risky_order_count"], 12)
        self.assertEqual(
            payload["summary"]["risky_order_count_by_region"],
            {"east": 3, "west": 6, "central": 3},
        )
        self.assertEqual(
            payload["summary"]["risky_revenue_by_region"],
            {"east": 930, "west": 1290, "central": 780},
        )
        phases = payload["native_db_phases"]["compact_summary_batch"]["batch"]
        self.assertEqual(phases["raw_candidate_count"], 0)
        self.assertEqual(payload["native_continuation_backend"], "optix_db_compact_summary")


if __name__ == "__main__":
    unittest.main()
