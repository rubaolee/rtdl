import unittest

from rtdsl.primitive_hierarchy import iter_primitive_hierarchy_nodes


def _find_node(node_id: str):
    for node in iter_primitive_hierarchy_nodes():
        if node.id == node_id:
            return node
    return None


class Goal3332OwnerFaceContractPrimitiveCatalogWiringTest(unittest.TestCase):
    def test_closed_shape_topology_candidate_points_to_owner_face_reference(self):
        node = _find_node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertTrue(node.reference_path.startswith("docs/reports/goal33"))
        self.assertTrue(
            "owner_face" in node.reference_path
            or "owner-face" in node.reference_path
            or "incident_owner_face" in node.reference_path
        )
        self.assertIn("owner_face_id", node.outputs)
        self.assertIn("filter closed shape candidates by caller supplied owner face ids", node.intent_phrases)
        self.assertIn("caller-supplied owner-face", node.boundary)
        self.assertIn("RayJoin assignment interpretation", node.boundary)

    def test_candidate_remains_claim_bounded_and_not_promoted(self):
        node = _find_node("candidate.closed_shape_topology_membership_count_2d")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertEqual(node.status, "candidate_behavior")
        self.assertEqual(node.layer, "candidate_experimental")
        self.assertIn("planned_optix", node.backends)


if __name__ == "__main__":
    unittest.main()
