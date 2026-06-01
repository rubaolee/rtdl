from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2891_runtime_provenance_index_in_conformance_snapshot_2026-05-31.md"


class Goal2891RuntimeProvenanceIndexInConformanceSnapshotTest(unittest.TestCase):
    def test_partner_conformance_snapshot_indexes_runtime_provenance(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        snapshot = packet["partner_conformance_snapshot"]

        self.assertEqual("accept", validation["status"])
        self.assertEqual(1, snapshot["runtime_provenance_record_count"])
        record = snapshot["runtime_provenance_records"][0]
        self.assertEqual("bounded_triton_torch_carrier_typed_payload_gather", record["path"])
        self.assertEqual("triton", record["partner"])
        self.assertEqual("torch", record["carrier"])
        self.assertEqual("pod_runtime_copy_decision_seam_wrapped", record["status"])
        self.assertEqual("Goal2889", record["evidence_goal"])
        self.assertTrue(record["goal2883_same_pointer_evidence_indexed"])
        self.assertTrue(record["goal2889_copy_decision_seam_wrap_indexed"])
        self.assertTrue(record["goal2889_executed_conversion_seam_lease_indexed"])

    def test_runtime_provenance_does_not_authorize_release_claims(self) -> None:
        snapshot = rt.v2_5_internal_readiness_packet(repo_root=ROOT)["partner_conformance_snapshot"]
        record = snapshot["runtime_provenance_records"][0]

        for field in (
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "triton_preview_auto_selection_authorized",
            "release_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(record[field])
        self.assertFalse(snapshot["release_conformance_complete"])
        self.assertIn("does not authorize release", snapshot["claim_boundary"])

    def test_readiness_indexes_goal2891_report(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2891_runtime_provenance_index_in_conformance_snapshot_2026-05-31.md"

        self.assertTrue(packet["required_report_presence"][path])
        self.assertIn("keep_goal2891_runtime_provenance_snapshot_green", packet["allowed_next_actions"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2891",
            "runtime_provenance_records",
            "bounded_triton_torch_carrier_typed_payload_gather",
            "goal2883_same_pointer_evidence_indexed",
            "goal2889_copy_decision_seam_wrap_indexed",
            "not a v2.5 release authorization",
            "not true-zero-copy wording",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
