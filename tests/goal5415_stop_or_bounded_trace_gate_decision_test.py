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
    / "xhd_goal5415_stop_or_bounded_trace_gate_decision.json"
)
GOAL5414 = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5414_synthetic_payload_transition_trace_fixture.json"
)


class Goal5415StopOrBoundedTraceGateDecisionTest(unittest.TestCase):
    def test_decision_stops_lb_and_does_not_authorize_bounded_gate(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["matched"])
        decision = payload["decision"]
        self.assertTrue(decision["stop_current_explicit_lb_line"])
        self.assertFalse(decision["attempt_bounded_xhd_payload_transition_sample_gate"])
        self.assertFalse(decision["bounded_xhd_sample_gate_authorized"])
        self.assertFalse(decision["native_payload_transition_backend_authorized"])
        self.assertFalse(decision["full_goal5387_row_identity_gate_authorized"])
        self.assertTrue(decision["return_to_full_reproduction_mainline"])

    def test_decision_is_supported_by_previous_evidence(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        basis = payload["decision_basis"]
        self.assertTrue(basis["goal5408_review_amendment_absorbed"])
        self.assertFalse(basis["goal5411_bounded_statused_sample_gate_passed"])
        self.assertTrue(basis["goal5412_fail_closed_current_model"])
        self.assertTrue(basis["goal5414_synthetic_non_app_trace_proof_passed"])
        self.assertTrue(basis["exact_dataset_blocker_still_primary"])

        goal5414 = json.loads(GOAL5414.read_text(encoding="utf-8"))
        self.assertTrue(goal5414["matched"])
        self.assertFalse(goal5414["claim_boundary"]["bounded_xhd_sample_row_recovery_claimed"])
        self.assertFalse(goal5414["claim_boundary"]["explicit_lb_support_claimed"])

    def test_claim_boundary_keeps_all_broad_claims_closed(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["decision_claimed"])
        self.assertTrue(boundary["synthetic_non_app_payload_transition_trace_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "bounded_xhd_sample_row_recovery_claimed",
            "native_backend_implementation_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(boundary[key], key)

    def test_next_mainline_returns_to_full_reproduction_blockers(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(payload["pod_expectation"]["pod_required_for_this_decision"])
        next_mainline = payload["next_mainline"]
        self.assertIn("exact paper input provenance", next_mainline["focus"])
        self.assertIn("figure-by-figure reproducibility status", next_mainline["focus"])
        self.assertIn("denominator-aligned performance plan", next_mainline["focus"])
        self.assertIn(
            "more -lb row-identity probing without exact dataset or new external review",
            next_mainline["forbidden_next_focus"],
        )


if __name__ == "__main__":
    unittest.main()
