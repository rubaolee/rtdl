from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from rtdsl.optix_runtime import _find_optional_backend_symbol
from rtdsl.optix_runtime import _load_optix_library
from examples import rtdl_dbscan_clustering_app as dbscan
from examples import rtdl_outlier_detection_app as outlier


def prepared_optix_fixed_radius_available() -> bool:
    try:
        lib = _load_optix_library()
    except Exception:
        return False
    return (
        _find_optional_backend_symbol(lib, "rtdl_optix_prepare_fixed_radius_count_threshold_2d") is not None
        and _find_optional_backend_symbol(lib, "rtdl_optix_run_prepared_fixed_radius_count_threshold_2d") is not None
        and _find_optional_backend_symbol(lib, "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d") is not None
    )


class _FakePreparedOptixFixedRadius:
    def __init__(self, rows):
        self._rows = tuple(rows)
        self.closed = False

    def run(self, query_points, *, radius, threshold=0):
        if self.closed:
            raise RuntimeError("fake prepared handle is closed")
        return tuple(self._rows)

    def count_threshold_reached(self, query_points, *, radius, threshold=0):
        if self.closed:
            raise RuntimeError("fake prepared handle is closed")
        return sum(1 for row in self._rows if int(row["threshold_reached"]) != 0)

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


def _outlier_count_rows(points):
    return tuple(
        {
            "query_id": row["point_id"],
            "neighbor_count": min(int(row["neighbor_count"]), outlier.MIN_NEIGHBORS_INCLUDING_SELF),
            "threshold_reached": 0 if bool(row["is_outlier"]) else 1,
        }
        for row in outlier.brute_force_outlier_rows(points)
    )


def _dbscan_count_rows(points):
    return tuple(
        {
            "query_id": row["point_id"],
            "neighbor_count": min(int(row["neighbor_count"]), dbscan.MIN_POINTS),
            "threshold_reached": 1 if bool(row["is_core"]) else 0,
        }
        for row in dbscan.brute_force_core_flag_rows(points)
    )


