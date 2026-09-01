"""Hostile regression tests for the post-Goal5836 internal audit."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import unittest

from scripts import audit_goal5835_goal5836 as audit


class Goal5835Goal5836StrictAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = audit.verify_stored()

    @staticmethod
    def _reseal(document: dict) -> dict:
        document["strict_audit_authority_sha256"] = audit._seal(document)
        return document

    def test_01_stored_authority_rebuilds_exactly(self) -> None:
        self.assertEqual(self.authority, audit.build_authority())
        self.assertEqual(self.authority, audit.verify_stored())
        self.assertEqual(
            self.authority["strict_audit_authority_sha256"],
            audit._seal(self.authority),
        )

    def test_02_frozen_goal5835_result_and_recount_are_identical(self) -> None:
        identities = self.authority["historical_inputs"]
        self.assertEqual(
            identities["goal5835_result"]["sha256"],
            identities["goal5835_recount"]["sha256"],
        )
        self.assertTrue(
            self.authority["verification"][
                "goal5835_result_equals_recount_bytes"
            ]
        )

    def test_03_goal5835_semantics_regenerate_ignoring_only_paths(self) -> None:
        verification = self.authority["verification"]
        self.assertTrue(
            verification[
                "goal5835_semantic_regeneration_equal_ignoring_absolute_paths"
            ]
        )
        self.assertFalse(
            verification["goal5835_whole_document_regeneration_equal"]
        )
        self.assertIn(
            "P2-G5835-PATH-DEPENDENT-RECEIPT",
            {row["id"] for row in self.authority["findings"]},
        )

    def test_04_goal5835_is_projection_not_executed_paper_app(self) -> None:
        goal = self.authority["goal5835"]
        self.assertEqual(
            goal["strict_classification"],
            "BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE",
        )
        self.assertFalse(goal["executed_paper_app"])
        self.assertFalse(
            goal["receipt_source_directly_calls_execute_registered_problem"]
        )
        self.assertFalse(
            goal["receipt_source_directly_calls_trajectory_to_swept_segments"]
        )
        self.assertFalse(
            goal["receipt_source_directly_calls_deduplicate_triangle_edges"]
        )
        self.assertTrue(goal["fixture_loader_calls_deduplicate_triangle_edges"])
        self.assertEqual(
            goal["fixture_loader_deduplication_scope"],
            "NEGATIVE_FACE_INTERIOR_BOUNDARY_RECONSTRUCTION_ONLY",
        )
        self.assertEqual(goal["new_goal5835_gpu_launch_count"], 0)
        self.assertEqual(goal["inherited_b3_true_optix_launch_count"], 33)

    def test_05_no_positive_complete_mesh_fixture_exists(self) -> None:
        goal = self.authority["goal5835"]
        self.assertEqual(goal["complete_mesh_rows"], ["face_interior_only_boundary"])
        self.assertEqual(goal["positive_complete_mesh_rows"], [])

    def test_06_fixture_sphere_identity_is_synthetic(self) -> None:
        goal = self.authority["goal5835"]
        self.assertTrue(goal["piecewise_connected"])
        self.assertEqual(goal["piecewise_sphere_ids"], [0, 1])

    def test_07_duplicate_triangle_id_breaks_direction_invariance(self) -> None:
        probe = self.authority["goal5835"][
            "duplicate_triangle_direction_probe"
        ]
        self.assertFalse(probe["duplicate_triangle_ids_rejected"])
        self.assertFalse(probe["input_order_invariant"])
        self.assertNotEqual(
            probe["forward_shared_direction"],
            probe["reverse_shared_direction"],
        )

    def test_08_app_adapter_accepts_inconsistent_generic_output(self) -> None:
        probe = self.authority["goal5835"]["malformed_output_probe"]
        self.assertFalse(probe["malformed_output_rejected"])
        self.assertNotEqual(probe["edge_count"], probe["bit_count"])
        self.assertNotEqual(probe["reported_collision"], probe["computed_or"])

    def test_09_non_integral_ids_are_currently_accepted(self) -> None:
        probe = self.authority["goal5835"]["permissive_id_probe"]
        self.assertTrue(probe["accepted"])
        self.assertEqual(probe["sphere_id"], 1.5)
        self.assertEqual(probe["path_segment_id"], 2.5)

    def test_10_goal5836_terminal_negative_outcome_is_preserved(self) -> None:
        goal = self.authority["goal5836"]
        self.assertEqual(goal["a1_classification"], "MATERIAL_PREDICATE_DIFFERENCE")
        self.assertTrue(goal["terminal_refusal_confirmed"])
        self.assertTrue(goal["transaction_complete"])
        self.assertFalse(goal["paper_app_promotion_succeeded"])
        self.assertEqual(goal["author_or_rtdl_goal5836_execution_count"], 0)
        self.assertEqual(goal["performance_timing_count"], 0)

    def test_11_review_is_internal_and_external_review_is_deferred(self) -> None:
        review = self.authority["review_state"]
        self.assertEqual(review["review_type"], "INTERNAL_HOSTILE_SELF_AUDIT")
        self.assertFalse(review["external_review_requested"])
        self.assertEqual(review["external_review_count"], 0)
        self.assertEqual(
            review["external_review_status"],
            "DEFERRED_BY_OWNER_UNTIL_RETURN_FROM_TRAVEL",
        )
        self.assertFalse(review["consensus_claimed"])
        self.assertFalse(
            self.authority["next_action"]["pod_required_for_this_audit"]
        )

    def test_12_cgo_manuscript_does_not_use_goals_as_experiment(self) -> None:
        impact = self.authority["cgo_manuscript_impact"]
        self.assertFalse(impact["goal5835_literal_present"])
        self.assertFalse(impact["goal5836_literal_present"])
        self.assertTrue(impact["sui_is_used_as_related_work_problem_inventory"])
        self.assertFalse(
            impact["negative_goal5836_result_should_be_added_as_experiment"]
        )
        self.assertEqual(len(impact["audited_file"]["sha256"]), 64)

    def test_13_finding_denominator_and_severities_are_exact(self) -> None:
        findings = self.authority["findings"]
        self.assertEqual({row["id"] for row in findings}, audit.EXPECTED_FINDINGS)
        counts = {
            severity: sum(row["severity"] == severity for row in findings)
            for severity in ("P0", "P1", "P2", "P3")
        }
        self.assertEqual(counts, {"P0": 0, "P1": 1, "P2": 6, "P3": 1})

    def test_14_historical_identity_paths_are_relative(self) -> None:
        for row in self.authority["historical_inputs"].values():
            path = PurePosixPath(row["path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)

    def test_15_coordinated_reseal_cannot_hide_claim_scope_finding(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["findings"] = [
            row for row in changed["findings"]
            if row["id"] != "P1-G5835-CLAIM-SCOPE"
        ]
        self._reseal(changed)
        with self.assertRaisesRegex(audit.StrictAuditError, "FINDING_SET_MISMATCH"):
            audit.validate_policy(changed)

    def test_16_coordinated_reseal_cannot_promote_goal5835(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["goal5835"]["executed_paper_app"] = True
        changed["claim_boundary"]["goal5835_may_be_called_paper_reproduction"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(
            audit.StrictAuditError, "GOAL5835_COUNTEREVIDENCE_MISMATCH"
        ):
            audit.validate_policy(changed)

    def test_17_coordinated_reseal_cannot_reopen_goal5836(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["goal5836"]["terminal_refusal_confirmed"] = False
        changed["goal5836"]["paper_app_promotion_succeeded"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(
            audit.StrictAuditError, "GOAL5836_VERDICT_MISMATCH"
        ):
            audit.validate_policy(changed)

    def test_18_coordinated_reseal_cannot_fabricate_external_review(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["review_state"]["external_review_requested"] = True
        changed["review_state"]["external_review_count"] = 1
        changed["review_state"]["consensus_claimed"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(audit.StrictAuditError, "REVIEW_STATE_MISMATCH"):
            audit.validate_policy(changed)

    def test_19_new_output_round_trips_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "authority"
            written = audit.write_authority(output)
            self.assertEqual(written, audit.verify_stored(output))

    def test_20_capsule_manifest_carries_current_audit_policy(self) -> None:
        manifest = json.loads(
            (audit.ROOT / "CAPSULE_MANIFEST.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            manifest["status"],
            "GOAL5836_COMPLETE__POST_A1_STRICT_AUDIT_CLAIM_NARROWED",
        )
        self.assertEqual(
            manifest["goal5835_strict_classification"],
            "BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE",
        )
        self.assertEqual(
            manifest["strict_audit_review_type"],
            "INTERNAL_HOSTILE_SELF_AUDIT",
        )
        self.assertEqual(manifest["external_review_count"], 0)
        self.assertFalse(manifest["consensus_claimed"])
        self.assertFalse(manifest["a2_reachable"])
        authority_path = (
            audit.ROOT
            / "history/internal_docs/goal5835_goal5836_strict_audit_20260901"
            / "STRICT_AUDIT_AUTHORITY.json"
        )
        authority_bytes = authority_path.read_bytes()
        authority = json.loads(authority_bytes)
        self.assertEqual(
            manifest["strict_audit_authority_sha256"],
            hashlib.sha256(authority_bytes).hexdigest(),
        )
        self.assertEqual(
            manifest["strict_audit_internal_seal"],
            authority["strict_audit_authority_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
