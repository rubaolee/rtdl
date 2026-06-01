from pathlib import Path
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/rtdsl/hit_stream_handoff.py"
REPORT = ROOT / "docs/reports/goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md"


class Goal2889TorchCarrierCopyDecisionSeamLeaseWrapTest(unittest.TestCase):
    def test_static_trace_remains_attestation_not_executed_copy_wrap(self) -> None:
        trace = rt.trace_v2_5_hit_stream_torch_carrier_runtime_seam_authority(
            _device_hit_columns(),
            _device_payload_columns(),
            executed=False,
        )

        self.assertEqual("accept", trace["status"])
        self.assertFalse(trace["executed"])
        self.assertFalse(trace["copy_decision_wrapped_by_seam_lease"])
        for record in trace["lease_records"]:
            self.assertFalse(record["conversion_executed_under_seam_lease"])

    def test_source_wraps_torch_as_calls_with_neutral_seam_lease(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")

        self.assertIn("_torch_as_under_neutral_seam_lease", source)
        self.assertIn("lease.begin_partner_borrow()", source)
        self.assertIn("_torch_as(", source)
        self.assertIn("borrowed.complete_partner_borrow()", source)
        self.assertIn("copy_decision_wrapped_by_seam_lease", source)
        self.assertIn("conversion_executed_under_seam_lease", source)

    def test_executed_torch_path_records_wrapped_copy_decision_when_torch_is_available(self) -> None:
        torch = _try_import_torch()
        if torch is None:
            self.skipTest("torch runtime is not available in this environment")

        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=torch.tensor([0, 1], dtype=torch.int64),
            primitive_ids=torch.tensor([1, 0], dtype=torch.int64),
            backend="reference",
            native_device_column_output_proven_on_hardware=False,
        )
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            torch.tensor([10, 20], dtype=torch.int64),
            torch.tensor([1.5, 2.5], dtype=torch.float64),
            group_count=21,
        )

        inputs, metadata = rt.gather_typed_payload_columns_for_hit_stream(
            hit_columns,
            payload_columns,
            partner="triton",
        )
        trace = metadata["torch_carrier_execution"]["neutral_seam_runtime_authority_trace"]

        self.assertEqual("accept", trace["status"])
        self.assertTrue(trace["copy_decision_wrapped_by_seam_lease"])
        for record in trace["lease_records"]:
            self.assertTrue(record["conversion_executed_under_seam_lease"])
        self.assertEqual([20, 10], inputs["group_ids"].detach().cpu().tolist())
        self.assertEqual([2.5, 1.5], inputs["values"].detach().cpu().tolist())

    def test_readiness_indexes_goal2889_report(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])
        self.assertIn("keep_goal2889_copy_decision_seam_lease_wrap_green", packet["allowed_next_actions"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2889",
            "copy_decision_wrapped_by_seam_lease: true",
            "conversion_executed_under_seam_lease: true",
            "not a v2.5 release authorization",
            "not true-zero-copy wording",
            "Future promoted partner paths still need their own runtime seam-lease wrapping",
        ):
            self.assertIn(phrase, text)


def _try_import_torch():
    try:
        import torch
    except Exception:
        return None
    return torch


if __name__ == "__main__":
    unittest.main()
