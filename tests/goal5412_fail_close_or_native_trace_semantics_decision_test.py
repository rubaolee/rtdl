from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5412_fail_close_or_native_trace_semantics_decision.json"
)
REPORT = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5412_xhd_fail_close_or_native_trace_semantics_decision_2026-07-10.md"
)
CALL_FOR_REVIEW = (
    ROOT
    / "history"
    / "internal_docs"
    / "call_for_review_goal5412_xhd_fail_close_or_native_trace_semantics_decision_2026-07-10.md"
)


class Goal5412FailCloseOrNativeTraceDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.call_for_review = CALL_FOR_REVIEW.read_text(encoding="utf-8")

    def test_current_bridge_is_fail_closed_and_not_lb_support(self) -> None:
        decision = self.payload["decision"]
        self.assertFalse(decision["explicit_lb_support_authorized"])
        self.assertTrue(decision["explicit_lb_current_model_fail_closed"])
        self.assertEqual("fail_close_current_explicit_lb", decision["recommended_current_branch"])
        self.assertFalse(decision["full_goal5387_row_identity_gate_authorized"])
        self.assertFalse(decision["direct_native_fix_authorized"])
        self.assertFalse(self.payload["claim_boundary"]["explicit_lb_support_claimed"])

    def test_new_trace_semantic_is_design_only(self) -> None:
        decision = self.payload["decision"]
        trace = self.payload["authorized_generic_design"]
        self.assertTrue(decision["new_generic_native_trace_semantics_design_authorized"])
        self.assertFalse(decision["new_generic_native_trace_implementation_authorized"])
        self.assertTrue(trace["design_only"])
        self.assertEqual("none", trace["app_semantics"])
        self.assertIn("non-XHD", trace["continuation_condition"])
        self.assertIn("payload_event_ordinal", trace["required_row_schema"])
        self.assertIn("cell_namespace_code", trace["required_row_schema"])
        self.assertIn("synthetic non-X-HD fixture", self.report)
        self.assertIn("narrow", self.report)
        self.assertIn("exception", self.report)

    def test_forbidden_shortcuts_are_explicit(self) -> None:
        forbidden = "\n".join(self.payload["forbidden_shortcuts"]).lower()
        self.assertIn("6 rows per active", forbidden)
        self.assertIn("62 rows per active", forbidden)
        self.assertIn("sample source/cell pairs", forbidden)
        self.assertIn("xhd", forbidden)
        self.assertIn("paper", forbidden)
        self.assertIn("figure", forbidden)
        self.assertIn("lb option", forbidden)

    def test_evidence_records_goal5411_no_go(self) -> None:
        goal5411 = self.payload["evidence_inputs"]["goal5411_bounded_statused_deferral"]
        self.assertFalse(goal5411["bounded_xhd_author_sample_row_gate_passed"])
        self.assertEqual([1554, 1554, 1554], goal5411["observed_statused_deferral_cells"])
        self.assertEqual([False, False, False], goal5411["author_sample_cells_recovered"])

    def test_claim_boundary_remains_closed_for_broad_claims(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertFalse(boundary["new_native_backend_implemented"])
        self.assertFalse(boundary["full_goal5387_row_identity_parity_claimed"])
        self.assertFalse(boundary["figure7_reproduction_claimed"])
        self.assertFalse(boundary["figure11_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])

    def test_call_for_review_requests_stop_or_design_review(self) -> None:
        self.assertIn("approve_fail_close_only_stop_trace_line", self.call_for_review)
        self.assertIn("approve_goal5412_fail_close_current_bridge", self.call_for_review)
        self.assertIn("design only", self.call_for_review)
        self.assertIn("It is not", self.call_for_review)


if __name__ == "__main__":
    unittest.main()
