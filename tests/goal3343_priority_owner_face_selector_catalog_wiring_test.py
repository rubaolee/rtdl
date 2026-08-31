import unittest

from rtdsl.primitive_hierarchy import iter_primitive_hierarchy_nodes


def _node(node_id: str):
    for node in iter_primitive_hierarchy_nodes():
        if node.id == node_id:
            return node
    return None


class Goal3343PriorityOwnerFaceSelectorCatalogWiringTest(unittest.TestCase):
    def test_catalog_preserves_priority_selector_discovery_terms(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertTrue(node.reference_path.startswith("docs/reports/goal33"))
        self.assertIn(
            "break incident topology ties only with caller supplied face priorities",
            node.intent_phrases,
        )
        self.assertTrue(
            "explicit-priority tie-break helper" in node.summary
            or "membership-filter pipeline" in node.summary
        )

    def test_candidate_remains_unpromoted(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertEqual(node.status, "candidate_behavior")
        self.assertEqual(node.layer, "candidate_experimental")


if __name__ == "__main__":
    unittest.main()
