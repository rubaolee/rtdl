from pathlib import Path
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2871_hit_stream_torch_carrier_seam_authority_guard_2026-05-31.md"
)


class Goal2871HitStreamTorchCarrierSeamAuthorityGuardTest(unittest.TestCase):
    def test_default_neutral_seam_authority_validation_accepts(self) -> None:
        validation = rt.validate_v2_5_hit_stream_neutral_seam_authority()

        self.assertEqual("accept", validation["status"])
        self.assertEqual("neutral_buffer_seam", validation["transfer_copy_lifetime_authority"])
        self.assertEqual((), validation["torch_carrier_forbidden_authority_field_hits"])
        self.assertEqual((), validation["neutral_seam_missing_authority_fields"])
        self.assertEqual("triton", validation["torch_carrier_allowed_only_for_partner"])
        self.assertFalse(validation["torch_is_neutral_protocol"])
        self.assertFalse(validation["true_zero_copy_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])

    def test_device_column_validation_keeps_torch_as_carrier_only(self) -> None:
        validation = rt.validate_v2_5_hit_stream_neutral_seam_authority(
            _device_hit_columns(),
            _device_payload_columns(),
        )
        adapter = rt.describe_v2_5_hit_stream_torch_carrier_adapter(
            _device_hit_columns(),
            _device_payload_columns(),
        )

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["torch_carrier_forbidden_authority_field_hits"])
        self.assertEqual(rt.GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS, validation["torch_carrier_forbidden_authority_fields"])
        self.assertTrue(adapter["raw_cuda_adapter_required"])
        self.assertTrue(adapter["torch_carrier_copy_diagnostics_are_advisory"])
        self.assertFalse(adapter["true_zero_copy_authorized"])

    def test_reconciliation_contract_names_the_authority_boundary(self) -> None:
        contract = rt.describe_v2_5_hit_stream_neutral_seam_reconciliation()

        self.assertTrue(contract["neutral_seam_authority_enforced"])
        self.assertEqual("neutral_buffer_seam", contract["transfer_copy_lifetime_authority"])
        self.assertEqual(
            rt.GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS,
            contract["torch_carrier_forbidden_authority_fields"],
        )
        self.assertTrue(contract["torch_carrier_copy_diagnostics_are_advisory"])
        self.assertIn("neutral buffer seam is the authority", contract["claim_boundary"])

    def test_readiness_packet_indexes_goal2871_report(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2871_hit_stream_torch_carrier_seam_authority_guard_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])

    def test_report_records_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2871",
            "neutral buffer seam",
            "torch carrier",
            "transfer/copy/lifetime",
            "not a v2.5 release authorization",
            "not true zero-copy",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
