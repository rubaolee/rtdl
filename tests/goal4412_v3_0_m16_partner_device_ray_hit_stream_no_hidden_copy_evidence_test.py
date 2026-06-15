from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/rtdsl/v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence.py"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
RUNNER = ROOT / "scripts/v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_measure.py"
REPORT = ROOT / "docs/reports/goal4412_v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4412_v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence_8192_2026-06-15.json"


class Goal4412V30M16PartnerDeviceRayHitStreamNoHiddenCopyEvidenceTest(unittest.TestCase):
    def test_m16_module_defines_partner_device_ray_contract(self) -> None:
        text = MODULE.read_text(encoding="utf-8")
        self.assertIn("V3_M16_PARTNER_DEVICE_RAY_HIT_STREAM_NO_HIDDEN_COPY_VERSION", text)
        self.assertIn("partner_device_ray_prepared_hit_stream_full_window_no_hidden_copy_pilot", text)
        self.assertIn("make_v3_m16_cupy_ray_columns", text)
        self.assertIn("scene.prepare_ray_batch_device_columns(ray_columns)", text)
        self.assertIn("ray_columns_partner_owned", text)
        self.assertIn("source_protocols", text)
        self.assertIn("query_rays_uploaded_each_run", text)
        self.assertIn("classify_no_hidden_copy_transfer_snapshot", text)

    def test_runtime_has_partner_device_ray_batch_metadata(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("prepare_ray_batch_device_columns", text)
        self.assertIn("ray_batch_created_from\": \"partner_device_columns", text)
        self.assertIn("ray_columns_partner_owned\": True", text)
        self.assertIn("query_rays_packed_on_device_once", text)
        self.assertIn("prepared_device_ray_batch_no_per_run_ray_upload", text)

    def test_runner_preloads_counter_before_rtdsl_import(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("LD_PRELOAD", text)
        self.assertIn("os.execvpe", text)
        self.assertLess(text.index("_ensure_transfer_counter_preloaded"), text.index("import rtdsl as rt"))
        self.assertIn("run_v3_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence_case", text)

    def test_validator_accepts_synthetic_m16_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m16_partner_device_ray_hit_stream_no_hidden_copy_payload(payload)
        self.assertTrue(validation["ray_columns_partner_owned"])
        self.assertFalse(validation["query_rays_uploaded_each_run"])
        self.assertTrue(validation["true_zero_copy_ready"])

    def test_validator_rejects_host_created_ray_batch(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        row["ray_columns_partner_owned"] = False
        payload["partner_rows"] = (row,)
        with self.assertRaisesRegex(GraphValidationError, "partner-owned ray columns"):
            rt.validate_v3_m16_partner_device_ray_hit_stream_no_hidden_copy_payload(payload)

    def test_pod_artifact_and_report_capture_partner_device_ray_gate(self) -> None:
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_v3_m16_partner_device_ray_hit_stream_no_hidden_copy_payload(payload)
        self.assertTrue(validation["ray_columns_partner_owned"])
        self.assertFalse(validation["query_rays_uploaded_each_run"])
        self.assertTrue(validation["no_hidden_column_copy_ready"])
        self.assertTrue(validation["true_zero_copy_ready"])

        row = payload["partner_rows"][0]
        self.assertEqual("cupy", row["partner"])
        self.assertEqual(8192, row["ray_count"])
        self.assertEqual([16384, 16384, 16384, 67100672, 8192, 0, 0, 1], row["validation_signature"])
        self.assertEqual("partner_device_columns", row["ray_batch_created_from"])
        evidence = row["metadata"]["same_stream_evidence"]
        self.assertIn("cupy", evidence["source_protocols"])
        self.assertTrue(evidence["ray_columns_partner_owned"])
        self.assertEqual("partner_device_columns", evidence["ray_batch_created_from"])
        summary = row["transfer_counter_summary"]
        self.assertEqual(5, summary["sample_count"])
        self.assertLessEqual(summary["max_observed_host_to_device_bytes"], 4096)
        classification = row["transfer_counter_classification"]
        self.assertEqual(0, classification["observed_device_to_host_calls"])
        self.assertEqual(0, classification["observed_device_to_device_calls"])
        self.assertEqual(0, classification["observed_unknown_calls"])
        self.assertTrue(classification["true_zero_copy_ready"])

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("M16 Partner-Device-Ray Hit-Stream No-Hidden-Copy Evidence", report)
        self.assertIn("partner-owned CuPy device ray columns", report)


def _snapshot() -> dict[str, object]:
    return {
        "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
        "total_calls": 1,
        "total_bytes": 88,
        "host_to_device_calls": 1,
        "host_to_device_bytes": 88,
        "device_to_host_calls": 0,
        "device_to_host_bytes": 0,
        "device_to_device_calls": 0,
        "device_to_device_bytes": 0,
        "unknown_calls": 0,
        "unknown_bytes": 0,
    }


def _synthetic_payload() -> dict[str, object]:
    classification = rt.classify_no_hidden_copy_transfer_snapshot(
        _snapshot(),
        min_named_column_bytes=8192,
        measured_window=(
            "partner_device_ray_prepared_native_producer_enqueue_to_same_stream_"
            "hit_stream_row_reduction_before_summary_materialization"
        ),
        readiness_source="v3_m16_partner_device_ray_hit_stream_transfer_counter_classification",
    )
    metadata = rt.annotate_no_hidden_copy_metadata(
        {
            "same_stream_evidence": {
                "event_pair_scope": "partner_device_ray_prepared_native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization",
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": _snapshot(),
                "prepared_ray_batch_used": True,
                "ray_columns_partner_owned": True,
                "ray_batch_created_from": "partner_device_columns",
                "source_protocols": ("cupy",),
                "query_rays_uploaded_each_run": False,
                "prepared_rays_resident_on_device": True,
                "host_row_materialization_before_consumer": False,
            }
        },
        classification,
        readiness_source="v3_m16_partner_device_ray_hit_stream_transfer_counter_classification",
    )
    return {
        "version": rt.V3_M16_PARTNER_DEVICE_RAY_HIT_STREAM_NO_HIDDEN_COPY_VERSION,
        "status": rt.V3_M16_PARTNER_DEVICE_RAY_HIT_STREAM_NO_HIDDEN_COPY_STATUS,
        "graph_id": rt.V3_M16_GRAPH_ID,
        "contract_key": rt.V3_M16_CONTRACT_KEY,
        "partner_rows": (
            {
                "partner": "cupy",
                "backend": "optix",
                "validation_signature": (16, 16, 16, 28, 8, 0, 0, 1),
                "ray_count": 8,
                "metadata": metadata,
                "transfer_counter_classification": classification,
                "same_stream_ready": True,
                "transfer_counter_observed": True,
                "prepared_ray_batch_used": True,
                "ray_columns_partner_owned": True,
                "ray_batch_created_from": "partner_device_columns",
                "query_rays_uploaded_each_run": False,
                "no_hidden_column_copy_ready": True,
                "true_zero_copy_ready": True,
                "public_claim_authorized": False,
            },
        ),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "prepared_ray_batch_used": True,
            "ray_columns_partner_owned": True,
            "query_rays_uploaded_each_run": False,
            "no_hidden_column_copy_ready": True,
            "true_zero_copy_ready": True,
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
