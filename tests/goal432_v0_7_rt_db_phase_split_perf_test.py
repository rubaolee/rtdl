from __future__ import annotations

import unittest
from unittest import mock

from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import measure_backend_family_split


class _FakePrepared:
    def __init__(self, rows):
        self._rows = rows

    def run(self):
        return self._rows


class _FakePrepareKernel:
    def __init__(self, rows):
        self._rows = rows

    def bind(self, **inputs):
        return _FakePrepared(self._rows)


class Goal432PhaseSplitPerfTest(unittest.TestCase):
    def test_measure_backend_family_split_reports_prepare_execute_and_total(self):
        case = make_conjunctive_scan_case(64)
        expected_rows = ({"row_id": 1}, {"row_id": 2})
        with mock.patch("rtdsl.db_perf.run_cpu_python_reference", return_value=expected_rows):
            with mock.patch("rtdsl.db_perf.prepare_embree", return_value=_FakePrepareKernel(expected_rows)):
                report = measure_backend_family_split(
                    db_perf_conjunctive_scan_reference,
                    case,
                    repeats=2,
                    backend_name="embree",
                )

        self.assertEqual(report["row_count"], 2)
        self.assertIn("embree_prepare_seconds_samples", report)
        self.assertIn("embree_execute_seconds_samples", report)
        self.assertIn("embree_total_seconds_samples", report)
        self.assertEqual(len(report["embree_prepare_seconds_samples"]), 2)
        self.assertEqual(len(report["embree_execute_seconds_samples"]), 2)
        self.assertEqual(len(report["embree_total_seconds_samples"]), 2)


if __name__ == "__main__":
    unittest.main()
