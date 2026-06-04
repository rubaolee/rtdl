import unittest

from rtdsl.primitive_hierarchy import iter_primitive_hierarchy_nodes


def _node(node_id: str):
    for node in iter_primitive_hierarchy_nodes():
        if node.id == node_id:
            return node
    return None


class Goal3340FailClosedOwnerFaceSelectorCatalogWiringTest(unittest.TestCase):
    def test_catalog_points_to_fail_closed_selector_report(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertEqual(
            node.reference_path,
            "docs/reports/goal3339_fail_closed_incident_owner_face_selector_2026-06-04.md",
        )
        self.assertIn(
            "derive owner face only when incident topology has a unique maximum",
            node.intent_phrases,
        )
        self.assertIn("fail-closed incident-face selector", node.summary)

    def test_candidate_status_is_not_promoted(self):
        node = _node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertEqual(node.status, "candidate_behavior")
        self.assertEqual(node.layer, "candidate_experimental")


if __name__ == "__main__":
    unittest.main()
