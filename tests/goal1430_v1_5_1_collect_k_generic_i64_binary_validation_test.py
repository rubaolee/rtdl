from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
STATUS = (
    "source_symbols_present_python_adapter_routed_embree_optix_adapter_parity_ok_"
    "binary_validation_ok_generic_abi_parity_ok_stable_review_pending"
)


class Goal1430V151CollectKGenericI64BinaryValidationTest(unittest.TestCase):
    def test_contract_records_binary_validation_but_keeps_stable_blocked(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(
            contract["status"],
            STATUS,
        )
        self.assertTrue(contract["native_source_symbols_present"])
        self.assertTrue(contract["native_binary_validation_present"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertEqual(contract["required_adapter_work"], ())
        self.assertEqual(
            contract["built_symbol_validation_evidence"],
            (
                "docs/reports/goal1430_v1_5_1_collect_k_generic_i64_binary_validation_2026-05-06.md",
            ),
        )
        self.assertEqual(
            contract["generic_abi_parity_evidence"],
            (
                "docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.md",
                "docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.md",
            ),
        )

    def test_binary_validation_report_records_both_backend_symbols(self) -> None:
        report = (
            ROOT
            / "docs/reports/goal1430_v1_5_1_collect_k_generic_i64_binary_validation_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("rtdl_embree_collect_k_bounded_i64", report)
        self.assertIn("rtdl_optix_collect_k_bounded_i64", report)
        self.assertIn("217bd991a1a6cefdd581e4faf43d80192c7dae94", report)
        self.assertIn('"emitted": 2', report)
        self.assertIn('"overflow": 1', report)
        self.assertIn("rows\": [1, 10, 2, 20]", report)
        self.assertIn("does not authorize stable primitive promotion", report)
        self.assertIn("No performance, zero-copy, whole-app", report)

    def test_rebuild_optix_artifact_is_reviewable_text(self) -> None:
        build = (
            ROOT
            / "docs/reports/goal1430_v1_5_1_collect_k_rebuild_optix_2026-05-06.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("build/librtdl_optix.so", build)
        self.assertIn("src/native/rtdl_optix.cpp", build)
        self.assertIn("nvcc", build)

    def test_consensus_records_gemini_accept_and_claude_unavailable(self) -> None:
        consensus = (
            ROOT
            / "docs/reports/two_ai_goal1430_v1_5_1_collect_k_generic_i64_binary_validation_consensus_2026-05-06.md"
        ).read_text(encoding="utf-8")
        claude = (
            ROOT
            / "docs/reports/claude_goal1430_v1_5_1_collect_k_generic_i64_binary_validation_unavailable_2026-05-06.md"
        ).read_text(encoding="utf-8")
        gemini = (
            ROOT
            / "docs/reports/gemini_goal1430_v1_5_1_collect_k_generic_i64_binary_validation_review_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("2-AI Consensus", consensus)
        self.assertIn("Gemini review", consensus)
        self.assertIn("Claude was attempted but unavailable", consensus)
        self.assertIn("ACCEPT", gemini)
        self.assertIn("No Claude acceptance is claimed", claude)


if __name__ == "__main__":
    unittest.main()
