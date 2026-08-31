from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl import v2_8_fixed_radius_graph_component_front_door as front_door


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4162_predicate_border_assignment_policy_metadata_2026-06-09.md"


class Goal4162PredicateBorderAssignmentPolicyMetadataTest(unittest.TestCase):
    def test_public_prepared_runner_exposes_policy_parameter(self) -> None:
        signature = inspect.signature(
            rt.run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d
        )
        self.assertIn("border_assignment_policy", signature.parameters)
        self.assertEqual(
            signature.parameters["border_assignment_policy"].default,
            "lowest_predicate_true_point_id_within_radius",
        )

    def test_internal_helper_validates_and_reports_policy(self) -> None:
        source = Path(front_door.__file__).read_text(encoding="utf-8")
        for fragment in (
            "border_assignment_policy: str = \"lowest_predicate_true_point_id_within_radius\"",
            "raise ValueError(\"border_assignment_policy must be 'lowest_predicate_true_point_id_within_radius'\")",
            "\"border_assignment_policy\": border_assignment_policy",
            "\"border_assignment_policy\": \"not_needed_all_predicate_true\"",
            "\"deterministic_neighbor_candidate_policy\": \"lowest_predicate_true_point_id_within_radius\"",
        ):
            self.assertIn(fragment, source)

    def test_report_states_behavior_unchanged_and_route_not_promoted(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted metadata hardening; behavior unchanged",
            "`border_assignment_policy=\"lowest_predicate_true_point_id_within_radius\"`",
            "Unsupported values fail closed",
            "does not solve the Goal4159 road sparse gap",
            "does not promote the route",
            "without hidden dispatch or app-specific engine logic",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
