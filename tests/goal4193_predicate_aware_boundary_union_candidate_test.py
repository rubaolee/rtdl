import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4193_predicate_aware_boundary_union_candidate_primitive_2026-06-09.md"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
FUTURE_TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal4193PredicateAwareBoundaryUnionCandidateTest(unittest.TestCase):
    def test_candidate_node_is_discoverable_and_not_promoted(self) -> None:
        node = rt.find_primitive_hierarchy_node("continuation.predicate_aware_boundary_union")

        self.assertEqual(node.layer, "continuation")
        self.assertEqual(node.status, "candidate_behavior")
        self.assertIn("boundary_assignment_summary", node.outputs)
        self.assertIn("continuation.fixed_radius_graph", node.depends_on)
        self.assertIn("intent:components", node.capability_tags)
        self.assertIn("shape:fixed_radius", node.capability_tags)
        self.assertIn("output:columns", node.capability_tags)
        self.assertIn("continuation.fixed_radius_graph", node.considered_alternatives)
        self.assertIn("not an app-specific clustering or DBSCAN primitive", node.distinct_from)

    def test_discovery_finds_boundary_assignment_without_app_terms(self) -> None:
        matches = rt.find_primitive(text="predicate aware boundary union fixed radius components")
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].node_id, "continuation.predicate_aware_boundary_union")
        self.assertIn("alias:predicate_aware_boundary_union", matches[0].matched_on)

    def test_strict_hierarchy_validation_accepts_candidate_metadata(self) -> None:
        validation = rt.validate_primitive_hierarchy(require_discovery_metadata=True)
        self.assertTrue(validation["valid"], validation)
        self.assertEqual(validation["discovery_metadata_missing"], ())
        self.assertEqual(validation["promotion_metadata_missing"], ())

    def test_catalog_and_report_record_boundary(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        future = FUTURE_TODO.read_text(encoding="utf-8")

        self.assertIn("continuation.predicate_aware_boundary_union", catalog)
        self.assertIn("Candidate continuation for fixed-radius component grouping", catalog)
        self.assertIn("candidate_behavior", catalog)
        self.assertIn("Goal4190 showed", report)
        self.assertIn("must not encode DBSCAN", report)
        self.assertIn("does not implement the primitive", report)
        self.assertIn("Goal4190 tested the lighter counts-only mixed-predicate route", future)


if __name__ == "__main__":
    unittest.main()
