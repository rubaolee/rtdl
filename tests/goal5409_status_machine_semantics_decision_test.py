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
    / "xhd_goal5409_status_machine_semantics_decision.json"
)
REPORT = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5409_xhd_status_machine_semantics_or_fail_closed_decision_2026-07-10.md"
)
CFR = (
    ROOT
    / "history"
    / "internal_docs"
    / "call_for_review_goal5409_xhd_status_machine_semantics_or_fail_closed_decision_2026-07-10.md"
)


class Goal5409StatusMachineSemanticsDecisionTest(unittest.TestCase):
    def _payload(self) -> dict:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_decision_authorizes_generic_probe_not_lb_support(self) -> None:
        payload = self._payload()
        self.assertEqual(
            "rtdl.paper_reproduction.xhd.goal5409.status_machine_semantics_decision.v1",
            payload["schema"],
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(
            "branch_a_one_more_generic_semantic_probe",
            payload["decision"]["branch"],
        )
        self.assertEqual(
            "Goal5410_generic_statused_large_cell_deferral_stream_probe",
            payload["decision"]["authorized_next_goal"],
        )
        self.assertFalse(payload["decision"]["explicit_lb_support_authorized"])
        self.assertFalse(payload["decision"]["direct_native_fix_authorized"])
        self.assertFalse(payload["claim_boundary"]["explicit_lb_support_claimed"])

    def test_generic_candidate_is_app_neutral_and_statused(self) -> None:
        payload = self._payload()
        candidate = payload["generic_semantic_candidate"]
        self.assertEqual("statused_large_cell_deferral_stream", candidate["name"])
        self.assertEqual("none", candidate["app_semantics"])
        description = candidate["description"]
        self.assertIn("active query id", description)
        self.assertIn("cell id", description)
        self.assertIn("payload status machine", description)
        why_generic = "\n".join(candidate["why_generic"])
        self.assertIn("X-HD", why_generic)
        self.assertIn("synthetic app-neutral fixtures", why_generic)

    def test_evidence_keeps_5407_5408_boundaries(self) -> None:
        payload = self._payload()
        self.assertEqual(
            "author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap",
            payload["evidence_inputs"]["goal5407_membership_probe"]["classification"],
        )
        self.assertFalse(
            payload["evidence_inputs"]["goal5408_namespace_reconciliation"][
                "compact_original_namespace_remap_explains_author_samples"
            ]
        )
        self.assertFalse(
            payload["evidence_inputs"]["goal5406_rtdl_full_cover"]["row_count_parity"]
        )
        self.assertFalse(
            payload["evidence_inputs"]["goal5406_rtdl_full_cover"]["row_hash_parity"]
        )

    def test_goal5410_gates_require_synthetic_bounded_full_and_fail_closed(self) -> None:
        payload = self._payload()
        gate_names = {gate["gate"] for gate in payload["goal5410_required_gates"]}
        self.assertEqual(
            {
                "synthetic_app_neutral_status_stream",
                "bounded_xhd_author_sample_row_gate",
                "full_goal5387_row_identity_gate",
                "fail_closed_exit",
            },
            gate_names,
        )
        for gate in payload["goal5410_required_gates"]:
            self.assertTrue(gate["required"])

    def test_forbidden_shortcuts_and_claim_boundary_are_explicit(self) -> None:
        payload = self._payload()
        forbidden = "\n".join(payload["forbidden_shortcuts"])
        self.assertIn("hard-code 6 rows per active", forbidden)
        self.assertIn("hard-code 62 rows per active", forbidden)
        self.assertIn("hard-code author sample source/cell pairs", forbidden)
        self.assertIn("add X-HD option names", forbidden)
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["figure7_reproduction_claimed"])
        self.assertFalse(boundary["figure11_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])

    def test_docs_explain_full_cover_is_not_author_raw_stream(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        cfr = CFR.read_text(encoding="utf-8")
        self.assertIn("statused_large_cell_deferral_stream", report)
        self.assertIn("RTDL full-cover", report)
        self.assertIn("author raw offload stream", report)
        self.assertIn("Goal5410_generic_statused_large_cell_deferral_stream_probe", report)
        self.assertIn("block_goal5409_and_fail_close_explicit_lb", cfr)


if __name__ == "__main__":
    unittest.main()
