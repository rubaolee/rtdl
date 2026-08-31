from __future__ import annotations

from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import rtdsl as rt
from rtdsl.v4_hierarchy_frontier import (
    HierarchyFrontierError,
    HierarchyFrontierSchema,
    HierarchyReducer,
    compile_hierarchy_frontier,
    hierarchy_content_sha256,
)
from goal5764_m6_hierarchy_fixtures import (
    hierarchy_coverage_fixture,
    rt_barneshut_author_fixture,
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _schema(spec, reducer: HierarchyReducer) -> HierarchyFrontierSchema:
    hierarchy = spec.prepared_hierarchy.hierarchy
    return HierarchyFrontierSchema(
        producer_contract_sha256=hashlib.sha256(b"test-producer").hexdigest(),
        hierarchy_sha256=hierarchy_content_sha256(spec),
        reducer=reducer,
        maximum_output_rows=hierarchy.point_count,
        maximum_visits_per_source=hierarchy.node_count * 2 + 1,
    )


class Goal5764V4HierarchyFrontierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.count_spec, cls.coverage = hierarchy_coverage_fixture()

    def test_closed_count_contract_compiles(self) -> None:
        compiled = compile_hierarchy_frontier(
            self.count_spec, _schema(self.count_spec, HierarchyReducer.AGGREGATE_COUNT))
        self.assertEqual(self.count_spec.prepared_hierarchy.hierarchy.point_count, compiled.point_count)
        self.assertEqual("aggregate_hierarchy_continuation_reduce_3d", compiled.to_dict()["program_bundle"])
        self.assertFalse(compiled.to_dict()["new_native_symbol_added"])

    def test_wrong_reducer_fails_closed(self) -> None:
        with self.assertRaisesRegex(HierarchyFrontierError, "reducer_binding"):
            compile_hierarchy_frontier(
                self.count_spec,
                _schema(self.count_spec, HierarchyReducer.INVERSE_SQUARE_SCALAR_SUM),
            )

    def test_same_shape_different_content_fails_hierarchy_binding(self) -> None:
        schema = _schema(self.count_spec, HierarchyReducer.AGGREGATE_COUNT)
        hierarchy = self.count_spec.prepared_hierarchy.hierarchy
        changed = rt.aggregate_hierarchy_3d(
            **{
                name: (
                    tuple(value + 1.0 if index == 0 else value
                          for index, value in enumerate(hierarchy.point_x))
                    if name == "point_x" else getattr(hierarchy, name)
                )
                for name in (
                    "point_x", "point_y", "point_z", "point_weight",
                    "node_cx", "node_cy", "node_cz", "node_half_size", "node_weight",
                    "member_offsets", "member_indices", "child_offsets", "child_indices",
                    "node_next_index", "node_rope_index", "source_leaf_node_index",
                    "node_subtree_end_index",
                )
            }
        )
        changed_spec = rt.aggregate_frontier_reduce_spec_3d(
            rt.prepare_aggregate_hierarchy_3d(changed),
            opening=self.count_spec.opening,
            reducer=self.count_spec.reducer,
        )
        with self.assertRaisesRegex(HierarchyFrontierError, "hierarchy_binding"):
            compile_hierarchy_frontier(changed_spec, schema)

    def test_truncating_capacity_fails_closed(self) -> None:
        schema = replace(
            _schema(self.count_spec, HierarchyReducer.AGGREGATE_COUNT),
            maximum_output_rows=2,
        )
        with self.assertRaisesRegex(HierarchyFrontierError, "output_capacity"):
            compile_hierarchy_frontier(self.count_spec, schema)

    def test_visit_bound_is_compiler_derived_not_user_tuned(self) -> None:
        schema = replace(
            _schema(self.count_spec, HierarchyReducer.AGGREGATE_COUNT),
            maximum_visits_per_source=1000,
        )
        with self.assertRaisesRegex(HierarchyFrontierError, "visit_bound"):
            compile_hierarchy_frontier(self.count_spec, schema)

    def test_size_distance_nonthreaded_opening_is_rejected(self) -> None:
        illegal = rt.aggregate_frontier_reduce_spec_3d(
            self.count_spec.prepared_hierarchy,
            opening=rt.SizeDistanceOpening(max_ratio=1.0),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )
        with self.assertRaisesRegex(HierarchyFrontierError, "opening"):
            compile_hierarchy_frontier(
                illegal, _schema(illegal, HierarchyReducer.AGGREGATE_COUNT))

    def test_coverage_consumer_has_exact_reference_semantics(self) -> None:
        reference = rt.run_aggregate_frontier_reduce_reference_3d(
            rt.aggregate_frontier_reduce_execution_contract_3d(
                self.count_spec, backend="reference", max_output_rows=3))
        values = tuple(row["reducer_value_0"] for row in reference["rows"])
        self.assertEqual(self.coverage["expected_reducer_values"], values)

    def test_author_fixture_matches_independent_author_reference(self) -> None:
        spec, expected, metadata = rt_barneshut_author_fixture(256)
        reference = rt.run_aggregate_frontier_reduce_reference_3d(
            rt.aggregate_frontier_reduce_execution_contract_3d(
                spec, backend="reference", max_output_rows=256))
        actual = tuple(float(row["reducer_value_0"]) * metadata["force_scale"]
                       for row in reference["rows"])
        oracle = tuple(float(row["scalar_force"]) for row in expected)
        self.assertEqual(256, len(actual))
        self.assertLess(max(abs(left - right) for left, right in zip(actual, oracle)), 1.0e-9)
        self.assertGreaterEqual(metadata["node_count"], 10)

    def test_product_has_no_application_or_publication_dispatch(self) -> None:
        text = (ROOT / "src/rtdsl/v4_hierarchy_frontier.py").read_text().lower()
        for forbidden in ("barneshut", "rt_barneshut", "paper_app", "dataset_name"):
            self.assertNotIn(forbidden, text)

    def test_true_optix_native_is_one_launch_with_per_node_trace(self) -> None:
        text = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text()
        begin = text.index("// Generic true-OptiX aggregate-hierarchy continuation executor.")
        end = text.index(
            "static void write_prepared_fixed_radius_count_threshold_3d_device_outputs_optix",
            begin,
        )
        block = text[begin:end]
        self.assertIn("optixTrace(", block)
        self.assertIn("optixLaunch(", block)
        self.assertIn("node_count * 2ull + 1ull", block)
        self.assertIn("rtdl_optix_bind_traversal_audit_context(", block)

    def test_product_does_not_raise_trace_or_callable_depth(self) -> None:
        metadata = _schema(
            self.count_spec, HierarchyReducer.AGGREGATE_COUNT).semantic_dict()
        self.assertEqual(1, metadata["max_trace_depth"])
        self.assertEqual(0, metadata["max_callable_depth"])
        source = inspect.getsource(compile_hierarchy_frontier).lower()
        self.assertNotIn("setmaxtracedepth", source)
        self.assertNotIn("callableprogram", source)


if __name__ == "__main__":
    unittest.main()
