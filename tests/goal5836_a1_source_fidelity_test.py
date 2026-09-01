from __future__ import annotations

import copy
from pathlib import PurePosixPath
import unittest

from scripts import goal5836_a1_build_source_fidelity as a1


class Goal5836A1SourceFidelityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = a1.verify_stored()

    @staticmethod
    def _reseal(document: dict) -> dict:
        document["source_fidelity_authority_sha256"] = a1._seal(document)
        return document

    def test_01_stored_authority_rebuilds_exactly(self) -> None:
        self.assertEqual(self.authority, a1.verify_stored())
        self.assertEqual(
            self.authority["source_fidelity_authority_sha256"],
            a1._seal(self.authority),
        )

    def test_02_a1_only_is_authorized_and_consumed(self) -> None:
        authorization = self.authority["authorization"]
        self.assertEqual(
            {key for key, value in authorization.items() if value},
            {
                "a0_completed",
                "a1_owner_authorized",
                "a1_static_inspection_completed",
                "a1_authorization_consumed",
            },
        )

    def test_03_classification_is_the_preregistered_material_difference(self) -> None:
        self.assertEqual(
            self.authority["classification"],
            "MATERIAL_PREDICATE_DIFFERENCE",
        )
        self.assertEqual(self.authority["status"], a1.STATUS)

    def test_04_only_the_two_material_dimensions_trigger_refusal(self) -> None:
        material = {
            row["dimension"]
            for row in self.authority["semantic_classification"]
            if row["decision"] == "MATERIAL_PREDICATE_DIFFERENCE"
        }
        self.assertEqual(
            material,
            {
                "obstacle_edge_direction_contract",
                "inside_start_and_initial_overlap_coverage",
            },
        )

    def test_05_ordinary_linear_curve_semantics_are_not_falsely_rejected(self) -> None:
        decisions = {
            row["dimension"]: row["decision"]
            for row in self.authority["semantic_classification"]
        }
        self.assertEqual(
            decisions["piecewise_linear_swept_sphere_representation"],
            "MATCH",
        )
        self.assertEqual(
            decisions["constant_radius_width_and_linear_endcaps"],
            "MATCH",
        )
        self.assertEqual(
            decisions["face_interior_only_collision"],
            "MATCH_LIMITATION",
        )

    def test_06_author_benchmark_really_enables_directed_loop_edges(self) -> None:
        locators = {
            row["path"]: {anchor["label"] for anchor in row["anchors"]}
            for row in self.authority["author_source"]["locators"]
        }
        self.assertIn(
            "ccd_benchmark_enables_loop_edges",
            locators["RTCD/Benchmark/Curve/benchmark.cpp"],
        )
        self.assertIn(
            "loop_selects_directed_edges",
            locators["RTCD/CollisionScenes/obstacle.h"],
        )
        self.assertIn(
            "directed_edge_set",
            locators["RTCD/Meshes/mesh.h"],
        )

    def test_07_goal5835_arbitrary_direction_and_exclusion_are_bound(self) -> None:
        labels = {
            anchor["label"]
            for row in self.authority["goal5835_source"]["locators"]
            for anchor in row["anchors"]
        }
        self.assertIn("first_occurrence_fixes_arbitrary_direction", labels)
        self.assertIn("initial_overlap_is_excluded", labels)

    def test_08_author_sources_are_exact_git_bound_capsule_bytes(self) -> None:
        selected = self.authority["author_source"]["selected_files"]
        self.assertEqual([row["path"] for row in selected], list(a1.AUTHOR_FILES))
        for row in selected:
            self.assertEqual(len(row["sha256"]), 64)
            self.assertEqual(len(row["git_oid_sha1"]), 40)
            self.assertGreater(row["bytes"], 0)

    def test_09_every_identity_path_is_repository_relative(self) -> None:
        for row in self.authority["predecessors"]:
            path = PurePosixPath(row["path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)
        for row in self.authority["author_source"]["selected_files"]:
            path = PurePosixPath(row["path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)

    def test_10_no_build_execution_gpu_timing_or_external_review_occurred(self) -> None:
        observation = self.authority["a1_observation"]
        self.assertTrue(observation["author_source_semantics_inspected"])
        self.assertTrue(observation["source_fidelity_classification_made"])
        self.assertFalse(observation["author_program_output_inspected"])
        for field in (
            "author_build_count",
            "author_execution_count",
            "rtdl_goal5836_execution_count",
            "input_freeze_count",
            "route_materialization_count",
            "gpu_worker_count",
            "timing_count",
            "performance_result_count",
            "product_or_case_study_mutation_count",
            "external_review_count",
        ):
            self.assertEqual(observation[field], 0)

    def test_11_a1_negative_outcome_is_terminal_and_a2_is_unreachable(self) -> None:
        transition = self.authority["terminal_transition"]
        self.assertFalse(transition["a2_reachable"])
        self.assertFalse(transition["a3_reachable"])
        self.assertFalse(transition["a4_reachable"])
        self.assertFalse(transition["a5_reachable"])
        self.assertEqual(
            transition["next_owner_gate"],
            "NONE__A1_TERMINAL_NEGATIVE_OUTCOME",
        )

    def test_12_goal_transaction_completes_without_promotion(self) -> None:
        completion = self.authority["goal_completion"]
        self.assertTrue(completion["goal5836_transaction_complete"])
        self.assertFalse(completion["successful_promotion_path_complete"])
        self.assertEqual(
            completion["terminal_stage"],
            "A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION",
        )

    def test_13_claim_ceiling_remains_fail_closed(self) -> None:
        claim = self.authority["claim_boundary"]
        self.assertEqual(claim["paper_app_status"], "NOT_A_PAPER_APP")
        self.assertTrue(claim["goal5835_scope_preserved"])
        self.assertFalse(claim["paper_app_claimed"])
        self.assertFalse(claim["performance_claimed"])
        self.assertFalse(claim["complete_rtccd_claimed"])
        self.assertEqual(claim["generalization_exam_count"], 0)

    def test_14_coordinated_reseal_cannot_upgrade_to_match(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["classification"] = "MATCH_SELECTED_EDGE_PREDICATE"
        self._reseal(changed)
        with self.assertRaisesRegex(a1.A1Error, "CLASSIFICATION_OR_STATUS_MISMATCH"):
            a1.validate_policy(changed)

    def test_15_coordinated_reseal_cannot_authorize_a2(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["authorization"]["a2_input_freeze_authorized"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(a1.A1Error, "AUTHORIZATION_DOCUMENT_MISMATCH"):
            a1.validate_policy(changed)

    def test_16_coordinated_reseal_cannot_hide_a_material_row(self) -> None:
        changed = copy.deepcopy(self.authority)
        row = next(
            item
            for item in changed["semantic_classification"]
            if item["dimension"] == "inside_start_and_initial_overlap_coverage"
        )
        row["decision"] = "MATCH"
        self._reseal(changed)
        with self.assertRaisesRegex(a1.A1Error, "MATERIAL_DIFFERENCE_ROWS_MISMATCH"):
            a1.validate_policy(changed)

    def test_17_coordinated_reseal_cannot_reopen_a2(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["terminal_transition"]["a2_reachable"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(a1.A1Error, "TERMINAL_TRANSITION_MISMATCH"):
            a1.validate_policy(changed)

    def test_18_paper_locators_cover_method_limit_and_graph(self) -> None:
        locators = self.authority["paper_evidence"]["semantic_locators"]
        self.assertEqual([row["pdf_page"] for row in locators], [5, 7, 10])
        supports = {item for row in locators for item in row["supports"]}
        self.assertTrue(any("inside starts" in item for item in supports))
        self.assertTrue(any("not faces" in item for item in supports))


if __name__ == "__main__":
    unittest.main()
