from __future__ import annotations

from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import rtdsl as rt


def _prepared_hierarchy():
    hierarchy = rt.aggregate_hierarchy_3d(
        point_x=[0.0, 1.0, 2.0],
        point_y=[0.0, 0.0, 0.0],
        point_z=[0.0, 1.0, 2.0],
        point_weight=[1.0, 2.0, 3.0],
        node_cx=[1.0, 0.0, 1.5],
        node_cy=[0.0, 0.0, 0.0],
        node_cz=[1.0, 0.0, 1.5],
        node_half_size=[2.0, 0.5, 0.5],
        node_weight=[6.0, 1.0, 5.0],
        member_offsets=[0, 0, 1, 3],
        member_indices=[0, 1, 2],
        child_offsets=[0, 2, 2, 2],
        child_indices=[1, 2],
        source_leaf_node_index=[1, 2, 2],
        node_subtree_end_index=[3, 2, 3],
    )
    return rt.prepare_aggregate_hierarchy_3d(hierarchy)


class Goal5070NonForceGenericityProofTest(unittest.TestCase):
    def test_leaf_only_opening_public_contract_is_exported(self) -> None:
        for name in (
            "LeafOnlyOpening",
            "AGGREGATE_HIERARCHY_3D_OPENING_LEAF_ONLY",
            "AGGREGATE_HIERARCHY_3D_SUPPORTED_OPENINGS",
        ):
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__, name)

        metadata = rt.LeafOnlyOpening().to_metadata()
        self.assertEqual("leaf_only_opening", metadata["policy"])
        self.assertFalse(metadata["app_specific_policy_allowed"])
        self.assertFalse(metadata["uses_distance"])
        self.assertFalse(metadata["uses_node_size"])

    def test_contract_lists_two_distinct_opening_policies(self) -> None:
        contract = rt.describe_aggregate_hierarchy_3d_contract()

        self.assertIn("size_distance_opening", contract["opening_policies"])
        self.assertIn("leaf_only_opening", contract["opening_policies"])
        self.assertGreaterEqual(len(contract["opening_policies"]), 2)

    def test_non_force_reducer_with_leaf_only_opening_uses_same_execution_contract(self) -> None:
        spec = rt.aggregate_frontier_reduce_spec_3d(
            _prepared_hierarchy(),
            opening=rt.LeafOnlyOpening(),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )
        execution = rt.aggregate_frontier_reduce_execution_contract_3d(spec, backend="numba")
        metadata = execution.to_metadata()

        self.assertEqual("aggregate_count", metadata["spec"]["reducer"])
        self.assertEqual("leaf_only_opening", metadata["spec"]["opening"]["policy"])
        self.assertNotEqual("size_distance_opening", metadata["spec"]["opening"]["policy"])
        self.assertNotIn("inverse_square", metadata["spec"]["reducer"])
        self.assertEqual(rt.AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT, metadata["contract_version"])
        self.assertEqual("optional_numba_cpu_reference_prototype", metadata["backend_status"])
        self.assertTrue(metadata["backend_execution_authorized"])
        self.assertTrue(metadata["numba_execution_authorized"])
        self.assertFalse(metadata["native_backend_symbols_authorized"])

    def test_unsupported_opening_object_fails_closed(self) -> None:
        class AppOpening:
            def to_metadata(self):
                return {"policy": "app_opening"}

        with self.assertRaisesRegex(ValueError, "supported aggregate hierarchy opening"):
            rt.aggregate_frontier_reduce_spec_3d(
                _prepared_hierarchy(),
                opening=AppOpening(),
                reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
            )

    def test_public_module_still_has_no_app_identity(self) -> None:
        source = (REPO_ROOT / "src" / "rtdsl" / "aggregate_hierarchy.py").read_text(encoding="utf-8")
        for forbidden in ("BarnesHut", "Treelogy", "RTBH", "author-optix-payload", "load_inline", "import torch"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
