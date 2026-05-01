import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_dbscan_clustering_app as dbscan
from examples import rtdl_outlier_detection_app as outlier
from tests.goal757_prepared_optix_fixed_radius_count_test import _FakePreparedOptixFixedRadius
from tests.goal757_prepared_optix_fixed_radius_count_test import _dbscan_count_rows
from tests.goal757_prepared_optix_fixed_radius_count_test import _outlier_count_rows


class Goal952DensityNativeContinuationTest(unittest.TestCase):
    def test_outlier_embree_compact_path_reports_native_continuation(self) -> None:
        payload = outlier.run_app(
            "embree",
            copies=1,
            output_mode="density_summary",
        )

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "embree_threshold_count")
        self.assertEqual(payload["neighbor_row_count"], 0)
        self.assertTrue(payload["matches_oracle"])

    def test_outlier_prepared_optix_path_reports_native_continuation(self) -> None:
        def fake_prepare(search_points, *, max_radius):
            return _FakePreparedOptixFixedRadius(_outlier_count_rows(search_points))

        with mock.patch.object(outlier.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            payload = outlier.prepare_session("optix").run()

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count")
        self.assertEqual(payload["neighbor_row_count"], 0)
        self.assertTrue(payload["matches_oracle"])

    def test_dbscan_embree_core_flag_path_reports_native_continuation(self) -> None:
        payload = dbscan.run_app(
            "embree",
            copies=1,
            output_mode="core_flags",
        )

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "embree_threshold_count")
        self.assertEqual(payload["neighbor_row_count"], 0)
        self.assertEqual(payload["cluster_rows"], ())
        self.assertTrue(payload["matches_oracle"])

    def test_dbscan_prepared_optix_path_reports_native_continuation(self) -> None:
        def fake_prepare(search_points, *, max_radius):
            return _FakePreparedOptixFixedRadius(_dbscan_count_rows(search_points))

        with mock.patch.object(dbscan.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            payload = dbscan.prepare_session("optix").run()

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count")
        self.assertEqual(payload["neighbor_row_count"], 0)
        self.assertEqual(payload["cluster_rows"], ())
        self.assertTrue(payload["matches_oracle"])

    def test_full_python_cluster_path_does_not_overstate_native_continuation(self) -> None:
        payload = dbscan.run_app("cpu_python_reference", copies=1)

        self.assertFalse(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "none")
        self.assertNotEqual(payload["cluster_rows"], ())
        self.assertTrue(payload["matches_oracle"])


if __name__ == "__main__":
    unittest.main()
