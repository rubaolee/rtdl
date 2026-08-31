from __future__ import annotations

from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import rtdsl as rt


def _linearized_cluster_hierarchy() -> rt.AggregateHierarchy3D:
    """A non-paper synthetic hierarchy using continuation columns.

    The fixture represents three weighted samples in two leaf clusters.  The
    public continuation columns define a linear walk over the root and leaves;
    no paper app, author dump, force-law, or prepared-state adapter is involved.
    """

    return rt.aggregate_hierarchy_3d(
        point_x=[0.0, 1.0, 10.0],
        point_y=[0.0, 0.0, 0.0],
        point_z=[0.0, 0.0, 0.0],
        point_weight=[1.0, 1.0, 1.0],
        node_cx=[5.0, 0.5, 10.0],
        node_cy=[0.0, 0.0, 0.0],
        node_cz=[0.0, 0.0, 0.0],
        node_half_size=[100.0, 0.1, 0.1],
        node_weight=[3.0, 2.0, 1.0],
        member_offsets=[0, 0, 2, 3],
        member_indices=[0, 1, 2],
        child_offsets=[0, 2, 2, 2],
        child_indices=[1, 2],
        node_next_index=[1, 2, -1],
        node_rope_index=[-1, 2, -1],
        source_leaf_node_index=[1, 1, 2],
        node_subtree_end_index=[3, 2, 3],
    )


def _continuation_count_execution(backend: str):
    prepared = rt.prepare_aggregate_hierarchy_3d(_linearized_cluster_hierarchy())
    spec = rt.aggregate_frontier_reduce_spec_3d(
        prepared,
        opening=rt.ContinuationPayloadOpening(max_ratio=0.5),
        reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    )
    return rt.aggregate_frontier_reduce_execution_contract_3d(spec, backend=backend)


def _row_projection(result: dict) -> tuple[tuple[int, float, int, int, int], ...]:
    return tuple(
        (
            int(row["source_id"]),
            float(row["reducer_value_0"]),
            int(row["visited_node_count"]),
            int(row["aggregate_contribution_count"]),
            int(row["exact_contribution_count"]),
        )
        for row in result["rows"]
    )


class Goal5081ContinuationPayloadGenericityProofTest(unittest.TestCase):
    def test_non_force_continuation_payload_reference_consumer(self) -> None:
        execution = _continuation_count_execution("reference")
        result = rt.run_aggregate_frontier_reduce_reference_3d(execution)

        self.assertEqual("reference", result["backend"])
        self.assertEqual("continuation_payload_opening", result["metadata"]["opening_policy"]["policy"])
        self.assertEqual("aggregate_count", result["metadata"]["reducer"])
        self.assertEqual((0,), result["metadata"]["root_nodes"])
        self.assertFalse(result["metadata"]["paper_reproduction_claim_authorized"])
        self.assertEqual(
            (
                (0, 2.0, 3, 0, 2),
                (1, 2.0, 3, 0, 2),
                (2, 2.0, 3, 0, 2),
            ),
            _row_projection(result),
        )

    @unittest.skipUnless(rt.aggregate_frontier_reduce_numba_available(), "Numba not available")
    def test_non_force_continuation_payload_numba_matches_reference(self) -> None:
        reference = rt.run_aggregate_frontier_reduce_reference_3d(
            _continuation_count_execution("reference")
        )
        numba_result = rt.run_aggregate_frontier_reduce_numba_3d(
            _continuation_count_execution("numba")
        )

        self.assertEqual("numba", numba_result["backend"])
        self.assertEqual(_row_projection(reference), _row_projection(numba_result))
        self.assertEqual(
            "continuation_payload_opening",
            numba_result["metadata"]["opening_policy"]["policy"],
        )
        self.assertEqual("aggregate_count", numba_result["metadata"]["reducer"])

    def test_continuation_payload_requires_public_continuation_columns(self) -> None:
        hierarchy = rt.aggregate_hierarchy_3d(
            point_x=[0.0],
            point_y=[0.0],
            point_z=[0.0],
            point_weight=[1.0],
            node_cx=[0.0],
            node_cy=[0.0],
            node_cz=[0.0],
            node_half_size=[1.0],
            node_weight=[1.0],
            member_offsets=[0, 1],
            member_indices=[0],
            child_offsets=[0, 0],
            child_indices=[],
            source_leaf_node_index=[0],
            node_subtree_end_index=[1],
        )
        spec = rt.aggregate_frontier_reduce_spec_3d(
            rt.prepare_aggregate_hierarchy_3d(hierarchy),
            opening=rt.ContinuationPayloadOpening(max_ratio=0.5),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )
        execution = rt.aggregate_frontier_reduce_execution_contract_3d(spec, backend="reference")

        with self.assertRaisesRegex(ValueError, "node_next_index and node_rope_index"):
            rt.run_aggregate_frontier_reduce_reference_3d(execution)

    def test_fixture_and_core_text_do_not_depend_on_paper_app_identity(self) -> None:
        source = (REPO_ROOT / "src" / "rtdsl" / "aggregate_hierarchy.py").read_text(encoding="utf-8")
        test_source = Path(__file__).read_text(encoding="utf-8")
        forbidden_tokens = (
            "Barnes" + "Hut",
            "Tree" + "logy",
            "RT" + "BH",
            "author" + "-optix-payload",
            "next" + "PrimId",
            "auto" + "RopePrimId",
        )
        for forbidden in forbidden_tokens:
            self.assertNotIn(forbidden, source)
            self.assertNotIn(forbidden, test_source)


if __name__ == "__main__":
    unittest.main()
