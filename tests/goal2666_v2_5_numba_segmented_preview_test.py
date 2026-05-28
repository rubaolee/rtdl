from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2666V25NumbaSegmentedPreviewTest(unittest.TestCase):
    def test_numba_descriptors_are_safe_without_runtime_import(self):
        count_descriptor = rt.describe_numba_segmented_count_i64()
        sum_descriptor = rt.describe_numba_segmented_sum_f64()

        self.assertEqual(count_descriptor["operation"], "segmented_count_i64")
        self.assertEqual(count_descriptor["partner"], "numba")
        self.assertEqual(count_descriptor["status"], "preview_not_promoted")
        self.assertFalse(count_descriptor["raw_kernel_required"])
        self.assertFalse(count_descriptor["replaces_rt_traversal"])
        self.assertFalse(count_descriptor["promoted_performance_path"])
        self.assertEqual(count_descriptor["group_id_validation_mode"], "device_resident_error_flag")
        self.assertEqual(sum_descriptor["operation"], "segmented_sum_f64")
        self.assertEqual(sum_descriptor["partner"], "numba")
        self.assertEqual(sum_descriptor["status"], "preview_not_promoted")
        self.assertFalse(sum_descriptor["raw_kernel_required"])
        self.assertFalse(sum_descriptor["replaces_rt_traversal"])
        self.assertFalse(sum_descriptor["promoted_performance_path"])
        self.assertEqual(sum_descriptor["group_id_validation_mode"], "device_resident_error_flag")
        self.assertIn("NUMBA_GROUP_ID_VALIDATION_MODE", rt.__all__)
        self.assertIn("run_numba_segmented_count_i64", rt.__all__)
        self.assertIn("run_numba_segmented_sum_f64", rt.__all__)

    def test_numba_module_is_lazy_import_and_records_no_app_terms(self):
        source = (ROOT / "src/rtdsl/numba_partner_continuation.py").read_text()

        self.assertIn("@cuda.jit", source)
        self.assertIn("cuda.atomic.add", source)
        self.assertIn("_numba_group_id_validation_kernel", source)
        self.assertIn("cuda.atomic.max(error_flag, 0, 1)", source)
        self.assertIn("group_ids must be in [0, group_count)", source)
        self.assertNotIn("host_groups = group_ids.copy_to_host()", source)
        self.assertNotIn("RawKernel", source)
        self.assertNotIn("raydb", source.lower())
        self.assertNotIn("dbscan", source.lower())
        self.assertNotIn("barnes", source.lower())

    def test_numba_availability_probe_is_boolean(self):
        self.assertIsInstance(rt.numba_partner_available(), bool)

    def test_docs_record_goal2666_boundary(self):
        report = (ROOT / "docs/reports/goal2666_v2_5_numba_segmented_preview_2026-05-27.md").read_text()

        self.assertIn("Numba fallback", report)
        self.assertIn("preview_not_promoted", report)
        self.assertIn("no public speedup claim", report)


if __name__ == "__main__":
    unittest.main()
