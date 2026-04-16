import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl import FakePostgresqlConnection
from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import measure_backend_family
from rtdsl.db_perf import measure_postgresql_conjunctive_scan
from rtdsl.db_perf import measure_postgresql_grouped_count


class Goal427V07RtDbOptixPerfTest(unittest.TestCase):
    def test_measure_backend_family_reports_optix_fields(self) -> None:
        case = make_conjunctive_scan_case(16)
        with mock.patch("rtdsl.db_perf.run_cpu_python_reference", return_value=(({"row_id": 1},))), mock.patch(
            "rtdsl.db_perf.run_cpu", return_value=(({"row_id": 1},))
        ), mock.patch("rtdsl.db_perf.run_optix", return_value=(({"row_id": 1},))):
            report = measure_backend_family(
                db_perf_conjunctive_scan_reference,
                case,
                repeats=1,
                backend_name="optix",
            )
        self.assertEqual(report["row_count"], 1)
        self.assertIn("optix_seconds_median", report)

    def test_measure_backend_family_rejects_unknown_backend(self) -> None:
        case = make_conjunctive_scan_case(8)
        with self.assertRaisesRegex(ValueError, "unsupported backend family"):
            measure_backend_family(
                db_perf_conjunctive_scan_reference,
                case,
                repeats=1,
                backend_name="unknown",
            )

    def test_measure_postgresql_conjunctive_scan_with_fake_connection(self) -> None:
        case = make_conjunctive_scan_case(32)
        with mock.patch("rtdsl.db_perf.connect_postgresql", return_value=FakeConnectionContext()):
            report = measure_postgresql_conjunctive_scan(
                case["table"],
                case["predicates"],
                dsn="fake",
                repeats=1,
            )
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
        self.assertIn("postgresql_setup_seconds_median", report)


class FakeConnectionContext:
    def __enter__(self):
        return FakePostgresqlConnection()

    def __exit__(self, exc_type, exc, tb):
        return False


if __name__ == "__main__":
    unittest.main()
