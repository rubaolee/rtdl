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


class Goal436VulkanNativePreparedDbDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _require_vulkan()

    def _assert_prepared_matches_reference_twice(self, kernel_fn, case):
        reference_rows = rt.run_cpu_python_reference(kernel_fn, **case)
        direct_rows = rt.run_vulkan(kernel_fn, **case)
        prepared = rt.prepare_vulkan(kernel_fn).bind(**case)
        try:
            first_rows = prepared.run()
            second_rows = prepared.run()
        finally:
            prepared.dataset.close()

        self.assertEqual(direct_rows, reference_rows)
        self.assertEqual(first_rows, reference_rows)
        self.assertEqual(second_rows, reference_rows)

    def test_conjunctive_scan_reuses_native_dataset_and_preserves_rows(self):
        self._assert_prepared_matches_reference_twice(
            db_perf_conjunctive_scan_reference,
            make_conjunctive_scan_case(2048),
        )

    def test_grouped_count_reuses_native_dataset_and_preserves_rows(self):
        self._assert_prepared_matches_reference_twice(
            db_perf_grouped_count_reference,
            make_grouped_count_case(2048),
        )

    def test_grouped_sum_reuses_native_dataset_and_preserves_rows(self):
        self._assert_prepared_matches_reference_twice(
            db_perf_grouped_sum_reference,
            make_grouped_sum_case(2048),
        )

    def test_public_prepared_dataset_runs_multiple_query_shapes(self):
        table = make_conjunctive_scan_case(2048)["table"]
        dataset = rt.prepare_vulkan_db_dataset(table, primary_fields=("ship_date", "discount", "quantity"))
        try:
            scan_rows = dataset.conjunctive_scan(
                {
                    "clauses": (
                        ("ship_date", "between", 40, 220),
                        ("discount", "between", 3, 7),
                        ("quantity", "lt", 20),
                    )
                }
            )
            count_rows = dataset.grouped_count(
                {
                    "predicates": (
                        ("ship_date", "between", 40, 220),
                        ("quantity", "lt", 20),
                    ),
                    "group_keys": ("region",),
                }
            )
            sum_rows = dataset.grouped_sum(
                {
                    "predicates": (
                        ("ship_date", "ge", 60),
                        ("discount", "le", 8),
                    ),
                    "group_keys": ("region",),
                    "value_field": "revenue",
                }
            )
        finally:
            dataset.close()

        self.assertEqual(scan_rows, rt.run_cpu_python_reference(db_perf_conjunctive_scan_reference, **make_conjunctive_scan_case(2048)))
        self.assertEqual(count_rows, rt.run_cpu_python_reference(db_perf_grouped_count_reference, **make_grouped_count_case(2048)))
        self.assertEqual(sum_rows, rt.run_cpu_python_reference(db_perf_grouped_sum_reference, **make_grouped_sum_case(2048)))


if __name__ == "__main__":
    unittest.main()
