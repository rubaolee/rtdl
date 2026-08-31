from __future__ import annotations

from pathlib import Path
import math
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import rtdsl as rt


def _prepared_three_point_hierarchy() -> rt.PreparedAggregateHierarchy3D:
    hierarchy = rt.aggregate_hierarchy_3d(
        point_x=[0.0, 2.0, 0.0],
        point_y=[0.0, 0.0, 3.0],
        point_z=[0.0, 0.0, 0.0],
        point_weight=[1.0, 2.0, 3.0],
        node_cx=[0.6, 0.0, 1.0],
        node_cy=[0.9, 0.0, 1.5],
        node_cz=[0.0, 0.0, 0.0],
        node_half_size=[3.0, 0.0, 1.5],
        node_weight=[6.0, 1.0, 5.0],
        member_offsets=[0, 0, 1, 3],
        member_indices=[0, 1, 2],
        child_offsets=[0, 2, 2, 2],
        child_indices=[1, 2],
        source_leaf_node_index=[1, 2, 2],
        node_subtree_end_index=[3, 2, 3],
    )
    return rt.prepare_aggregate_hierarchy_3d(hierarchy)


def _execution(
    *,
    backend: str,
    opening: rt.SizeDistanceOpening | rt.LeafOnlyOpening,
    reducer: str,
    max_output_rows: int | None = 3,
) -> rt.AggregateFrontierReduceExecutionContract3D:
    spec = rt.aggregate_frontier_reduce_spec_3d(
        _prepared_three_point_hierarchy(),
        opening=opening,
        reducer=reducer,
    )
    return rt.aggregate_frontier_reduce_execution_contract_3d(
        spec,
        backend=backend,
        max_output_rows=max_output_rows,
    )


def _assert_rows_close(testcase: unittest.TestCase, lhs, rhs) -> None:
    testcase.assertEqual(len(lhs), len(rhs))
    for left, right in zip(lhs, rhs):
        testcase.assertEqual(left["source_id"], right["source_id"])
        testcase.assertEqual(left["visited_node_count"], right["visited_node_count"])
        testcase.assertEqual(left["aggregate_contribution_count"], right["aggregate_contribution_count"])
        testcase.assertEqual(left["exact_contribution_count"], right["exact_contribution_count"])
        testcase.assertEqual(left["status_code"], right["status_code"])
        for key in ("reducer_value_0", "reducer_value_1", "reducer_value_2"):
            testcase.assertTrue(math.isclose(left[key], right[key], rel_tol=1e-12), (key, left[key], right[key]))


class Goal5073AggregateFrontierReduceNumbaParityTest(unittest.TestCase):
    def test_numba_public_symbols_and_metadata_are_exported(self) -> None:
        for name in (
            "AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NUMBA",
            "AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS",
            "aggregate_frontier_reduce_numba_available",
            "aggregate_frontier_reduce_numba_3d",
            "run_aggregate_frontier_reduce_numba_3d",
        ):
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__, name)

        execution = _execution(
            backend="numba",
            opening=rt.LeafOnlyOpening(),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )
        metadata = execution.to_metadata()
        self.assertEqual("optional_numba_cpu_reference_prototype", metadata["backend_status"])
        self.assertTrue(metadata["backend_execution_authorized"])
        self.assertTrue(metadata["numba_execution_authorized"])
        self.assertFalse(metadata["native_backend_symbols_authorized"])

    def test_numba_runtime_missing_fails_closed_without_python_reference_fallback(self) -> None:
        if rt.aggregate_frontier_reduce_numba_available():
            self.skipTest("Numba is available; missing-runtime branch is not active in this environment")
        with self.assertRaisesRegex(RuntimeError, "Numba"):
            rt.aggregate_frontier_reduce_numba_3d(
                _execution(
                    backend="numba",
                    opening=rt.LeafOnlyOpening(),
                    reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
                )
            )

    @unittest.skipUnless(rt.aggregate_frontier_reduce_numba_available(), "Numba is required for parity execution")
    def test_numba_leaf_only_count_matches_cpu_reference(self) -> None:
        reference = rt.aggregate_frontier_reduce_reference_3d(
            _execution(
                backend="reference",
                opening=rt.LeafOnlyOpening(),
                reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
            )
        )
        numba = rt.aggregate_frontier_reduce_numba_3d(
            _execution(
                backend="numba",
                opening=rt.LeafOnlyOpening(),
                reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
            )
        )

        self.assertEqual("numba", numba["backend"])
        self.assertEqual("reference", numba["metadata"]["parity_oracle_backend"])
        _assert_rows_close(self, reference["rows"], numba["rows"])

    @unittest.skipUnless(rt.aggregate_frontier_reduce_numba_available(), "Numba is required for parity execution")
    def test_numba_size_distance_inverse_square_matches_cpu_reference(self) -> None:
        reference = rt.aggregate_frontier_reduce_reference_3d(
            _execution(
                backend="reference",
                opening=rt.SizeDistanceOpening(max_ratio=0.5),
                reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
            )
        )
        numba = rt.run_aggregate_frontier_reduce_numba_3d(
            _execution(
                backend="numba",
                opening=rt.SizeDistanceOpening(max_ratio=0.5),
                reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
            )
        )

        _assert_rows_close(self, reference["rows"], numba["rows"])

    def test_numba_vector_reducer_and_overflow_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not support reducer"):
            rt.aggregate_frontier_reduce_numba_3d(
                _execution(
                    backend="numba",
                    opening=rt.SizeDistanceOpening(max_ratio=0.5),
                    reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_VECTOR_SUM,
                )
            )

        with self.assertRaisesRegex(ValueError, "max_output_rows would overflow"):
            rt.aggregate_frontier_reduce_numba_3d(
                _execution(
                    backend="numba",
                    opening=rt.LeafOnlyOpening(),
                    reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
                    max_output_rows=2,
                )
            )

    def test_public_module_still_has_no_app_identity_or_native_backend_claim(self) -> None:
        source = (REPO_ROOT / "src" / "rtdsl" / "aggregate_hierarchy.py").read_text(encoding="utf-8")
        for forbidden in (
            "BarnesHut",
            "Treelogy",
            "RTBH",
            "author-optix-payload",
            "load_inline",
            "import torch",
            "rtdl_optix",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
