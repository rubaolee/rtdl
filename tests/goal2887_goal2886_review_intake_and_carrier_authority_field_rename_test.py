from pathlib import Path
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/rtdsl/hit_stream_handoff.py"
REPORT = ROOT / "docs/reports/goal2887_goal2886_review_intake_and_carrier_authority_field_rename_2026-05-31.md"
TRACE_REPORT = ROOT / "docs/reports/goal2883_torch_carrier_runtime_seam_trace_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2886_claude_review_runtime_trace_and_conformance_snapshot_2026-05-31.md"


class Goal2887Goal2886ReviewIntakeAndCarrierAuthorityFieldRenameTest(unittest.TestCase):
    def test_review_is_indexed_by_readiness_packet(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        review_path = str(REVIEW.relative_to(ROOT)).replace("\\", "/")

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["external_review_presence"][review_path])
        self.assertEqual((), packet["missing_external_reviews"])
        self.assertIn("triage_goal2886_claude_review_before_any_release_packet", packet["allowed_next_actions"])

    def test_ambiguous_carrier_originated_field_is_removed_from_live_trace(self) -> None:
        trace = rt.trace_v2_5_hit_stream_torch_carrier_runtime_seam_authority(
            _device_hit_columns(),
            _device_payload_columns(),
        )
        source = SOURCE.read_text(encoding="utf-8")
        trace_report = TRACE_REPORT.read_text(encoding="utf-8")

        self.assertNotIn("carrier_originated_transfer_copy_lifetime", source)
        self.assertNotIn("carrier_originated_transfer_copy_lifetime: false", trace_report)
        self.assertTrue(trace["carrier_authority_disallowed_by_contract"])
        for record in trace["lease_records"]:
            self.assertTrue(record["carrier_authority_disallowed_by_contract"])

    def test_observed_runtime_facts_remain_separate_from_contract_invariant(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")

        for phrase in (
            "same_pointer_evidence_observed",
            "adapter_execution_proven_on_hardware",
            "event_log",
            "carrier_authority_disallowed_by_contract",
        ):
            self.assertIn(phrase, source)

    def test_review_caveat_and_report_boundary_are_preserved(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("hardcoded literal", review)
        self.assertIn("Goal2886", report)
        self.assertIn("carrier_authority_disallowed_by_contract: true", report)
        self.assertIn("not a v2.5 release authorization", report)
        self.assertIn("not true-zero-copy wording", report)

    def test_readiness_indexes_goal2887_report(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2887_goal2886_review_intake_and_carrier_authority_field_rename_2026-05-31.md"

        self.assertTrue(packet["required_report_presence"][path])
        self.assertIn("keep_goal2887_carrier_authority_field_rename_green", packet["allowed_next_actions"])


if __name__ == "__main__":
    unittest.main()
