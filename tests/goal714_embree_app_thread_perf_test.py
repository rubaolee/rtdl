import unittest

from scripts.goal714_embree_app_thread_perf import _canonical_payload
from scripts.goal714_embree_app_thread_perf import _select_cases


class Goal714EmbreeAppThreadPerfHarnessTest(unittest.TestCase):
    def test_select_cases_can_filter_by_group(self):
        cases = _select_cases("all", "polygon_overlap")
        self.assertEqual(
            [case.app for case in cases],
            ["polygon_pair_overlap_area_rows", "polygon_set_jaccard"],
        )

    def test_canonical_payload_ignores_backend_metadata(self):
        left = {
            "app": "demo",
            "backend": "cpu_python_reference",
            "backend_mode": "cpu_exact",
            "rows": [{"x": 1.00000000000004}],
        }
        right = {
            "app": "demo",
            "backend": "embree",
            "backend_mode": "embree_native_assisted",
            "rows": [{"x": 1.00000000000005}],
        }
        self.assertEqual(_canonical_payload(left), _canonical_payload(right))


if __name__ == "__main__":
    unittest.main()
