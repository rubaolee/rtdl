from __future__ import annotations

import unittest
from unittest import mock


class _FakeInner:
    transfer = "columnar"


class _FakeSalesDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 12
        self.scan_count_calls = 0
        self.scan_row_calls = 0

    def conjunctive_scan_count(self, predicates) -> int:
        self.scan_count_calls += 1
        return 8

    def conjunctive_scan(self, predicates):
        self.scan_row_calls += 1
        return ({"row_id": 1},)

    def grouped_count(self, query):
        return ({"region": "west", "count": 8},)

    def grouped_sum(self, query):
        return ({"region": "west", "sum": 400},)

    def close(self) -> None:
        pass


class _FakeRegionalDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 14
        self.scan_count_calls = 0
        self.scan_row_calls = 0

    def conjunctive_scan_count(self, predicates) -> int:
        self.scan_count_calls += 1
        return 6

    def conjunctive_scan(self, predicates):
        self.scan_row_calls += 1
        return ({"row_id": 1},)

    def grouped_count(self, query):
        return ({"region": "east", "count": 4},)

    def grouped_sum(self, query):
        return ({"region": "east", "sum": 900},)

    def close(self) -> None:
        pass


class Goal804DbCompactSummaryScanCountTest(unittest.TestCase):
    def test_sales_compact_summary_uses_scan_count_not_row_materialization(self) -> None:
        from examples import rtdl_sales_risk_screening as sales

        fake = _FakeSalesDataset()
        with mock.patch.object(sales, "_prepare_dataset", return_value=fake):
            with sales.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual(fake.scan_count_calls, 1)
        self.assertEqual(fake.scan_row_calls, 0)
        self.assertEqual(payload["row_counts"]["scan"], 8)
        self.assertEqual(payload["summary"]["risky_order_count"], 8)
        self.assertNotIn("risky_order_ids", payload["summary"])
        self.assertIn("query_conjunctive_scan_count_sec", payload["run_phases"])
        self.assertNotIn("query_conjunctive_scan_and_materialize_sec", payload["run_phases"])

    def test_regional_compact_summary_uses_scan_count_not_row_materialization(self) -> None:
        from examples import rtdl_v0_7_db_app_demo as regional

        fake = _FakeRegionalDataset()
        with mock.patch.object(regional, "_prepare_dataset", return_value=fake):
            with regional.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual(fake.scan_count_calls, 1)
        self.assertEqual(fake.scan_row_calls, 0)
        self.assertEqual(payload["summary"]["promo_order_count"], 6)
        self.assertIn("query_conjunctive_scan_count_sec", payload["run_phases"])
        self.assertNotIn("query_conjunctive_scan_and_materialize_sec", payload["run_phases"])


if __name__ == "__main__":
    unittest.main()
