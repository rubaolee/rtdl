import unittest
from unittest import mock

from examples import rtdl_dbscan_clustering_app as dbscan
from examples import rtdl_outlier_detection_app as outlier


class Goal695OptixFixedRadiusSummaryTest(unittest.TestCase):
    def test_outlier_app_can_use_optix_threshold_summary_rows(self):
        def fake_count_rows(query_points, search_points, *, radius, threshold):
            self.assertEqual(query_points, search_points)
            self.assertEqual(radius, outlier.RADIUS)
            self.assertEqual(threshold, outlier.MIN_NEIGHBORS_INCLUDING_SELF)
            return tuple(
                {
                    "query_id": row["point_id"],
                    "neighbor_count": min(int(row["neighbor_count"]), threshold),
                    "threshold_reached": 0 if bool(row["is_outlier"]) else 1,
                }
                for row in outlier.brute_force_outlier_rows(query_points)
            )

        with mock.patch.object(outlier.rt, "fixed_radius_count_threshold_2d_optix", side_effect=fake_count_rows):
            result = outlier.run_app("optix", optix_summary_mode="rt_count_threshold")

        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["native_summary_row_count"], result["point_count"])
        self.assertEqual(result["outlier_point_ids"], [7, 8])
        self.assertIn("fixed-radius count prototype", result["boundary"])

    def test_dbscan_app_can_use_optix_core_flag_summary_rows(self):
        def fake_count_rows(query_points, search_points, *, radius, threshold):
            self.assertEqual(query_points, search_points)
            self.assertEqual(radius, dbscan.EPSILON)
            self.assertEqual(threshold, dbscan.MIN_POINTS)
            return tuple(
                {
                    "query_id": row["point_id"],
                    "neighbor_count": min(int(row["neighbor_count"]), threshold),
                    "threshold_reached": 1 if bool(row["is_core"]) else 0,
                }
                for row in dbscan.brute_force_core_flag_rows(query_points)
            )

        with mock.patch.object(dbscan.rt, "fixed_radius_count_threshold_2d_optix", side_effect=fake_count_rows):
            result = dbscan.run_app("optix", optix_summary_mode="rt_core_flags")

        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["cluster_rows"], ())
        self.assertEqual(len(result["core_flag_rows"]), result["point_count"])
        self.assertIn("core predicate prototype", result["boundary"])

    def test_native_sources_define_optix_traversal_not_cuda_row_wrapper(self):
        root = outlier.ROOT
        core_text = (root / "src" / "native" / "optix" / "rtdl_optix_core.cpp").read_text(encoding="utf-8")
        api_text = (root / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        runtime_text = (root / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        for phrase in (
            "__raygen__frn_count_probe",
            "__intersection__frn_count_isect",
            "__anyhit__frn_count_anyhit",
            "optixTrace(params.traversable",
            "optixTerminateRay",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, core_text)
        self.assertIn("rtdl_optix_run_fixed_radius_count_threshold", api_text)
        self.assertIn("fixed_radius_count_threshold_2d_optix", runtime_text)


if __name__ == "__main__":
    unittest.main()
