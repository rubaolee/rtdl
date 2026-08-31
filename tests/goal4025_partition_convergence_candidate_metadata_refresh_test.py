from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4025_partition_convergence_candidate_metadata_refresh_2026-06-08.md"


class Goal4025PartitionConvergenceCandidateMetadataRefreshTest(unittest.TestCase):
    def test_candidate_evidence_goals_include_current_validation_chain(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        goals = description["candidate_strategy_evidence_goals"]["partition_convergence_hybrid"]
        for goal in (
            "Goal4014",
            "Goal4016",
            "Goal4017",
            "Goal4019",
            "Goal4021",
            "Goal4023",
            "Goal4024",
        ):
            self.assertIn(goal, goals)

    def test_candidate_requirements_include_validation_and_status_gates(self) -> None:
        requirements = rt.V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS
        for requirement in (
            "typed_partition_summary_stream_contract",
            "same_contract_validator_against_python_reference",
            "component_label_oracle_against_all_pairs",
            "complete_candidate_coverage_status_invariant",
            "edge_case_status_and_float_tolerance_tests",
        ):
            self.assertIn(requirement, requirements)

    def test_guidance_names_native_promotion_gate(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.055,
            component_threshold=12,
            backend="optix",
            partner="numba",
            strategy="partition_convergence_hybrid",
        )
        guidance = plan["candidate_strategy_partition_guidance"]
        self.assertIn("required_validation_chain", guidance)
        self.assertEqual(
            guidance["native_promotion_gate"],
            "candidate_device_producer_must_pass_goal4019_goal4021_goal4023_goal4024_before_timing",
        )
        self.assertIn("incomplete_partition_pair_prefix_marked_complete", guidance["rejected_shortcuts"])
        self.assertFalse(plan["runtime_executable"])
        self.assertFalse(plan["native_abi_added"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_source_and_report_record_metadata_refresh(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4024",
            "required_validation_chain",
            "native_promotion_gate",
            "component_label_oracle_against_all_pairs",
            "does not make partition_convergence_hybrid executable",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
