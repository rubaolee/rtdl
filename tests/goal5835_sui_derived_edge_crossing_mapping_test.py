"""Goal5835 bounded Sui-derived mapping tests."""

from __future__ import annotations

import inspect
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from case_studies.sui_derived_edge_crossing_core import (  # noqa: E402
    ObstacleTriangle,
    deduplicate_triangle_edges,
    execute_registered_problem,
    trajectory_to_swept_segments,
)
from case_studies.sui_derived_edge_crossing_core import (  # noqa: E402
    bounded_piecewise_linear_core as core,
)
from case_studies.sui_derived_edge_crossing_core.fixtures import (  # noqa: E402
    load_registered_cases,
)
from case_studies.sui_derived_edge_crossing_core import (  # noqa: E402
    independent_edge_capsule_oracle as oracle,
)


AUTHORITY = ROOT / "history/internal_docs/goal5834_b1_fixture_preaction_20260830/FIXTURE_AUTHORITY.json"
WORKERS = ROOT / "history/internal_docs/goal5834_b1_fixture_preaction_20260830/WORKER_INPUTS.json"


class Goal5835SuiDerivedEdgeCrossingMappingTest(unittest.TestCase):
    def test_piecewise_trajectory_maps_one_to_one_to_capsules(self):
        rows = trajectory_to_swept_segments(
            7, ((0, 0, 0), (1, 0, 0), (1, 1, 0)), 0.25,
            first_path_segment_id=100)
        self.assertEqual(len(rows), 2)
        self.assertEqual([row.path_segment_id for row in rows], [100, 101])
        self.assertEqual(rows[0].end, rows[1].start)
        self.assertEqual([row.application_id for row in rows], [100, 101])

    def test_triangle_edge_dedup_is_deterministic_and_reconstructable(self):
        triangles = (
            ObstacleTriangle(
                "t1", ("a", "b", "c"),
                ((0, 0, 0), (1, 0, 0), (0, 1, 0))),
            ObstacleTriangle(
                "t2", ("b", "d", "c"),
                ((1, 0, 0), (1, 1, 0), (0, 1, 0))),
        )
        forward = deduplicate_triangle_edges(triangles)
        reversed_input = deduplicate_triangle_edges(tuple(reversed(triangles)))
        self.assertEqual(forward, reversed_input)
        self.assertEqual(len(forward), 5)
        shared = next(row for row in forward
                      if row.source_triangle_ids == ("t1", "t2"))
        self.assertEqual(shared.edge_id, "b--c")

    def test_all_registered_mappings_reproduce_executed_public_bytes(self):
        cases = load_registered_cases(AUTHORITY, WORKERS)
        self.assertEqual(len(cases), 11)
        self.assertEqual(len({row.family_id for row in cases}), 10)
        pair_count = 0
        for case in cases:
            static, batch = case.problem.public_inputs()
            self.assertEqual(
                static.commitment_sha256,
                case.public_static_input_commitment_sha256)
            self.assertEqual(
                batch.commitment_sha256,
                case.public_query_commitment_sha256)
            projection = case.problem.identity_projection()
            self.assertEqual(
                len(projection["curve_to_path"]), len(case.problem.swept_segments))
            self.assertEqual(
                len(projection["query_to_edge"]), len(case.problem.obstacle_edges))
            capsules = tuple((row.start, row.end, row.radius, row.application_id)
                             for row in case.problem.swept_segments)
            edges = tuple((row.start, row.end)
                          for row in case.problem.obstacle_edges)
            bits, collision = oracle.edge_capsule_bits(capsules, edges)
            self.assertEqual(collision, int(any(bits)))
            pair_count += len(capsules) * len(edges)
        self.assertEqual(pair_count, 21)

    def test_application_execution_route_has_no_cpu_geometry_or_expected_bits(self):
        source = inspect.getsource(core.execute_registered_problem)
        for forbidden in (
            "oracle", "distance", "capsule_entry", "expected_output",
            "verify_curve_motion_segments",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("prepared.execute(batch)", source)

    def test_application_aliases_only_the_already_sealed_generic_result(self):
        problem = load_registered_cases(AUTHORITY, WORKERS)[0].problem
        generic = SimpleNamespace(
            per_query_hit=(1,), any_hit=1, output_sha256="a" * 64,
            physical_receipt={"host_aggregation": "OR_after_raw_receipt_seal"},
            traversal_receipt={"physical_executor_classification":
                               "optix_traversal_observed"},
        )

        class Prepared:
            def __enter__(self): return self
            def __exit__(self, *_args): return None
            def execute(self, batch):
                self.batch = batch
                return generic

        prepared = Prepared()
        materialized = SimpleNamespace(prepare=lambda _static: prepared)
        result = execute_registered_problem(materialized, problem)
        self.assertEqual(result.per_edge_hit, (1,))
        self.assertEqual(result.collision, 1)
        self.assertEqual(result.raw_gpu_bit_vector_commitment_sha256, "a" * 64)
        self.assertEqual(result.edge_ids, tuple(
            row.edge_id for row in problem.obstacle_edges))

    def test_independent_oracle_imports_no_rtdsl(self):
        source = inspect.getsource(oracle).lower()
        self.assertNotIn("rtdsl", source)


if __name__ == "__main__":
    unittest.main()
