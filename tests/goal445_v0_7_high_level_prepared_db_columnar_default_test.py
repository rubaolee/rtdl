from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import db_perf_grouped_count_reference
from rtdsl.db_perf import db_perf_grouped_sum_reference
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_grouped_sum_case


def _require_embree():
    try:
        rt.embree_version()
    except Exception as exc:
        raise unittest.SkipTest(f"Embree backend unavailable: {exc}") from exc


def _require_optix():
    try:
        rt.optix_version()
    except Exception as exc:
        raise unittest.SkipTest(f"OptiX backend unavailable: {exc}") from exc


def _require_vulkan():
    try:
        rt.vulkan_version()
    except Exception as exc:
        raise unittest.SkipTest(f"Vulkan backend unavailable: {exc}") from exc


class Goal445HighLevelPreparedDbColumnarDefaultTest(unittest.TestCase):
    def _assert_prepared_uses_columnar_and_matches_reference(self, prepare_fn, kernel_fn, case):
        reference_rows = rt.run_cpu_python_reference(kernel_fn, **case)
        prepared = prepare_fn(kernel_fn).bind(**case)
        try:
            rows = prepared.run()
            self.assertEqual(prepared.dataset.transfer, "columnar")
            self.assertEqual(rows, reference_rows)
        finally:
            prepared.dataset.close()

    def test_embree_prepared_db_workloads_use_columnar_transfer(self):
        _require_embree()
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_embree,
            db_perf_conjunctive_scan_reference,
            make_conjunctive_scan_case(2048),
        )
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_embree,
            db_perf_grouped_count_reference,
            make_grouped_count_case(2048),
        )
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_embree,
            db_perf_grouped_sum_reference,
            make_grouped_sum_case(2048),
        )

    def test_optix_prepared_db_workloads_use_columnar_transfer(self):
        _require_optix()
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_optix,
            db_perf_conjunctive_scan_reference,
            make_conjunctive_scan_case(2048),
        )
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_optix,
            db_perf_grouped_count_reference,
            make_grouped_count_case(2048),
        )
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_optix,
            db_perf_grouped_sum_reference,
            make_grouped_sum_case(2048),
        )

    def test_vulkan_prepared_db_workloads_use_columnar_transfer(self):
        _require_vulkan()
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_vulkan,
            db_perf_conjunctive_scan_reference,
            make_conjunctive_scan_case(2048),
        )
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_vulkan,
            db_perf_grouped_count_reference,
            make_grouped_count_case(2048),
        )
        self._assert_prepared_uses_columnar_and_matches_reference(
            rt.prepare_vulkan,
            db_perf_grouped_sum_reference,
            make_grouped_sum_case(2048),
        )

    def test_direct_prepared_dataset_defaults_remain_row_transfer(self):
        case = make_conjunctive_scan_case(8)
        dataset = rt.prepare_embree_db_dataset(case["table"])
        try:
            self.assertEqual(dataset._dataset.transfer, "row")
        finally:
            dataset.close()


if __name__ == "__main__":
    unittest.main()
