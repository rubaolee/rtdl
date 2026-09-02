from dataclasses import dataclass
from pathlib import Path
import re
import unittest

from case_studies.linear_rtccd_owner_grouped import (
    DirectedObstacleEdge,
    LinearRTCCDOwnerGroupedProblem,
    LinearTrajectoryCandidate,
    SweptSphereSegment,
    UndirectedObstacleEdge,
    bidirect_obstacle_edges,
    evaluate_owner_grouped_collision_reference,
    execute_problem,
    prepare_problem,
    segment_segment_distance2,
)
from case_studies.linear_rtccd_owner_grouped.fixtures import (
    REGISTERED_SURFACE_GAP_FLOOR,
    deterministic_scale_case,
    registered_local_cases,
)
from case_studies.linear_rtccd_owner_grouped.run_local_validation import (
    STORED_RECEIPT,
    build_local_validation_receipt,
)


class _Prepared:
    def __init__(self, result):
        self._result = result
        self.execute_count = 0
        self.close_count = 0

    @property
    def lifecycle_receipt(self):
        return {"execution_count": self.execute_count}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def execute(self, batch):
        self.batch = batch
        self.execute_count += 1
        return self._result

    def close(self):
        self.close_count += 1


class _Materialized:
    def __init__(self, result):
        self.result = result
        self.static = None

    def prepare(self, static):
        self.static = static
        self.prepared = _Prepared(self.result)
        return self.prepared


class _FailingClosePrepared(_Prepared):
    def close(self):
        raise OSError("generic close failed")


@dataclass(frozen=True)
class _GenericResult:
    owner_hit_bits: tuple[int, ...]
    any_hit: int
    hit_owner_count: int
    query_completion_tokens: tuple[int, ...]
    output_sha256: str = "a" * 64
    physical_receipt: dict = None
    traversal_receipt: dict = None

    def __post_init__(self):
        object.__setattr__(self, "physical_receipt", {"generic": True})
        object.__setattr__(self, "traversal_receipt", {"generic": True})


