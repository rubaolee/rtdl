from __future__ import annotations

import unittest
from unittest import mock


class Goal1202DbChunkedCompactSummaryTest(unittest.TestCase):
    def test_sales_risk_split_helper_bounds_large_prepared_db_jobs(self) -> None:
        from examples import rtdl_sales_risk_screening as sales

        self.assertEqual(sales._split_copies(100000, 50000), (50000, 50000))
        self.assertEqual(sales._split_copies(100001, 50000), (50000, 50000, 1))

    def test_database_app_reports_chunked_compact_summary_metadata(self) -> None:
        from examples import rtdl_database_analytics_app as database
        from examples import rtdl_sales_risk_screening as sales
        from tests.goal1156_db_compact_summary_batch_contract_test import _AppBatchDataset

        datasets = [_AppBatchDataset(), _AppBatchDataset()]
        with (
            mock.patch.object(sales, "DB_COMPACT_SUMMARY_CHUNK_COPIES", 2),
            mock.patch.object(sales, "_prepare_dataset", side_effect=datasets),
        ):
            with database.prepare_session("optix", scenario="sales_risk", copies=3) as session:
                payload = session.run(output_mode="compact_summary")

        sales_section = payload["sections"]["sales_risk"]
        self.assertTrue(sales_section["session"]["chunked_compact_summary"])
        self.assertEqual(sales_section["session"]["chunk_copies"], [2, 1])
        self.assertEqual(sales_section["prepared_dataset"]["transfer"], "chunked_columnar")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["native_continuation_backend"], "optix_db_compact_summary")


if __name__ == "__main__":
    unittest.main()
