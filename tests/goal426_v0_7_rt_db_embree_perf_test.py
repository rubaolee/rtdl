import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl import FakePostgresqlConnection
from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import db_perf_grouped_count_reference
from rtdsl.db_perf import hash_rows
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_sales_perf_table
from rtdsl.db_perf import measure_backend_family
from rtdsl.db_perf import measure_postgresql_conjunctive_scan
from rtdsl.db_perf import measure_postgresql_grouped_count
from rtdsl.db_perf import median_seconds


class Goal426V07RtDbEmbreePerfTest(unittest.TestCase):
    def test_make_sales_perf_table_is_deterministic(self) -> None:
        self.assertEqual(make_sales_perf_table(8), make_sales_perf_table(8))
        self.assertEqual(len(make_sales_perf_table(8)), 8)

    def test_hash_rows_is_stable(self) -> None:
        rows = ({"row_id": 1}, {"row_id": 2})
        self.assertEqual(hash_rows(rows), hash_rows(rows))

    def test_median_seconds_handles_odd_and_even_samples(self) -> None:
        self.assertEqual(median_seconds([3.0, 1.0, 2.0]), 2.0)
        self.assertEqual(median_seconds([1.0, 2.0, 3.0, 4.0]), 2.5)

    def test_measure_backend_family_reports_row_count_and_hash(self) -> None:
        case = make_conjunctive_scan_case(64)
        report = measure_backend_family(
            db_perf_conjunctive_scan_reference,
            case,
            repeats=1,
        )
        self.assertGreater(report["row_count"], 0)
        self.assertIn("row_hash", report)
        self.assertIn("embree_seconds_median", report)
        self.assertIn("cpu_seconds_median", report)

    def test_measure_postgresql_conjunctive_scan_with_fake_connection(self) -> None:
        case = make_conjunctive_scan_case(32)
        with mock.patch("rtdsl.db_perf.connect_postgresql", return_value=FakeConnectionContext()):
            report = measure_postgresql_conjunctive_scan(
                case["table"],
                case["predicates"],
                dsn="fake",
                repeats=1,
            )
        self.assertGreaterEqual(report["row_count"], 0)
        self.assertIn("postgresql_query_seconds_median", report)

    def test_measure_postgresql_grouped_count_with_fake_connection(self) -> None:
        case = make_grouped_count_case(32)
        with mock.patch("rtdsl.db_perf.connect_postgresql", return_value=FakeConnectionContext()):
            report = measure_postgresql_grouped_count(
                case["table"],
                case["query"],
                dsn="fake",
                repeats=1,
            )
        self.assertGreaterEqual(report["row_count"], 0)
        self.assertIn("postgresql_setup_seconds_median", report)


class FakeConnectionContext:
    def __enter__(self):
        return FakePostgresqlConnection()

    def __exit__(self, exc_type, exc, tb):
        return False


if __name__ == "__main__":
    unittest.main()
