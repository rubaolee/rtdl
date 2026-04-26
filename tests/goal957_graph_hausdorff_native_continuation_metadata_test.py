from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_graph_analytics_app as graph_app
from examples import rtdl_hausdorff_distance_app as hausdorff_app


class _FakePreparedThreshold:
    def __init__(self, target, max_radius: float):
        self.target = target
        self.max_radius = max_radius

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, query_points, *, radius: float, threshold: int):
        raise AssertionError("Hausdorff OptiX threshold metadata path should use scalar count")

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int):
        return len(query_points)


class _FakePreparedScene:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def count(self, prepared_rays):
        return 1


class _FakePreparedRays:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class Goal957GraphHausdorffNativeContinuationMetadataTest(unittest.TestCase):
    def test_unified_graph_summary_propagates_native_continuation_from_sections(self) -> None:
        payload = graph_app.run_app(
            "cpu_python_reference",
            scenario="all",
            copies=2,
            output_mode="summary",
        )

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "oracle_cpp+oracle_cpp")
        self.assertFalse(payload["rt_core_accelerated"])

    def test_visibility_edges_optix_reports_visibility_pair_native_continuation(self) -> None:
        with (
            mock.patch.object(graph_app.rt, "prepare_optix_ray_triangle_any_hit_2d", return_value=_FakePreparedScene()),
            mock.patch.object(graph_app.rt, "prepare_optix_rays_2d", return_value=_FakePreparedRays()),
            mock.patch.object(graph_app.rt, "visibility_pair_rows") as visibility_pair_rows,
        ):
            payload = graph_app.run_app("optix", scenario="visibility_edges", output_mode="summary")

        section = payload["sections"]["visibility_edges"]
        visibility_pair_rows.assert_not_called()
        self.assertTrue(section["native_continuation_active"])
        self.assertEqual(section["native_continuation_backend"], "optix_prepared_visibility_anyhit_count")
        self.assertTrue(section["rt_core_accelerated"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_prepared_visibility_anyhit_count")
        self.assertTrue(payload["rt_core_accelerated"])

    def test_hausdorff_embree_directed_summary_reports_native_continuation(self) -> None:
        with mock.patch.object(
            hausdorff_app.rt,
            "directed_hausdorff_2d_embree",
            side_effect=(
                {"distance": 0.3, "source_id": 3, "target_id": 103, "row_count": 4},
                {"distance": 0.2, "source_id": 102, "target_id": 2, "row_count": 4},
            ),
        ):
            payload = hausdorff_app.run_app("embree", copies=1, embree_result_mode="directed_summary")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "embree_directed_hausdorff")
        self.assertFalse(payload["rt_core_accelerated"])

    def test_hausdorff_optix_threshold_reports_native_continuation(self) -> None:
        with mock.patch.object(
            hausdorff_app.rt,
            "prepare_optix_fixed_radius_count_threshold_2d",
            side_effect=_FakePreparedThreshold,
        ):
            payload = hausdorff_app.run_app(
                "optix",
                copies=1,
                optix_summary_mode="directed_threshold_prepared",
                hausdorff_threshold=0.4,
                require_rt_core=True,
            )

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count")
        self.assertTrue(payload["rt_core_accelerated"])

    def test_hausdorff_default_knn_rows_do_not_report_native_continuation(self) -> None:
        payload = hausdorff_app.run_app("cpu_python_reference", copies=1)

        self.assertFalse(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "none")
        self.assertFalse(payload["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
