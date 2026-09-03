from __future__ import annotations

import json
import unittest

from scripts import goal5840_build_independent_refinement_preregistration as prereg


class Goal5840IndependentRefinementPreregistrationTest(unittest.TestCase):
    def test_stored_authority_rebuilds_byte_identically(self) -> None:
        expected = prereg.build_authority()
        stored = json.loads(prereg.OUTPUT_PATH.read_text(encoding="ascii"))
        prereg.validate_authority(stored)
        self.assertEqual(prereg._serialized(stored), prereg._serialized(expected))

    def test_every_route_has_every_property_mutation(self) -> None:
        authority = prereg.build_authority()
        pairs = {
            (row["route_id"], row["property_id"])
            for row in authority["mutation_matrix"]
        }
        expected = {
            (route["route_id"], property_id)
            for route in prereg.ROUTES
            for property_id in prereg.PROPERTIES
        }
        self.assertEqual(pairs, expected)
        self.assertTrue(all(
            row["target_selector"] and row["replacement"]
            for row in authority["mutation_matrix"]
        ))

    def test_route_specific_mutation_targets_are_frozen(self) -> None:
        authority = prereg.build_authority()
        targets = {
            row["mutation_id"]: row["target_selector"]
            for row in authority["mutation_matrix"]
        }
        self.assertEqual(len(targets), 15)
        self.assertIn(
            "family_schema.channels[relation_item_id].semantic",
            targets.values(),
        )
        self.assertIn(
            "family_schema.physical.sbt.record_count_relation",
            targets.values(),
        )

    def test_extractor_cannot_trust_existing_projection(self) -> None:
        extractor = prereg.build_authority()["independent_extractor"]
        self.assertFalse(extractor["imports_rtdsl"])
        self.assertFalse(extractor["imports_existing_compiler_projection_builder"])
        self.assertFalse(extractor["reads_stored_compiler_projection_as_target_facts"])

    def test_preregistration_authorizes_no_result_claim(self) -> None:
        boundary = prereg.build_authority()["claim_boundary"]
        self.assertTrue(boundary["preregistration_only"])
        self.assertFalse(boundary["lowering_preservation_established"])
        self.assertFalse(boundary["cgo_claim_authorized"])
        self.assertFalse(boundary["external_review_or_consensus"])

    def test_goal5838_core_remains_the_frozen_baseline(self) -> None:
        for path in (
            "src/rtdsl/v4_family_schema.py",
            "src/rtdsl/v4_generic_family_lifecycle.py",
            "src/rtdsl/v4_family.py",
        ):
            self.assertIn(path, prereg.BASELINE_FILES)

    def test_mutable_baseline_is_revision_bound_not_future_tree_bound(self) -> None:
        baseline = prereg.build_authority()["baseline"]
        self.assertEqual(baseline["commit"], prereg.BASELINE_COMMIT)
        self.assertIn("later working-tree files", baseline["identity_rule"])


if __name__ == "__main__":
    unittest.main()
