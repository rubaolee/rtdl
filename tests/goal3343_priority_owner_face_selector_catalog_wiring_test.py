import unittest

from rtdsl.primitive_hierarchy import iter_primitive_hierarchy_nodes


def _node(node_id: str):
    for node in iter_primitive_hierarchy_nodes():
        if node.id == node_id:
            return node
    return None


class Goal3343PriorityOwnerFaceSelectorCatalogWiringTest(unittest.TestCase):
    def test_catalog_points_to_priority_selector_report(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertEqual(
            node.reference_path,
            "docs/reports/goal3342_priority_owner_face_selector_reference_2026-06-04.md",
        )
        self.assertIn(
            "break incident topology ties only with caller supplied face priorities",
            node.intent_phrases,
        )
        self.assertIn("explicit-priority tie-break helper", node.summary)

    def test_candidate_remains_unpromoted(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertEqual(node.status, "candidate_behavior")
        self.assertEqual(node.layer, "candidate_experimental")


if __name__ == "__main__":
    unittest.main()
