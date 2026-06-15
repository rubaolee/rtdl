from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/rtdsl/v3_0_m14_hit_stream_full_window_transfer_audit.py"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
RUNNER = ROOT / "scripts/v3_0_m14_hit_stream_full_window_transfer_audit.py"
REPORT = ROOT / "docs/reports/goal4410_v3_0_m14_hit_stream_full_window_transfer_audit_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4410_v3_0_m14_hit_stream_full_window_transfer_audit_8192_2026-06-15.json"


class Goal4410V30M14HitStreamFullWindowTransferAuditTest(unittest.TestCase):
    def test_m14_module_defines_full_window_audit_contract(self) -> None:
        text = MODULE.read_text(encoding="utf-8")
        self.assertIn("V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_VERSION", text)
        self.assertIn("ray_triangle_hit_stream_full_window_transfer_audit", text)
        self.assertIn("classify_v3_m14_full_window_transfer_snapshot", text)
        self.assertIn("producer_consumer", text)
        self.assertIn("expected_query_ray_upload_bytes", text)
        self.assertIn("handoff_no_hidden_output_copy_ready", text)
        self.assertIn("full_window_true_zero_copy_ready", text)

    def test_runtime_supports_default_and_full_counter_scopes(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")
        method_start = text.index("def ray_triangle_hit_stream_same_stream_row_reduction_summary")
        method_end = text.index("def ray_triangle_hit_stream_event_ordered_row_reduction_summary", method_start)
        method = text[method_start:method_end]
        self.assertIn('transfer_counter_scope: str = "post_native_enqueue"', method)
        self.assertIn('"producer_consumer"', method)
        self.assertIn("transfer_counter_scope == \"producer_consumer\"", method)
        self.assertIn("transfer_counter_scope == \"post_native_enqueue\"", method)
        self.assertIn("native_producer_enqueue_to_same_stream_row_reduction_before_summary_materialization", method)
        self.assertIn('"transfer_counter_scope": transfer_counter_scope', method)

    def test_runner_preloads_counter_before_rtdsl_import(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("LD_PRELOAD", text)
        self.assertIn("os.execvpe", text)
        self.assertLess(text.index("_ensure_transfer_counter_preloaded"), text.index("import rtdsl as rt"))
        self.assertIn("run_v3_m14_hit_stream_full_window_transfer_audit_case", text)

    def test_classifier_accepts_expected_query_upload_plus_small_params(self) -> None:
        audit = rt.classify_v3_m14_full_window_transfer_snapshot(
            _snapshot(host_to_device_bytes=8 * rt.V3_M14_GPU_RAY3D_HOST_BYTES + 128),
            ray_count=8,
            min_named_output_column_bytes=8 * 16,
        )
        self.assertTrue(audit["producer_input_upload_observed"])
        self.assertTrue(audit["producer_input_upload_explained"])
        self.assertTrue(audit["handoff_no_hidden_output_copy_ready"])
        self.assertFalse(audit["full_window_true_zero_copy_ready"])
        self.assertEqual(128, audit["observed_host_to_device_excess_after_expected_query_upload_bytes"])

    def test_classifier_rejects_forbidden_transfer_direction(self) -> None:
        audit = rt.classify_v3_m14_full_window_transfer_snapshot(
            _snapshot(
                host_to_device_bytes=8 * rt.V3_M14_GPU_RAY3D_HOST_BYTES + 128,
                device_to_host_calls=1,
                device_to_host_bytes=8,
            ),
            ray_count=8,
            min_named_output_column_bytes=8 * 16,
        )
        self.assertFalse(audit["handoff_no_hidden_output_copy_ready"])
        self.assertIn("device_to_host_copy_observed", audit["disallowed_reasons"])
        with self.assertRaisesRegex(GraphValidationError, "forbidden transfer direction"):
            rt.validate_v3_m14_full_window_transfer_audit(audit)

    def test_validator_accepts_synthetic_m14_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m14_hit_stream_full_window_transfer_audit_payload(payload)
        self.assertTrue(validation["producer_input_upload_explained"])
        self.assertTrue(validation["handoff_no_hidden_output_copy_ready"])
        self.assertFalse(validation["full_window_true_zero_copy_ready"])
        self.assertFalse(validation["public_claim_authorized"])

    def test_validator_rejects_wrong_runtime_scope(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        metadata = dict(row["metadata"])
        evidence = dict(metadata["full_window_transfer_evidence"])
        evidence["transfer_counter_scope"] = "post_native_enqueue"
        metadata["full_window_transfer_evidence"] = evidence
        row["metadata"] = metadata
        payload["partner_rows"] = (row,)
        with self.assertRaisesRegex(GraphValidationError, "transfer counter scope"):
            rt.validate_v3_m14_hit_stream_full_window_transfer_audit_payload(payload)

    def test_pod_artifact_and_report_capture_full_window_audit(self) -> None:
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_v3_m14_hit_stream_full_window_transfer_audit_payload(payload)
        self.assertTrue(validation["producer_input_upload_observed"])
        self.assertTrue(validation["producer_input_upload_explained"])
        self.assertTrue(validation["handoff_no_hidden_output_copy_ready"])
        self.assertFalse(validation["full_window_true_zero_copy_ready"])

        row = payload["partner_rows"][0]
        self.assertEqual("cupy", row["partner"])
        self.assertEqual(8192, row["ray_count"])
        self.assertEqual([16384, 16384, 16384, 67100672, 8192, 0, 0, 1], row["validation_signature"])
        audit = row["transfer_audit"]
        self.assertEqual(262144, audit["expected_query_ray_upload_bytes"])
        self.assertGreaterEqual(audit["observed_host_to_device_bytes"], 262144)
        self.assertEqual(0, audit["observed_device_to_host_calls"])
        self.assertEqual(0, audit["observed_device_to_device_calls"])
        self.assertEqual(0, audit["observed_unknown_calls"])
        self.assertFalse(audit["full_window_true_zero_copy_ready"])

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("M14 Hit-Stream Full-Window Transfer Audit", report)
        self.assertIn("not an end-to-end true-zero-copy claim", report)


def _snapshot(
    *,
    host_to_device_bytes: int,
    device_to_host_calls: int = 0,
    device_to_host_bytes: int = 0,
) -> dict[str, object]:
    host_to_device_calls = 2 if host_to_device_bytes else 0
    total_calls = host_to_device_calls + int(device_to_host_calls)
    total_bytes = int(host_to_device_bytes) + int(device_to_host_bytes)
    return {
        "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
        "total_calls": total_calls,
        "total_bytes": total_bytes,
        "host_to_device_calls": host_to_device_calls,
        "host_to_device_bytes": int(host_to_device_bytes),
        "device_to_host_calls": int(device_to_host_calls),
        "device_to_host_bytes": int(device_to_host_bytes),
        "device_to_device_calls": 0,
        "device_to_device_bytes": 0,
        "unknown_calls": 0,
        "unknown_bytes": 0,
    }


def _synthetic_payload() -> dict[str, object]:
    snapshot = _snapshot(host_to_device_bytes=8 * rt.V3_M14_GPU_RAY3D_HOST_BYTES + 128)
    audit = rt.classify_v3_m14_full_window_transfer_snapshot(
        snapshot,
        ray_count=8,
        min_named_output_column_bytes=8 * 16,
    )
    row = {
        "partner": "cupy",
        "backend": "optix",
        "validation_signature": (16, 16, 16, 28, 8, 0, 0, 1),
        "ray_count": 8,
        "metadata": {
            "full_window_transfer_evidence": {
                "event_pair_scope": "native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization",
                "transfer_counter_scope": "producer_consumer",
                "transfer_counter_snapshot": snapshot,
            }
        },
        "transfer_audit": audit,
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "producer_input_upload_observed": True,
        "producer_input_upload_explained": True,
        "no_device_to_host_device_to_device_or_unknown_copy": True,
        "handoff_no_hidden_output_copy_ready": True,
        "full_window_true_zero_copy_ready": False,
        "public_claim_authorized": False,
    }
    return {
        "version": rt.V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_VERSION,
        "status": rt.V3_M14_HIT_STREAM_FULL_WINDOW_TRANSFER_AUDIT_STATUS,
        "graph_id": rt.V3_M14_GRAPH_ID,
        "contract_key": rt.V3_M14_CONTRACT_KEY,
        "partner_rows": (row,),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "producer_input_upload_observed": True,
            "producer_input_upload_explained": True,
            "no_device_to_host_device_to_device_or_unknown_copy": True,
            "handoff_no_hidden_output_copy_ready": True,
            "full_window_true_zero_copy_ready": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
