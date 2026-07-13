from __future__ import annotations

from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import rtdsl as rt


def _hierarchy_with_descriptors(**overrides):
    kwargs = dict(
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
        node_next_index=[-1, -1, -1],
        node_resume_index=[-1, -1, -1],
        node_rope_index=[-1, -1, -1],
        source_leaf_node_index=[1, 2, 2],
        node_subtree_end_index=[3, 2, 3],
    )
    kwargs.update(overrides)
    return rt.aggregate_hierarchy_3d(**kwargs)


class Goal5068AggregateHierarchyDescriptorExtensionTest(unittest.TestCase):
    def test_source_leaf_and_subtree_end_are_generic_descriptor_columns(self) -> None:
        hierarchy = _hierarchy_with_descriptors()
        metadata = hierarchy.to_metadata()
        contract = rt.describe_aggregate_hierarchy_3d_contract()

        self.assertEqual(("source_leaf_node_index", "node_subtree_end_index"), metadata["descriptor_columns"])
        self.assertEqual(("source_leaf_node_index", "node_subtree_end_index"), contract["descriptor_columns"])
        self.assertEqual((1, 2, 2), hierarchy.source_leaf_node_index)
        self.assertEqual((3, 2, 3), hierarchy.node_subtree_end_index)
        self.assertFalse(metadata["app_specific_schema_allowed"])
        self.assertFalse(metadata["backend_execution_authorized"])

    def test_source_leaf_descriptor_must_reference_leaf_containing_point(self) -> None:
        with self.assertRaisesRegex(ValueError, "must reference a leaf"):
            _hierarchy_with_descriptors(source_leaf_node_index=[0, 2, 2])
        with self.assertRaisesRegex(ValueError, "not a member"):
            _hierarchy_with_descriptors(source_leaf_node_index=[2, 2, 2])
        with self.assertRaisesRegex(ValueError, "length must match point_count"):
            _hierarchy_with_descriptors(source_leaf_node_index=[1, 2])

    def test_subtree_end_descriptor_must_contain_child_ranges(self) -> None:
        with self.assertRaisesRegex(ValueError, "node_index < end"):
            _hierarchy_with_descriptors(node_subtree_end_index=[0, 2, 3])
        with self.assertRaisesRegex(ValueError, "contained"):
            _hierarchy_with_descriptors(node_subtree_end_index=[2, 2, 3])
        with self.assertRaisesRegex(ValueError, "length must match node_count"):
            _hierarchy_with_descriptors(node_subtree_end_index=[3, 2])

    def test_descriptors_do_not_authorize_backend_execution(self) -> None:
        hierarchy = _hierarchy_with_descriptors()
        prepared = rt.prepare_aggregate_hierarchy_3d(hierarchy)
        spec = rt.aggregate_frontier_reduce_spec_3d(
            prepared,
            opening=rt.SizeDistanceOpening(max_ratio=0.5),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )

        self.assertFalse(prepared.to_metadata()["backend_execution_authorized"])
        self.assertFalse(spec.to_metadata()["backend_execution_authorized"])
        self.assertEqual("aggregate_count", spec.reducer)


if __name__ == "__main__":
    unittest.main()
