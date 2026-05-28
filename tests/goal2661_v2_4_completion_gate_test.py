from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal2661V24CompletionGateTest(unittest.TestCase):
    def test_completion_gate_closes_internal_v2_4_without_release_claims(self):
        gate = rt.v2_4_completion_gate()
        validation = rt.validate_v2_4_completion_gate(gate)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(gate["status"], "internal_v2_4_complete_no_public_release_tag")
        self.assertTrue(gate["internal_milestone_complete"])
        self.assertFalse(gate["public_release_tag_authorized"])
        self.assertFalse(gate["package_install_claim_authorized"])
        self.assertFalse(gate["public_speedup_claim_authorized"])
        self.assertEqual(gate["next_partner_milestone"], "v2_5_triton_first_with_numba_fallback")

    def test_completion_gate_requires_all_roadmap_deliverables(self):
        gate = rt.v2_4_completion_gate()
        deliverables = set(gate["required_deliverables"])

        self.assertEqual(len(deliverables), len(rt.V2_4_REQUIRED_COMPLETION_DELIVERABLES))
        self.assertIn("typed_buffer_protocol", deliverables)
        self.assertIn("prepared_session_protocol", deliverables)
        self.assertIn("segmented_chunked_row_streaming_protocol", deliverables)
        self.assertIn("benchmark_protocol_integration", deliverables)
        self.assertIn("machine_readable_phase_timing", deliverables)
        self.assertIn("native_vocabulary_boundary_gate", deliverables)

    def test_completion_gate_preserves_benchmark_basis_for_v2_5(self):
        gate = rt.v2_4_completion_gate()

        self.assertTrue(gate["same_contract_benchmark_basis_retained"])
        self.assertEqual(gate["benchmark_app_count"], 10)
        self.assertEqual(gate["primary_comparison_row_count"], 11)
        self.assertEqual(gate["benchmark_basis_hardware"], "NVIDIA RTX A5000 pod evidence")
        self.assertIn("Hausdorff / X-HD-style", gate["low_margin_rows"])
        self.assertIn("Barnes-Hut / RT-BarnesHut-style", gate["low_margin_rows"])
        self.assertIn("Robot collision", gate["low_margin_rows"])

    def test_completion_gate_blocks_native_app_vocabulary_pressure(self):
        gate = rt.v2_4_completion_gate()

        self.assertEqual(gate["native_engine_boundary"], "app_agnostic_native_engine")
        self.assertFalse(gate["app_specific_native_vocab_allowed"])
        self.assertEqual(gate["v2_5_preconditions"], rt.V2_4_V2_5_PRECONDITIONS)
        self.assertIn(
            "reject app-domain vocabulary in native primitive symbols",
            gate["v2_5_preconditions"],
        )
        self.assertIn(
            "label slower convenience paths as optional, compatibility, learner/preview, or rejected",
            gate["v2_5_preconditions"],
        )
        self.assertIn(
            "explicitly classify every non-piloted v2.5 benchmark app",
            gate["v2_5_preconditions"],
        )

    def test_partner_protocol_validation_locks_counts_and_tolerance_ratios(self):
        validation = rt.validate_v2_4_partner_protocol_contract()
        basis = rt.V2_4_BENCHMARK_PERFORMANCE_BASIS

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(len(basis), rt.V2_4_PRIMARY_COMPARISON_ROW_COUNT)
        self.assertEqual(len({row.app for row in basis}), rt.V2_4_PRIMARY_BENCHMARK_APP_COUNT)
        self.assertEqual(
            rt.v2_4_partner_protocol_contract().promoted_path_tolerance_ratio,
            0.10,
        )
        self.assertEqual(
            rt.v2_4_partner_protocol_contract().opt_in_tolerance_ratio,
            0.20,
        )

    def test_completion_evidence_reports_exist(self):
        gate = rt.v2_4_completion_gate()
        missing = [
            report
            for report in gate["evidence_reports"]
            if not (ROOT / report).exists()
        ]

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
