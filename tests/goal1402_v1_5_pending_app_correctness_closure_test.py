from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_barnes_hut_force_app as barnes
from examples import rtdl_hausdorff_distance_app as hausdorff
from examples import rtdl_road_hazard_screening as road
from examples import rtdl_segment_polygon_hitcount as segment


class _PreparedThresholdAllCovered:
    def __call__(
        self,
        *,
        search_points,
        query_points,
        radius: float,
        threshold: int,
        backend: str,
        max_radius: float,
        prepare_scene,
    ):
        self.query_count = len(query_points)
        self.radius = radius
        self.threshold = threshold
        self.backend = backend
        self.max_radius = max_radius
        return {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "threshold_reached_count": len(query_points),
            "run_phases": {
                "scene_prepare_sec": 0.001,
                "query_fixed_radius_threshold_reached_count_sec": 0.002,
            },
        }


class Goal1402PendingAppCorrectnessClosureTest(unittest.TestCase):
    def test_segment_polygon_hitcount_embree_and_optix_surface_match_cpu_rows(self):
        cpu = segment.run_case("cpu_python_reference", "authored_segment_polygon_minimal")
        embree = segment.run_case("embree", "authored_segment_polygon_minimal")

        with mock.patch.object(segment.rt, "run_optix", return_value=tuple(cpu["rows"])):
            optix = segment.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                optix_mode="host_indexed",
            )

        self.assertEqual(embree["rows"], cpu["rows"])
        self.assertEqual(optix["rows"], cpu["rows"])
        self.assertEqual(embree["row_count"], cpu["row_count"])
        self.assertEqual(optix["row_count"], cpu["row_count"])
        self.assertEqual(optix["native_continuation_backend"], "none")

    def test_road_hazard_summary_embree_and_optix_surface_match_cpu_count(self):
        cpu = road.run_case("cpu_python_reference", output_mode="summary")
        cpu_rows = road.run_case("cpu_python_reference", output_mode="rows")
        embree = road.run_case("embree", output_mode="summary")

        with mock.patch.object(road.rt, "run_optix", return_value=tuple(cpu_rows["rows"])):
            optix = road.run_case("optix", output_mode="summary", optix_mode="host_indexed")

        self.assertEqual(embree["priority_segment_count"], cpu["priority_segment_count"])
        self.assertEqual(optix["priority_segment_count"], cpu["priority_segment_count"])
        self.assertEqual(embree["priority_segments"], cpu["priority_segments"])
        self.assertEqual(optix["priority_segments"], cpu["priority_segments"])
        self.assertTrue(cpu["summary_materializes_rows"])
        self.assertTrue(optix["summary_materializes_rows"])

    def test_hausdorff_embree_summary_and_optix_threshold_surface_match_oracle_decision(self):
        embree = hausdorff.run_app("embree", copies=1, embree_result_mode="directed_summary")
        threshold = float(embree["oracle"]["hausdorff_distance"])
        fake = _PreparedThresholdAllCovered()

        with mock.patch.object(
            hausdorff.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            side_effect=fake,
        ):
            optix = hausdorff.run_app(
                "optix",
                copies=1,
                optix_summary_mode="directed_threshold_prepared",
                hausdorff_threshold=threshold,
                require_rt_core=True,
            )

        self.assertTrue(embree["matches_oracle"])
        self.assertTrue(optix["matches_oracle"])
        self.assertTrue(optix["within_threshold"])
        self.assertTrue(optix["oracle_within_threshold"])
        self.assertEqual(optix["native_continuation_backend"], "optix_threshold_count")
        self.assertEqual(fake.backend, "optix")

    def test_barnes_hut_embree_summary_and_optix_node_coverage_match_oracle_decision(self):
        embree = barnes.run_app("embree", output_mode="candidate_summary")
        fake = _PreparedThresholdAllCovered()

        with mock.patch.object(
            barnes.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            side_effect=fake,
        ):
            optix = barnes.run_app(
                "optix",
                optix_summary_mode="node_coverage_prepared",
                node_radius=barnes.NODE_DISCOVERY_RADIUS,
                require_rt_core=True,
            )

        self.assertEqual(embree["candidate_row_count"], 24)
        self.assertEqual(embree["body_count_with_candidates"], 6)
        self.assertTrue(optix["matches_oracle"])
        self.assertTrue(optix["oracle_decision_matches"])
        self.assertTrue(optix["node_coverage"]["all_bodies_have_node_candidate"])
        self.assertEqual(optix["node_coverage"]["generic_primitive"], "FIXED_RADIUS_COUNT_THRESHOLD_2D")
        self.assertEqual(optix["node_coverage"]["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(fake.backend, "optix")


if __name__ == "__main__":
    unittest.main()
