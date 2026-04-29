from __future__ import annotations

import unittest
from unittest import mock


class _FakeInner:
    transfer = "columnar"


class _FakeEmbreeDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 21
        self.scan_count_calls = 0
        self.grouped_count_summary_calls = 0
        self.grouped_sum_summary_calls = 0
        self.grouped_count_calls = 0
        self.grouped_sum_calls = 0

    def conjunctive_scan_count(self, predicates) -> int:
        self.scan_count_calls += 1
        return 11

    def grouped_count(self, query):
        self.grouped_count_calls += 1
        return ({"region": "east", "count": 7},)

    def grouped_sum(self, query):
        self.grouped_sum_calls += 1
        return ({"region": "east", "sum": 123},)

    def grouped_count_summary(self, query) -> dict[str, int]:
        self.grouped_count_summary_calls += 1
        return {"east": 7, "west": 4}

    def grouped_sum_summary(self, query) -> dict[str, int]:
        self.grouped_sum_summary_calls += 1
        return {"east": 123, "west": 456}

    def close(self) -> None:
        pass


class Goal1128EmbreeDbCompactSummaryContractTest(unittest.TestCase):
    def test_embree_prepared_dataset_exposes_compact_summary_methods(self) -> None:
        from rtdsl import embree_runtime

        self.assertTrue(hasattr(embree_runtime.PreparedEmbreeDbDataset, "conjunctive_scan_count"))
        self.assertTrue(hasattr(embree_runtime.PreparedEmbreeDbDataset, "grouped_count_summary"))
        self.assertTrue(hasattr(embree_runtime.PreparedEmbreeDbDataset, "grouped_sum_summary"))

    def test_regional_embree_compact_summary_avoids_group_row_materialization(self) -> None:
        from examples import rtdl_v0_7_db_app_demo as regional

        fake = _FakeEmbreeDataset()
        with mock.patch.object(regional, "_prepare_dataset", return_value=fake):
            with regional.prepare_session("embree", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual(fake.scan_count_calls, 1)
        self.assertEqual(fake.grouped_count_summary_calls, 1)
        self.assertEqual(fake.grouped_sum_summary_calls, 1)
        self.assertEqual(fake.grouped_count_calls, 0)
        self.assertEqual(fake.grouped_sum_calls, 0)
        self.assertEqual(payload["native_continuation_backend"], "embree_db_compact_summary")
        self.assertIn("query_grouped_count_summary_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_count_and_materialize_sec", payload["run_phases"])

    def test_sales_embree_compact_summary_avoids_group_row_materialization(self) -> None:
        from examples import rtdl_sales_risk_screening as sales

        fake = _FakeEmbreeDataset()
        with mock.patch.object(sales, "_prepare_dataset", return_value=fake):
            with sales.prepare_session("embree", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual(fake.scan_count_calls, 1)
        self.assertEqual(fake.grouped_count_summary_calls, 1)
        self.assertEqual(fake.grouped_sum_summary_calls, 1)
        self.assertEqual(fake.grouped_count_calls, 0)
        self.assertEqual(fake.grouped_sum_calls, 0)
        self.assertEqual(payload["native_continuation_backend"], "embree_db_compact_summary")
        self.assertIn("query_grouped_sum_summary_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_sum_and_materialize_sec", payload["run_phases"])


if __name__ == "__main__":
    unittest.main()
