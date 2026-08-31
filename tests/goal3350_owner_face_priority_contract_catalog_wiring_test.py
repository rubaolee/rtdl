from pathlib import Path
import unittest

from rtdsl.primitive_hierarchy import find_primitive_hierarchy_node


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal3350_owner_face_priority_contract_catalog_wiring_2026-06-04.md"
NODE_ID = "candidate.closed_shape_topology_membership_count_2d"
CONTRACT_REPORT = "docs/reports/goal3349_owner_face_priority_pipeline_contract_2026-06-04.md"


class Goal3350OwnerFacePriorityContractCatalogWiringTest(unittest.TestCase):
    def test_hierarchy_points_to_formal_contract(self):
        node = find_primitive_hierarchy_node(NODE_ID)
        self.assertEqual(node.reference_path, CONTRACT_REPORT)
        self.assertEqual(node.status, "candidate_behavior")
        self.assertEqual(node.layer, "candidate_experimental")
        self.assertIn("formal priority pipeline contract", node.summary)
        self.assertIn("find the explicit priority owner face pipeline contract", node.intent_phrases)

    def test_generated_catalog_points_to_formal_contract(self):
        text = CATALOG.read_text(encoding="utf-8")
        self.assertIn(f"| `{NODE_ID}` |", text)
        self.assertIn(CONTRACT_REPORT, text)
        self.assertIn("formal priority pipeline contract", text)

    def test_report_records_non_promotion_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not a promotion", text)
        self.assertIn(CONTRACT_REPORT, text)
        self.assertIn("candidate_behavior", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
