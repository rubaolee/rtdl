from __future__ import annotations

import unittest
from unittest import mock


class _FakeInner:
    transfer = "columnar"


class _FakeOptixSalesDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 12
        self.scan_count_calls = 0
        self.grouped_count_calls = 0
        self.grouped_sum_calls = 0
        self.grouped_count_summary_calls = 0
        self.grouped_sum_summary_calls = 0

    def conjunctive_scan_count(self, predicates) -> int:
        self.scan_count_calls += 1
        return 8

    def grouped_count(self, query):
        self.grouped_count_calls += 1
        return ({"region": "west", "count": 4},)

    def grouped_sum(self, query):
        self.grouped_sum_calls += 1
        return ({"region": "west", "sum": 860},)

    def grouped_count_summary(self, query):
        self.grouped_count_summary_calls += 1
        return {"central": 2, "east": 2, "west": 4}

    def grouped_sum_summary(self, query):
        self.grouped_sum_summary_calls += 1
        return {"central": 520, "east": 620, "west": 860}

    def close(self) -> None:
        pass


class Goal851OptixDbSalesGroupedSummaryFastpathTest(unittest.TestCase):
    def test_sales_compact_summary_prefers_group_summary_fastpaths(self) -> None:
        from examples import rtdl_sales_risk_screening as sales

        fake = _FakeOptixSalesDataset()
        with mock.patch.object(sales, "_prepare_dataset", return_value=fake):
            with sales.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual(fake.scan_count_calls, 1)
        self.assertEqual(fake.grouped_count_summary_calls, 1)
        self.assertEqual(fake.grouped_sum_summary_calls, 1)
        self.assertEqual(fake.grouped_count_calls, 0)
        self.assertEqual(fake.grouped_sum_calls, 0)
        self.assertEqual(payload["summary"]["risky_order_count"], 8)
        self.assertEqual(
            payload["summary"]["risky_order_count_by_region"],
            {"central": 2, "east": 2, "west": 4},
        )
        self.assertEqual(
            payload["summary"]["risky_revenue_by_region"],
            {"central": 520, "east": 620, "west": 860},
        )
        self.assertEqual(payload["summary"]["highest_risk_region"], "west")
        self.assertIn("query_grouped_count_summary_sec", payload["run_phases"])
        self.assertIn("query_grouped_sum_summary_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_count_and_materialize_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_sum_and_materialize_sec", payload["run_phases"])


if __name__ == "__main__":
    unittest.main()