class SuccessorLinearRTCCDOwnerGroupedAppTest(unittest.TestCase):
    def test_independent_segment_distance_handles_cross_parallel_and_endpoint(self):
        self.assertEqual(segment_segment_distance2(
            (-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0)), 0.0)
        self.assertAlmostEqual(segment_segment_distance2(
            (0, 0, 0), (1, 0, 0), (0, 2, 0), (1, 2, 0)), 4.0)
        self.assertAlmostEqual(segment_segment_distance2(
            (0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0)), 1.0)

    def test_registered_fixture_oracle_matches_all_expected_owner_bits(self):
        cases = registered_local_cases()
        self.assertEqual(len(cases), 6)
        for case in cases:
            with self.subTest(case=case.case_id):
                observed = evaluate_owner_grouped_collision_reference(case.problem)
                self.assertEqual(observed.per_trajectory_collision, case.expected_bits)
                self.assertEqual(observed.any_collision, int(any(case.expected_bits)))
                self.assertGreaterEqual(
                    observed.minimum_surface_gap,
                    REGISTERED_SURFACE_GAP_FLOOR,
                )
                admission = case.problem.surface_crossing_domain_admission()
                self.assertEqual(
                    admission["schema"],
                    "rtdl.case_study.linear_rtccd_surface_crossing_domain.v2",
                )
                self.assertGreater(
                    admission["minimum_query_length_lower_bound"],
                    admission["maximum_capsule_diameter_upper_bound"],
                )
                self.assertGreater(admission["certified_length_margin"], 0.0)
                self.assertTrue(admission["fully_contained_query_excluded"])
                self.assertFalse(
                    admission["pairwise_collision_discovery_performed"])

    def test_start_inside_fixture_has_one_inside_endpoint_and_reverse_query(self):
        case = next(row for row in registered_local_cases()
                    if row.case_id == "start_inside_bidirectional")
        edges = case.problem.directed_obstacle_edges
        self.assertEqual(len(edges), 2)
        self.assertEqual(edges[0].start, edges[1].end)
        self.assertEqual(edges[0].end, edges[1].start)
        segment = case.problem.trajectories[0].swept_segments[0]
        self.assertEqual(edges[0].start, (1.0, 0.0, 0.0))
        self.assertEqual(segment.start, (0.0, 0.0, 0.0))
        self.assertEqual(segment.end, (2.0, 0.0, 0.0))
        self.assertGreater(segment.radius, 0.0)

    def test_bidirect_expansion_and_problem_order_are_deterministic(self):
        edge = UndirectedObstacleEdge("wall", (0, 0, 0), (1, 0, 0))
        directed = bidirect_obstacle_edges((edge,))
        self.assertEqual(tuple(row.edge_id for row in directed),
                         ("wall:forward", "wall:reverse"))
        first = registered_local_cases()[3].problem
        reordered = LinearRTCCDOwnerGroupedProblem(
            first.problem_id,
            tuple(reversed(first.trajectories)),
            tuple(reversed(first.directed_obstacle_edges)),
        )
        self.assertEqual(first.public_inputs(), reordered.public_inputs())
        self.assertEqual(first.identity_projection(), reordered.identity_projection())

    def test_public_input_maps_many_primitives_to_same_owner(self):
        case = next(row for row in registered_local_cases()
                    if row.case_id == "many_primitives_one_owner")
        static, batch = case.problem.public_inputs()
        self.assertEqual(static.owner_ids, (0, 0, 1))
        self.assertEqual(static.owner_count, 2)
        self.assertEqual(len(batch.queries), 2)
        projection = case.problem.identity_projection()
        self.assertEqual(
            [row["owner_id"] for row in projection["primitive_to_owner"]],
            [0, 0, 1],
        )

    def test_application_front_door_uses_generic_owner_result(self):
        case = registered_local_cases()[3]
        generic = _GenericResult(
            case.expected_bits,
            1,
            2,
            (0,) * len(case.problem.directed_obstacle_edges),
        )
        materialized = _Materialized(generic)
        observed = execute_problem(materialized, case.problem)
        self.assertEqual(observed.per_trajectory_collision, (1, 1))
        self.assertEqual(observed.collided_trajectory_ids, ("alpha", "beta"))
        self.assertEqual(observed.any_collision, 1)
        self.assertEqual(materialized.static.owner_ids, (0, 1))

    def test_application_front_door_rejects_inconsistent_generic_metadata(self):
        case = registered_local_cases()[1]
        generic = _GenericResult(
            case.expected_bits,
            0,
            1,
            (0,) * len(case.problem.directed_obstacle_edges),
        )
        with self.assertRaisesRegex(RuntimeError, "metadata"):
            execute_problem(_Materialized(generic), case.problem)

    def test_application_prepared_front_door_reuses_one_generic_owner(self):
        case = registered_local_cases()[3]
        materialized = _Materialized(_GenericResult(
            case.expected_bits,
            1,
            2,
            (0,) * len(case.problem.directed_obstacle_edges),
        ))
        prepared = prepare_problem(materialized, case.problem)
        with prepared:
            first = prepared.execute()
            second = prepared.execute()
            self.assertEqual(prepared.lifecycle_receipt["execution_count"], 2)
        self.assertEqual(first, second)
        self.assertEqual(materialized.prepared.execute_count, 2)
        self.assertEqual(materialized.prepared.close_count, 1)
        prepared.close()
        self.assertEqual(materialized.prepared.close_count, 1)
        with self.assertRaisesRegex(RuntimeError, "closed"):
            prepared.execute()

    def test_application_context_preserves_body_and_cleanup_failures(self):
        case = registered_local_cases()[0]
        materialized = _Materialized(_GenericResult(
            case.expected_bits,
            int(any(case.expected_bits)),
            sum(case.expected_bits),
            (0,) * len(case.problem.directed_obstacle_edges),
        ))
        prepared = prepare_problem(materialized, case.problem)
        prepared._generic = _FailingClosePrepared(materialized.result)
        primary = ValueError("application body failed")
        with self.assertRaisesRegex(
                RuntimeError,
                "application body failed.*generic close failed") as caught:
            prepared.__exit__(ValueError, primary, None)
        self.assertIs(caught.exception.__cause__, primary)
        self.assertFalse(prepared._closed)

    def test_deterministic_scale_ladder_matches_independent_oracle(self):
        for dimensions in ((4, 2, 2, 1), (9, 3, 3, 2), (16, 4, 5, 1)):
            owners, segments, stride, duplicates = dimensions
            with self.subTest(dimensions=dimensions):
                first = deterministic_scale_case(
                    owners, segments, hit_stride=stride,
                    duplicate_query_factor=duplicates)
                second = deterministic_scale_case(
                    owners, segments, hit_stride=stride,
                    duplicate_query_factor=duplicates)
                self.assertEqual(first, second)
                observed = evaluate_owner_grouped_collision_reference(first.problem)
                self.assertEqual(observed.per_trajectory_collision,
                                 first.expected_bits)
                static, batch = first.problem.public_inputs()
                self.assertEqual(len(static.segment_indices), owners * segments)
                self.assertEqual(
                    len(batch.queries),
                    2 * duplicates * segments
                    * len(range(0, owners, stride)),
                )

    def test_scale_ladder_rejects_invalid_or_excessive_dimensions(self):
        for dimensions in ((0, 1), (1, 0), (4097, 1), (1024, 2048)):
            with self.subTest(dimensions=dimensions):
                with self.assertRaises(ValueError):
                    deterministic_scale_case(*dimensions)
        with self.assertRaisesRegex(ValueError, "query cardinality"):
            deterministic_scale_case(
                4096, 1, hit_stride=1, duplicate_query_factor=1024)
        with self.assertRaisesRegex(ValueError, "oracle pair cardinality"):
            deterministic_scale_case(2048, 1, hit_stride=1)

    def test_surface_crossing_domain_rejects_possible_fully_contained_query(self):
        trajectory = LinearTrajectoryCandidate("owner", (
            SweptSphereSegment(
                "segment", "sphere", (0, 0, 0), (2, 0, 0), 0.25),
        ))
        problem = LinearRTCCDOwnerGroupedProblem(
            "contained-query",
            (trajectory,),
            (DirectedObstacleEdge(
                "inside", (0.5, 0, 0), (1.5, 0, 0)),),
        )
        with self.assertRaisesRegex(ValueError, "surface-crossing"):
            problem.surface_crossing_domain_admission()

    def test_duplicate_geometric_queries_do_not_change_boolean_result(self):
        duplicate = next(row for row in registered_local_cases()
                         if row.case_id == "duplicate_geometric_queries")
        single = next(row for row in registered_local_cases()
                      if row.case_id == "one_owner_hit")
        self.assertEqual(
            evaluate_owner_grouped_collision_reference(
                duplicate.problem).per_trajectory_collision,
            evaluate_owner_grouped_collision_reference(
                single.problem).per_trajectory_collision,
        )

    def test_engine_successor_modules_contain_no_application_vocabulary(self):
        root = Path(__file__).resolve().parents[1]
        modules = (
            "src/rtdsl/v4_owner_grouped_any_hit.py",
            "src/rtdsl/v4_curve_owner_grouped_any_hit.py",
            "src/rtdsl/v4_curve_owner_grouped_any_hit_standard_library.py",
            "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_compiler.py",
            "src/rtdsl/v4_curve_owner_grouped_any_hit_prepared_runtime.py",
            "src/rtdsl/v4_curve_owner_grouped_any_hit_public.py",
        )
        for relative in modules:
            source = (root / relative).read_text(encoding="utf-8").lower()
            for forbidden in ("collision", "trajectory", "robot", "pose", "rtccd"):
                self.assertIsNone(
                    re.search(rf"\b{re.escape(forbidden)}\b", source), relative)

    def test_invalid_ids_and_zero_segments_fail_closed(self):
        with self.assertRaises(ValueError):
            SweptSphereSegment("", "sphere", (0, 0, 0), (1, 0, 0), 0.1)
        with self.assertRaises(ValueError):
            SweptSphereSegment("s", "sphere", (0, 0, 0), (0, 0, 0), 0.1)
        with self.assertRaises(ValueError):
            DirectedObstacleEdge("edge", (0, 0, 0), (0, 0, 0))
        segment = SweptSphereSegment(
            "s", "sphere", (0, 0, 0), (1, 0, 0), 0.1)
        with self.assertRaises(ValueError):
            LinearTrajectoryCandidate("t", (segment, segment))

    def test_local_validation_receipt_rebuilds_exactly(self):
        import json

        observed = build_local_validation_receipt()
        expected = json.loads(STORED_RECEIPT.read_text(
            encoding="utf-8", errors="strict"))
        self.assertEqual(observed, expected)
        self.assertEqual(
            observed["schema"],
            "rtdl.successor_owner_grouped_any_hit.local_validation.v3",
        )
        self.assertEqual(
            observed["status"],
            "LOCAL_RECEIPT_PASS__GPU_FUNCTIONAL_EVIDENCE_IS_SEPARATE",
        )
        self.assertFalse(observed["external_pod_evidence_embedded"])
        self.assertEqual(observed["registered_semantic_case_count"], 6)
        self.assertEqual(observed["registered_scale_case_count"], 3)
        self.assertEqual(observed["matching_local_case_count"], 9)
        self.assertTrue(observed["fresh_native_builder_ready"])
        self.assertTrue(observed["public_app_gpu_runner_ready"])
        self.assertEqual(observed["optix_launch_count"], 0)
        self.assertFalse(observed["benchmark_app_claimed"])
        self.assertTrue(all(
            row["all_required_markers_present"]
            for row in observed["author_source"]["evidence"]
        ))


if __name__ == "__main__":
    unittest.main()
