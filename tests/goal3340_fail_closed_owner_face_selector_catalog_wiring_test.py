import unittest

from rtdsl.primitive_hierarchy import iter_primitive_hierarchy_nodes


def _node(node_id: str):
    for node in iter_primitive_hierarchy_nodes():
        if node.id == node_id:
            return node
    return None


class Goal3340FailClosedOwnerFaceSelectorCatalogWiringTest(unittest.TestCase):
    def test_catalog_preserves_fail_closed_selector_discovery_terms(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertTrue(node.reference_path.startswith("docs/reports/goal33"))
        self.assertIn(
            "derive owner face only when incident topology has a unique maximum",
            node.intent_phrases,
        )
        self.assertTrue(
            "fail-closed incident-face selector" in node.summary
            or "explicit-priority tie-break helper" in node.summary
        )

    def test_candidate_status_is_not_promoted(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertEqual(node.status, "candidate_behavior")
        self.assertEqual(node.layer, "candidate_experimental")


if __name__ == "__main__":
    unittest.main()