class Goal757PreparedOptixFixedRadiusPortableTest(unittest.TestCase):
    def test_empty_prepared_handle_needs_no_native_library(self):
        with rt.prepare_optix_fixed_radius_count_threshold_2d((), max_radius=1.0) as prepared:
            self.assertEqual(prepared.max_radius, 1.0)
            self.assertEqual(prepared.run((), radius=0.5, threshold=1), ())
            self.assertEqual(prepared.count_threshold_reached((), radius=0.5, threshold=1), 0)

    def test_prepared_handle_rejects_radius_above_max_radius(self):
        with rt.prepare_optix_fixed_radius_count_threshold_2d((), max_radius=1.0) as prepared:
            with self.assertRaisesRegex(ValueError, "max_radius"):
                prepared.run((), radius=1.5, threshold=1)

    def test_closed_prepared_handle_is_rejected(self):
        prepared = rt.prepare_optix_fixed_radius_count_threshold_2d((), max_radius=1.0)
        prepared.close()
        with self.assertRaisesRegex(RuntimeError, "closed"):
            prepared.run((), radius=0.5, threshold=1)

    def test_outlier_app_prepared_optix_summary_matches_oracle(self):
        def fake_prepare(search_points, *, max_radius):
            self.assertEqual(max_radius, outlier.RADIUS)
            return _FakePreparedOptixFixedRadius(_outlier_count_rows(search_points))

        with mock.patch.object(outlier.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            result = outlier.run_app("optix", optix_summary_mode="rt_count_threshold_prepared")

        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["native_summary_row_count"], result["point_count"])
        self.assertEqual(result["outlier_point_ids"], [7, 8])

    def test_outlier_prepared_session_matches_oracle_and_closes(self):
        def fake_prepare(search_points, *, max_radius):
            return _FakePreparedOptixFixedRadius(_outlier_count_rows(search_points))

        with mock.patch.object(outlier.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            session = outlier.prepare_session("optix")
            result = session.run()
            session.close()

        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["execution_mode"], "prepared_session")
        with self.assertRaisesRegex(RuntimeError, "closed"):
            session.run()

    def test_dbscan_app_prepared_optix_core_flags_match_oracle(self):
        def fake_prepare(search_points, *, max_radius):
            self.assertEqual(max_radius, dbscan.EPSILON)
            return _FakePreparedOptixFixedRadius(_dbscan_count_rows(search_points))

        with mock.patch.object(dbscan.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            result = dbscan.run_app("optix", optix_summary_mode="rt_core_flags_prepared")

        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["neighbor_row_count"], 0)
        self.assertEqual(result["cluster_rows"], ())
        self.assertEqual(len(result["core_flag_rows"]), result["point_count"])

    def test_dbscan_prepared_session_matches_oracle_and_closes(self):
        def fake_prepare(search_points, *, max_radius):
            return _FakePreparedOptixFixedRadius(_dbscan_count_rows(search_points))

        with mock.patch.object(dbscan.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            session = dbscan.prepare_session("optix")
            result = session.run()
            session.close()

        self.assertTrue(result["matches_oracle"])
        self.assertEqual(result["execution_mode"], "prepared_session")
        with self.assertRaisesRegex(RuntimeError, "closed"):
            session.run()

    def test_fixed_radius_profiler_scalar_threshold_count_matches_oracle(self):
        profiler = __import__(
            "scripts.goal757_optix_fixed_radius_prepared_perf",
            fromlist=["run_suite"],
        )

        def unpack_points(points):
            if hasattr(points, "records") and hasattr(points, "count"):
                return tuple(
                    rt.Point(
                        id=int(points.records[index].id),
                        x=float(points.records[index].x),
                        y=float(points.records[index].y),
                    )
                    for index in range(points.count)
                )
            return points

        def fake_prepare(search_points, *, max_radius):
            points = unpack_points(search_points)
            is_outlier_fixture = any(int(point.id) == 4 and float(point.x) > 1.0 for point in points)
            rows = _outlier_count_rows(points) if is_outlier_fixture else _dbscan_count_rows(points)
            return _FakePreparedOptixFixedRadius(rows)

        with mock.patch.object(rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            payload = profiler.run_suite(copies=1, iterations=1, result_mode="threshold_count")

        self.assertEqual(payload["result_mode"], "threshold_count")
        for result in payload["results"]:
            with self.subTest(app=result["app"]):
                self.assertEqual(result["result_mode"], "threshold_count")
                self.assertTrue(result["prepared_output"]["matches_oracle"])
                self.assertEqual(result["prepared_optix_postprocess_sec"]["median_sec"], 0.0)

    def test_native_sources_export_prepared_optix_fixed_radius_symbols(self):
        root = outlier.ROOT
        api_text = (root / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workload_text = (root / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        runtime_text = (root / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        init_text = (root / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")
        for phrase in (
            "rtdl_optix_prepare_fixed_radius_count_threshold_2d",
            "rtdl_optix_run_prepared_fixed_radius_count_threshold_2d",
            "rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d",
            "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, api_text)
                self.assertIn(phrase, runtime_text)
        self.assertIn("PreparedFixedRadiusCountThreshold2D", workload_text)
        self.assertIn("prepare_optix_fixed_radius_count_threshold_2d", init_text)


@unittest.skipUnless(prepared_optix_fixed_radius_available(), "prepared OptiX fixed-radius symbols are not available")
class Goal757PreparedOptixFixedRadiusNativeTest(unittest.TestCase):
    def test_native_prepared_rows_match_one_shot_rows(self):
        points = outlier.make_outlier_case()["points"]
        expected = rt.fixed_radius_count_threshold_2d_optix(
            points,
            points,
            radius=outlier.RADIUS,
            threshold=outlier.MIN_NEIGHBORS_INCLUDING_SELF,
        )
        with rt.prepare_optix_fixed_radius_count_threshold_2d(points, max_radius=outlier.RADIUS) as prepared:
            observed = prepared.run(
                points,
                radius=outlier.RADIUS,
                threshold=outlier.MIN_NEIGHBORS_INCLUDING_SELF,
            )
        self.assertEqual(observed, expected)

    def test_native_outlier_and_dbscan_prepared_sessions_match_oracles(self):
        with outlier.prepare_session("optix") as outlier_session:
            outlier_result = outlier_session.run()
        with dbscan.prepare_session("optix") as dbscan_session:
            dbscan_result = dbscan_session.run()

        self.assertTrue(outlier_result["matches_oracle"])
        self.assertTrue(dbscan_result["matches_oracle"])
        self.assertEqual(outlier_result["neighbor_row_count"], 0)
        self.assertEqual(dbscan_result["neighbor_row_count"], 0)


if __name__ == "__main__":
    unittest.main()
