import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.internal.rtdl_sorting import derive_sorts_from_rows
from examples.internal.rtdl_sorting import expected_hit_counts
from examples.internal.rtdl_sorting import hit_counts_from_rows
from examples.internal.rtdl_sorting import make_ray_hit_sort_case
from examples.internal.rtdl_sorting import quicksort_reference
from examples.internal.rtdl_sorting import ray_hit_sorting_reference
from examples.internal.rtdl_sorting import run_sorting_backend
from examples.internal.rtdl_sorting import stable_sort_from_hit_counts
from examples.internal.rtdl_sorting import stable_sort_reference
from tests._embree_support import embree_available
from tests.rtdsl_vulkan_test import vulkan_available


def optix_available() -> bool:
    try:
        rt.optix_version()
    except Exception:
        return False
    return True


def native_oracle_available() -> bool:
    try:
        rt.oracle_version()
    except Exception:
        return False
    return True


class RtDlSortingTest(unittest.TestCase):
    def test_sorting_lowering_uses_lsi(self) -> None:
        plan = rt.lower_to_execution_plan(rt.compile_kernel(ray_hit_sorting_reference))
        self.assertEqual(plan.workload_kind, "lsi")

    def test_expected_hit_count_law_with_duplicates(self) -> None:
        values = (3, 1, 4, 1, 5, 0, 2, 5)
        self.assertEqual(expected_hit_counts(values), (4, 7, 3, 7, 2, 8, 5, 2))

    def test_make_case_rejects_negative_values(self) -> None:
        with self.assertRaises(ValueError):
            make_ray_hit_sort_case((1, -1, 2))

    def test_empty_and_singleton_inputs(self) -> None:
        self.assertEqual(expected_hit_counts(()), ())
        self.assertEqual(stable_sort_reference(()), ())
        singleton = (7,)
        self.assertEqual(expected_hit_counts(singleton), (1,))
        self.assertEqual(stable_sort_reference(singleton), singleton)
        self.assertEqual(quicksort_reference(singleton), singleton)

    def test_cpu_python_reference_matches_formula_and_sorted_order(self) -> None:
        values = (3, 1, 4, 1, 5, 0, 2, 5)
        result = run_sorting_backend("cpu_python_reference", values)
        self.assertEqual(result["hit_counts"], expected_hit_counts(values))
        self.assertEqual(result["ascending"], stable_sort_reference(values))
        self.assertEqual(result["descending"], stable_sort_reference(values, descending=True))
        self.assertEqual(result["ascending"], quicksort_reference(values))
        self.assertEqual(result["descending"], quicksort_reference(values, descending=True))

    @unittest.skipUnless(native_oracle_available(), "Native oracle is not available in the current environment")
    def test_cpu_native_matches_python_reference(self) -> None:
        values = (3, 1, 4, 1, 5, 0, 2, 5)
        python_rows = run_sorting_backend("cpu_python_reference", values)["rows"]
        native_rows = run_sorting_backend("cpu", values)["rows"]
        self.assertEqual(hit_counts_from_rows(values, native_rows), hit_counts_from_rows(values, python_rows))
        self.assertEqual(derive_sorts_from_rows(values, native_rows), derive_sorts_from_rows(values, python_rows))

    def test_duplicate_order_is_stable(self) -> None:
        values = (3, 1, 3, 1, 3)
        hit_counts = expected_hit_counts(values)
        ascending = stable_sort_from_hit_counts(values, hit_counts, descending=False)
        descending = stable_sort_from_hit_counts(values, hit_counts, descending=True)
        self.assertEqual(ascending, (1, 1, 3, 3, 3))
        self.assertEqual(descending, (3, 3, 3, 1, 1))

    def test_formula_scales_to_10k(self) -> None:
        values = tuple((index * 37) % 97 for index in range(10_000))
        hit_counts = expected_hit_counts(values)
        self.assertEqual(len(hit_counts), len(values))
        self.assertEqual(max(hit_counts), len(values))
        self.assertEqual(stable_sort_from_hit_counts(values, hit_counts), stable_sort_reference(values))

    @unittest.skipUnless(embree_available(), "Embree is not installed in the current environment")
    def test_embree_small_case_matches_cpu_sort(self) -> None:
        values = (3, 1, 4, 1, 5, 0, 2, 5)
        cpu_result = run_sorting_backend("cpu", values)
        embree_result = run_sorting_backend("embree", values)
        self.assertEqual(embree_result["hit_counts"], cpu_result["hit_counts"])
        self.assertEqual(embree_result["ascending"], cpu_result["ascending"])
        self.assertEqual(embree_result["descending"], cpu_result["descending"])

    @unittest.skipUnless(vulkan_available(), "Vulkan is not available or RTDL Vulkan library not found")
    def test_vulkan_small_case_matches_cpu_sort(self) -> None:
        values = (3, 1, 4, 1, 5, 0, 2, 5)
        cpu_result = run_sorting_backend("cpu", values)
        vulkan_result = run_sorting_backend("vulkan", values)
        self.assertEqual(vulkan_result["hit_counts"], cpu_result["hit_counts"])
        self.assertEqual(vulkan_result["ascending"], cpu_result["ascending"])
        self.assertEqual(vulkan_result["descending"], cpu_result["descending"])

    @unittest.skipUnless(optix_available(), "OptiX is not available in the current environment")
    def test_optix_small_case_matches_cpu_sort(self) -> None:
        values = (3, 1, 4, 1, 5, 0, 2, 5)
        cpu_result = run_sorting_backend("cpu", values)
        optix_result = run_sorting_backend("optix", values)
        self.assertEqual(optix_result["hit_counts"], cpu_result["hit_counts"])
        self.assertEqual(optix_result["ascending"], cpu_result["ascending"])
        self.assertEqual(optix_result["descending"], cpu_result["descending"])
