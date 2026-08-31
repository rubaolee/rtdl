from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.primitive_discovery import find_primitive


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3324_closed_shape_topology_membership_candidate_2026-06-04.md"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
NODE_ID = "candidate.closed_shape_topology_membership_count_2d"


class Goal3324ClosedShapeTopologyMembershipCandidateTest(unittest.TestCase):
    def test_candidate_node_is_discoverable_and_app_agnostic(self) -> None:
        node = rt.describe_primitive(NODE_ID)

        self.assertEqual(node["status"], "candidate_behavior")
        self.assertEqual(node["layer"], "candidate_experimental")
        self.assertIn("intent:membership", node["capability_tags"])
        self.assertIn("intent:count", node["capability_tags"])
        self.assertIn("shape:closed_shape", node["capability_tags"])
        self.assertIn("topology_aware_membership_count", node["aliases"])
        self.assertIn("rows.point_closed_shape_boundary_event_columns", node["depends_on"])
        self.assertIn("reduction.grouped", node["depends_on"])
        self.assertIn("RayJoin assignment interpretation", node["boundary"])
        self.assertNotIn("rayjoin", NODE_ID)

    def test_strict_metadata_and_duplicate_gate_pass_for_candidate(self) -> None:
        strict = rt.validate_primitive_hierarchy(require_discovery_metadata=True)
        self.assertTrue(strict["valid"], strict)

        duplicate_gate = rt.validate_primitive_hierarchy(
            enforce_promotion_metadata=True,
            promotion_candidate_ids=(NODE_ID,),
        )
        self.assertTrue(duplicate_gate["valid"], duplicate_gate)
        self.assertEqual(duplicate_gate["promotion_metadata_missing"], ())

    def test_discovery_finds_candidate_for_topology_membership_intent(self) -> None:
        matches = find_primitive(
            "topology aware closed shape membership count",
            intent="membership",
            shape="closed_shape",
            dim="2d",
            output="scalar",
            keying="by_query_id",
        )
        self.assertTrue(matches)
        self.assertEqual(matches[0].node_id, NODE_ID)

    def test_report_and_generated_catalog_record_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        catalog = CATALOG.read_text(encoding="utf-8")

        for text in (report, catalog):
            self.assertIn("Closed-Shape Topology-Aware Membership", text)
            self.assertIn("boundary ownership", text)
            self.assertIn("duplicate", text)

        self.assertIn(NODE_ID, catalog)
        self.assertIn("Candidate / Experimental Layer", catalog)
        self.assertIn("RayJoin, GIS, or benchmark-specific interpretation stays in Python app code", report)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized`: false", report)


if __name__ == "__main__":
    unittest.main()

