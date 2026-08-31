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
    opening: rt.SizeDistanceOpening | rt.LeafOnlyOpening,
    reducer: str,
    backend: str = "reference",
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


class Goal5072AggregateFrontierReduceCpuReferenceTest(unittest.TestCase):
    def test_leaf_only_aggregate_count_reference_executor(self) -> None:
        execution = _execution(
            opening=rt.LeafOnlyOpening(),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )
        result = rt.aggregate_frontier_reduce_reference_3d(execution)

        self.assertEqual("reference", result["backend"])
        self.assertEqual("implemented_cpu_reference", result["backend_status"])
        self.assertEqual(3, result["row_count"])
        self.assertFalse(result["partial_result_returned"])

        rows = result["rows"]
        self.assertEqual(tuple(rt.AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA), tuple(rows[0].keys()))
        self.assertEqual([0, 1, 2], [row["source_id"] for row in rows])
        self.assertEqual([2.0, 2.0, 2.0], [row["reducer_value_0"] for row in rows])
        self.assertEqual([3, 3, 3], [row["visited_node_count"] for row in rows])
        self.assertEqual([0, 0, 0], [row["aggregate_contribution_count"] for row in rows])
        self.assertEqual([2, 2, 2], [row["exact_contribution_count"] for row in rows])
        self.assertTrue(all(row["status_code"] == 0 for row in rows))

    def test_size_distance_inverse_square_reference_matches_pairwise_scalar_sum(self) -> None:
        execution = _execution(
            opening=rt.SizeDistanceOpening(max_ratio=0.5),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
        )
        result = rt.run_aggregate_frontier_reduce_reference_3d(execution)

        expected = [
            2.0 / 4.0 + 3.0 / 9.0,
            2.0 * 1.0 / 4.0 + 2.0 * 3.0 / 13.0,
            3.0 * 1.0 / 9.0 + 3.0 * 2.0 / 13.0,
        ]
        for row, expected_value in zip(result["rows"], expected):
            self.assertTrue(math.isclose(row["reducer_value_0"], expected_value, rel_tol=1e-12))
            self.assertEqual(0.0, row["reducer_value_1"])
            self.assertEqual(0.0, row["reducer_value_2"])
            self.assertEqual(0, row["aggregate_contribution_count"])
            self.assertEqual(2, row["exact_contribution_count"])

    def test_reference_executor_rejects_non_reference_backend_and_vector_reducer(self) -> None:
        with self.assertRaisesRegex(ValueError, "backend='reference'"):
            rt.aggregate_frontier_reduce_reference_3d(
                _execution(
                    opening=rt.LeafOnlyOpening(),
                    reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
                    backend="numba",
                )
            )

        with self.assertRaisesRegex(ValueError, "does not support reducer"):
            rt.aggregate_frontier_reduce_reference_3d(
                _execution(
                    opening=rt.SizeDistanceOpening(max_ratio=0.5),
                    reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_VECTOR_SUM,
                )
            )

    def test_reference_executor_fails_closed_before_materializing_overflow(self) -> None:
        with self.assertRaisesRegex(ValueError, "max_output_rows would overflow"):
            rt.aggregate_frontier_reduce_reference_3d(
                _execution(
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
