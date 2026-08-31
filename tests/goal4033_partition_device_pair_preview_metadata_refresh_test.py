from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4033_partition_device_pair_preview_metadata_refresh_2026-06-08.md"


class Goal4033PartitionDevicePairPreviewMetadataRefreshTest(unittest.TestCase):
    def test_metadata_records_device_bounded_pair_preview(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        goals = description["candidate_strategy_evidence_goals"]["partition_convergence_hybrid"]
        self.assertIn("Goal4032", goals)
        requirements = description["candidate_strategy_requirements"]["partition_convergence_hybrid"]
        self.assertIn("cupy_device_bounded_pair_enumeration_same_contract_pod_execution", requirements)
        guidance = description["candidate_strategy_partition_guidance"]["partition_convergence_hybrid"]
        self.assertEqual(
            guidance["executable_preview"],
            "cupy_device_bounded_pair_preview_and_numba_device_column_preview_pass_same_contract_but_are_not_final_fast_native_producers",
        )

    def test_plan_still_blocks_promotion_and_claims(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.055,
            component_threshold=12,
            backend="optix",
            partner="cupy",
            strategy="partition_convergence_hybrid",
        )
        self.assertEqual(plan["status"], "candidate_requires_native_implementation")
        self.assertFalse(plan["runtime_executable"])
        self.assertFalse(plan["native_abi_added"])
        self.assertFalse(plan["automatic_partner_selection_allowed"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4032",
            "device_bounded_offsets",
            "not a promoted performance route",
            "candidate_requires_native_implementation",
            "does not authorize speedup",
            "automatic-partner-selection",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()

