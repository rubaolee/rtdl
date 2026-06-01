from pathlib import Path
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2883_torch_carrier_runtime_seam_trace_2026-05-31.md"


class Goal2883TorchCarrierRuntimeSeamTraceTest(unittest.TestCase):
    def test_runtime_trace_records_neutral_seam_lease_transitions(self) -> None:
        trace = rt.trace_v2_5_hit_stream_torch_carrier_runtime_seam_authority(
            _device_hit_columns(),
            _device_payload_columns(),
            executed=False,
        )

        self.assertEqual("accept", trace["status"])
        self.assertFalse(trace["executed"])
        self.assertEqual("triton_torch_carrier_gather_columns", trace["trace_scope"])
        self.assertEqual("triton_launch_carrier_only", trace["carrier_metadata_scope"])
        self.assertEqual("neutral_buffer_seam_only", trace["authoritative_metadata_origin"])
        self.assertEqual("neutral_buffer_seam", trace["authority_origin"])
        self.assertEqual(3, trace["lease_count"])
        self.assertTrue(trace["all_leases_completed"])
        self.assertTrue(trace["carrier_authority_disallowed_by_contract"])
        self.assertFalse(trace["true_zero_copy_authorized"])
        for record in trace["lease_records"]:
            self.assertEqual(("handoff_begin", "continuation_complete"), record["event_log"])
            self.assertEqual("neutral_buffer_seam", record["authority_origin"])
            self.assertTrue(record["carrier_authority_disallowed_by_contract"])

    def test_authority_validation_includes_runtime_trace_status(self) -> None:
        validation = rt.validate_v2_5_hit_stream_neutral_seam_authority(
            _device_hit_columns(),
            _device_payload_columns(),
        )

        self.assertEqual("accept", validation["status"])
        self.assertEqual("accept", validation["runtime_seam_authority_trace_status"])
        trace = validation["runtime_seam_authority_trace"]
        self.assertEqual(3, trace["lease_count"])
        self.assertEqual("neutral_buffer_seam", trace["authority_origin"])

    def test_torch_execution_path_records_runtime_trace_when_torch_is_available(self) -> None:
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

        self.assertEqual("triton_torch_tensor_carrier", metadata["selected_gather_partner"])
        self.assertEqual("accept", trace["status"])
        self.assertTrue(trace["executed"])
        self.assertEqual(3, trace["lease_count"])
        self.assertEqual([20, 10], inputs["group_ids"].detach().cpu().tolist())
        self.assertEqual([2.5, 1.5], inputs["values"].detach().cpu().tolist())

    def test_readiness_indexes_goal2883(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2883_torch_carrier_runtime_seam_trace_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])
        self.assertIn("keep_goal2883_runtime_seam_trace_green", packet["allowed_next_actions"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2883",
            "handoff_begin",
            "continuation_complete",
            "authority_origin: neutral_buffer_seam",
            "not a v2.5 release authorization",
            "not true-zero-copy wording",
            "Future promoted partner paths still need their own runtime traces",
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
