from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
STATUS = (
    "source_symbols_present_python_adapter_routed_embree_optix_adapter_parity_ok_"
    "binary_validation_ok_generic_abi_parity_ok_production_wrapper_generic_symbol_route_ok_"
    "stable_review_pending"
)


class Goal1431V151CollectKGenericI64AbiParityTest(unittest.TestCase):
    def test_contract_records_generic_abi_parity_but_keeps_stable_blocked(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(contract["status"], STATUS)
        self.assertTrue(contract["native_binary_validation_present"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertEqual(
            contract["generic_abi_parity_evidence"],
            (
                "docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.md",
                "docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.md",
            ),
        )
        self.assertIn("formal generic ABI parity checks", contract["claim_boundary"])
        self.assertIn("production wrappers now route native candidate rows", contract["claim_boundary"])
        self.assertIn("does not authorize speedup", contract["claim_boundary"])
        self.assertIn("stable primitive wording", contract["claim_boundary"])

    def test_summary_report_records_scope_and_boundary(self) -> None:
        summary = (
            ROOT
            / "docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPTED for the measured generic i64 ABI parity package", summary)
        self.assertIn("Embree: ACCEPTED", summary)
        self.assertIn("OptiX: ACCEPTED", summary)
        self.assertIn("rtdl_embree_collect_k_bounded_i64", summary)
        self.assertIn("rtdl_optix_collect_k_bounded_i64", summary)
        self.assertIn("610e81a776079803e95030d661d28cc6bd995aa5", summary)
        self.assertIn("does not authorize stable primitive promotion", summary)
        self.assertIn("Stable `COLLECT_K_BOUNDED` primitive wording remains blocked", summary)

    def test_backend_artifacts_record_accepted_same_abi_cases(self) -> None:
        expected = {
            "embree": "docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.md",
            "optix": "docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.md",
        }

        for backend, relative_path in expected.items():
            report = (ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(backend=backend):
                self.assertIn("ACCEPTED.", report)
                self.assertIn(f"rtdl_{backend}_collect_k_bounded_i64", report)
                self.assertIn("Git HEAD: 610e81a776079803e95030d661d28cc6bd995aa5", report)
                self.assertIn("deduplicate_and_canonicalize_exact_fit: pass", report)
                self.assertIn("fail_closed_overflow_no_partial_rows: pass", report)
                self.assertIn("Failures: none", report)
                self.assertIn("not stable primitive promotion", report)
                self.assertIn("not speedup wording", report)

    def test_external_review_and_consensus_keep_boundary_narrow(self) -> None:
        gemini = (
            ROOT
            / "docs/reports/gemini_goal1431_v1_5_1_collect_k_generic_i64_abi_parity_review_2026-05-06.md"
        ).read_text(encoding="utf-8")
        claude = (
            ROOT
            / "docs/reports/claude_goal1431_v1_5_1_collect_k_generic_i64_abi_parity_unavailable_2026-05-06.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs/reports/two_ai_goal1431_v1_5_1_collect_k_generic_i64_abi_parity_consensus_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPT", gemini)
        self.assertIn("No Claude acceptance is claimed", claude)
        self.assertIn("2-AI Consensus", consensus)
        self.assertIn("Gemini external review: accepted", consensus)
        self.assertIn("Claude external review: attempted but unavailable", consensus)
        self.assertIn("not a stable primitive promotion", consensus)
        self.assertIn("Stable `COLLECT_K_BOUNDED` promotion remains blocked", consensus)


if __name__ == "__main__":
    unittest.main()
