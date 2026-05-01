from __future__ import annotations

import unittest
from unittest import mock


class _FakeInner:
    transfer = "columnar"


class _FakeOptixDashboardDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 14
        self.scan_count_calls = 0
        self.grouped_count_calls = 0
        self.grouped_sum_calls = 0
        self.grouped_count_summary_calls = 0
        self.grouped_sum_summary_calls = 0

    def conjunctive_scan_count(self, predicates) -> int:
        self.scan_count_calls += 1
        return 6

    def grouped_count(self, query):
        self.grouped_count_calls += 1
        return ({"region": "east", "count": 4},)

    def grouped_sum(self, query):
        self.grouped_sum_calls += 1
        return ({"region": "east", "sum": 900},)

    def grouped_count_summary(self, query):
        self.grouped_count_summary_calls += 1
        return {"east": 4, "west": 2}

    def grouped_sum_summary(self, query):
        self.grouped_sum_summary_calls += 1
        return {"east": 900, "west": 240}

    def close(self) -> None:
        pass


class Goal850OptixDbGroupedSummaryFastpathTest(unittest.TestCase):
    def test_regional_compact_summary_prefers_group_summary_fastpaths(self) -> None:
        from examples import rtdl_v0_7_db_app_demo as regional

        fake = _FakeOptixDashboardDataset()
        with mock.patch.object(regional, "_prepare_dataset", return_value=fake):
            with regional.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertEqual(fake.scan_count_calls, 1)
        self.assertEqual(fake.grouped_count_summary_calls, 1)
        self.assertEqual(fake.grouped_sum_summary_calls, 1)
        self.assertEqual(fake.grouped_count_calls, 0)
        self.assertEqual(fake.grouped_sum_calls, 0)
        self.assertEqual(payload["summary"]["promo_order_count"], 6)
        self.assertEqual(payload["summary"]["open_order_count_by_region"], {"east": 4, "west": 2})
        self.assertEqual(payload["summary"]["web_revenue_by_region"], {"east": 900, "west": 240})
        self.assertIn("query_grouped_count_summary_sec", payload["run_phases"])
        self.assertIn("query_grouped_sum_summary_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_count_and_materialize_sec", payload["run_phases"])
        self.assertNotIn("query_grouped_sum_and_materialize_sec", payload["run_phases"])


if __name__ == "__main__":
    unittest.main()
