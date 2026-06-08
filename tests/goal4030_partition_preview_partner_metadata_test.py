from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4030_partition_preview_partner_metadata_2026-06-08.md"


class Goal4030PartitionPreviewPartnerMetadataTest(unittest.TestCase):
    def test_candidate_metadata_records_both_partner_previews(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        goals = description["candidate_strategy_evidence_goals"]["partition_convergence_hybrid"]
        self.assertIn("Goal4027", goals)
        self.assertIn("Goal4029", goals)
        requirements = description["candidate_strategy_requirements"]["partition_convergence_hybrid"]
        self.assertIn("cupy_preview_producer_same_contract_pod_execution", requirements)
        self.assertIn("numba_preview_device_columns_same_contract_pod_execution", requirements)
        guidance = description["candidate_strategy_partition_guidance"]["partition_convergence_hybrid"]
        self.assertEqual(
            guidance["executable_preview"],
            "cupy_and_numba_partition_summary_previews_pass_same_contract_but_are_not_final_fast_native_producers",
        )

    def test_plan_still_blocks_promotion_and_claims(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.055,
            component_threshold=12,
            backend="optix",
            partner="numba",
            strategy="partition_convergence_hybrid",
        )
        self.assertEqual(plan["status"], "candidate_requires_native_implementation")
        self.assertFalse(plan["runtime_executable"])
        self.assertFalse(plan["native_abi_added"])
        self.assertFalse(plan["public_speedup_claim_authorized"])

    def test_source_and_report_record_partner_preview_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "numba_preview_device_columns_same_contract_pod_execution",
            "cupy_and_numba_partition_summary_previews_pass_same_contract",
            "not final fast native producers",
            "does not promote partition_convergence_hybrid",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
