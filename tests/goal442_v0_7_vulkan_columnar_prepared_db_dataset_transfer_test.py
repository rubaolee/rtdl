from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import db_perf_grouped_count_reference
from rtdsl.db_perf import db_perf_grouped_sum_reference
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_grouped_sum_case


def _require_vulkan():
    try:
        rt.vulkan_version()
    except Exception as exc:
        raise unittest.SkipTest(f"Vulkan backend unavailable: {exc}") from exc


class Goal442VulkanColumnarPreparedDbDatasetTransferTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _require_vulkan()

    def test_columnar_conjunctive_scan_matches_row_transfer_and_python_truth(self):
        case = make_conjunctive_scan_case(2048)
        reference_rows = rt.run_cpu_python_reference(db_perf_conjunctive_scan_reference, **case)
        row_dataset = rt.prepare_vulkan_db_dataset(
            case["table"],
            primary_fields=("ship_date", "discount", "quantity"),
            transfer="row",
        )
        columnar_dataset = rt.prepare_vulkan_db_dataset(
            case["table"],
            primary_fields=("ship_date", "discount", "quantity"),
            transfer="columnar",
        )
        try:
            row_rows = row_dataset.conjunctive_scan(case["predicates"])
            columnar_rows = columnar_dataset.conjunctive_scan(case["predicates"])
        finally:
            row_dataset.close()
            columnar_dataset.close()

        self.assertEqual(row_rows, reference_rows)
        self.assertEqual(columnar_rows, reference_rows)

    def test_columnar_grouped_count_matches_row_transfer_and_python_truth(self):
        case = make_grouped_count_case(2048)
        reference_rows = rt.run_cpu_python_reference(db_perf_grouped_count_reference, **case)
        row_dataset = rt.prepare_vulkan_db_dataset(
            case["table"],
            primary_fields=("ship_date", "quantity"),
            transfer="row",
        )
        columnar_dataset = rt.prepare_vulkan_db_dataset(
            case["table"],
            primary_fields=("ship_date", "quantity"),
            transfer="columnar",
        )
        try:
            row_rows = row_dataset.grouped_count(case["query"])
            columnar_rows = columnar_dataset.grouped_count(case["query"])
        finally:
            row_dataset.close()
            columnar_dataset.close()

        self.assertEqual(row_rows, reference_rows)
        self.assertEqual(columnar_rows, reference_rows)

    def test_columnar_grouped_sum_matches_row_transfer_and_python_truth(self):
        case = make_grouped_sum_case(2048)
        reference_rows = rt.run_cpu_python_reference(db_perf_grouped_sum_reference, **case)
        row_dataset = rt.prepare_vulkan_db_dataset(
            case["table"],
            primary_fields=("ship_date", "discount"),
            transfer="row",
        )
        columnar_dataset = rt.prepare_vulkan_db_dataset(
            case["table"],
            primary_fields=("ship_date", "discount"),
            transfer="columnar",
        )
        try:
            row_rows = row_dataset.grouped_sum(case["query"])
            columnar_rows = columnar_dataset.grouped_sum(case["query"])
        finally:
            row_dataset.close()
            columnar_dataset.close()

        self.assertEqual(row_rows, reference_rows)
        self.assertEqual(columnar_rows, reference_rows)

    def test_invalid_transfer_mode_rejected(self):
        case = make_conjunctive_scan_case(8)
        with self.assertRaisesRegex(ValueError, "transfer"):
            rt.prepare_vulkan_db_dataset(case["table"], transfer="invalid")


if __name__ == "__main__":
    unittest.main()
