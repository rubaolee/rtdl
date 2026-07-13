from __future__ import annotations

from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import rtdsl as rt


def _rope_distinguishing_hierarchy(*, confuse_rope_with_next: bool = False) -> rt.AggregateHierarchy3D:
    """Synthetic non-paper fixture where accepted aggregate traversal must use rope.

    Node 1 is an internal aggregate that is accepted for sources 0 and 1.  Its
    next continuation points to its child node 2, while its rope continuation
    points to sibling node 3.  A reducer output mismatch under the alternate
    continuation columns proves this fixture distinguishes rope from next.
    """

    node_next_index = [1, 2, 3, -1]
    node_rope_index = [-1, 2 if confuse_rope_with_next else 3, 3, -1]
    return rt.aggregate_hierarchy_3d(
        point_x=[0.0, 0.1, 10.0],
        point_y=[0.0, 0.0, 0.0],
        point_z=[0.0, 0.0, 0.0],
        point_weight=[1.0, 1.0, 1.0],
        node_cx=[0.0, 10.0, 0.0, 10.0],
        node_cy=[0.0, 0.0, 0.0, 0.0],
        node_cz=[0.0, 0.0, 0.0, 0.0],
        node_half_size=[100.0, 1.0, 0.1, 0.1],
        node_weight=[3.0, 2.0, 2.0, 1.0],
        member_offsets=[0, 0, 0, 2, 3],
        member_indices=[0, 1, 2],
        child_offsets=[0, 2, 3, 3, 3],
        child_indices=[1, 3, 2],
        node_next_index=node_next_index,
        node_rope_index=node_rope_index,
        source_leaf_node_index=[2, 2, 3],
        node_subtree_end_index=[4, 3, 3, 4],
    )


def _execution(hierarchy: rt.AggregateHierarchy3D, backend: str):
    spec = rt.aggregate_frontier_reduce_spec_3d(
        rt.prepare_aggregate_hierarchy_3d(hierarchy),
        opening=rt.ContinuationPayloadOpening(max_ratio=1.0),
        reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    )
    return rt.aggregate_frontier_reduce_execution_contract_3d(spec, backend=backend)


def _projection(result: dict) -> tuple[tuple[int, float, int, int, int], ...]:
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


class Goal5082ContinuationPayloadRopeBranchTest(unittest.TestCase):
    def test_reference_executor_uses_rope_after_accepted_aggregate(self) -> None:
        hierarchy = _rope_distinguishing_hierarchy()
        self.assertEqual(2, hierarchy.node_next_index[1])
        self.assertEqual(3, hierarchy.node_rope_index[1])

        result = rt.run_aggregate_frontier_reduce_reference_3d(_execution(hierarchy, "reference"))

        self.assertEqual(
            (
                (0, 2.0, 3, 1, 1),
                (1, 2.0, 3, 1, 1),
                (2, 2.0, 4, 0, 2),
            ),
            _projection(result),
        )
        self.assertEqual("continuation_payload_opening", result["metadata"]["opening_policy"]["policy"])
        self.assertEqual("aggregate_count", result["metadata"]["reducer"])

    def test_fixture_would_change_if_rope_were_confused_with_next(self) -> None:
        correct = rt.run_aggregate_frontier_reduce_reference_3d(
            _execution(_rope_distinguishing_hierarchy(), "reference")
        )
        confused = rt.run_aggregate_frontier_reduce_reference_3d(
            _execution(_rope_distinguishing_hierarchy(confuse_rope_with_next=True), "reference")
        )

        self.assertNotEqual(_projection(correct), _projection(confused))
        self.assertEqual((0, 2.0, 3, 1, 1), _projection(correct)[0])
        self.assertNotEqual((0, 2.0, 3, 1, 1), _projection(confused)[0])

    @unittest.skipUnless(rt.aggregate_frontier_reduce_numba_available(), "Numba not available")
    def test_numba_executor_matches_rope_branch_reference(self) -> None:
        hierarchy = _rope_distinguishing_hierarchy()
        reference = rt.run_aggregate_frontier_reduce_reference_3d(_execution(hierarchy, "reference"))
        numba_result = rt.run_aggregate_frontier_reduce_numba_3d(_execution(hierarchy, "numba"))

        self.assertEqual(_projection(reference), _projection(numba_result))

    def test_rope_fixture_has_no_paper_app_identity(self) -> None:
        source = Path(__file__).read_text(encoding="utf-8")
        for forbidden in (
            "Barnes" + "Hut",
            "Tree" + "logy",
            "RT" + "BH",
            "author" + "-optix-payload",
            "next" + "PrimId",
            "auto" + "RopePrimId",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
