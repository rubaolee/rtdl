from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/rtdsl/v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence.py"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
NATIVE = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
RUNNER = ROOT / "scripts/v3_0_m17_partner_device_ray_prepare_no_hidden_copy_measure.py"
REPORT = ROOT / "docs/reports/goal4413_v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4413_v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence_8192_2026-06-15.json"


class Goal4413V30M17PartnerDeviceRayPrepareNoHiddenCopyEvidenceTest(unittest.TestCase):
    def test_m17_module_defines_prepare_and_hot_path_contract(self) -> None:
        text = MODULE.read_text(encoding="utf-8")
        self.assertIn("V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_VERSION", text)
        self.assertIn("partner_device_ray_prepare_and_hit_stream_no_hidden_copy_pilot", text)
        self.assertIn("scene.prepare_ray_batch_device_columns(ray_columns)", text)
        self.assertIn("partner_device_ray_batch_prepare_from_device_columns_before_hot_path", text)
        self.assertIn("prepare_transfer_counter_classification", text)
        self.assertIn("ray_id_host_bookkeeping_downloaded", text)
        self.assertIn("host_ray_ids_available", text)

    def test_runtime_and_native_use_device_only_hit_stream_contract(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        native = NATIVE.read_text(encoding="utf-8")
        self.assertIn('"ray_id_host_bookkeeping_downloaded": False', runtime)
        self.assertIn('"host_ray_ids_available": False', runtime)
        self.assertIn("bool host_ray_ids_available = false", native)
        self.assertIn("host_ray_ids_available(true)", native)
        self.assertIn("require_host_ray_ids", native)
        self.assertIn("hit-stream-safe device-only contract", native)
        self.assertNotIn("download(host_ray_ids.data()", native)

    def test_runner_preloads_counter_before_rtdsl_import(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("LD_PRELOAD", text)
        self.assertIn("os.execvpe", text)
        self.assertLess(text.index("_ensure_transfer_counter_preloaded"), text.index("import rtdsl as rt"))
        self.assertIn("run_v3_m17_partner_device_ray_prepare_no_hidden_copy_evidence_case", text)

    def test_validator_accepts_synthetic_m17_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m17_partner_device_ray_prepare_no_hidden_copy_payload(payload)
        self.assertTrue(validation["ray_columns_partner_owned"])
        self.assertFalse(validation["ray_id_host_bookkeeping_downloaded"])
        self.assertTrue(validation["prepare_no_hidden_column_copy_ready"])
        self.assertTrue(validation["true_zero_copy_ready"])

    def test_validator_rejects_prepare_ray_id_download(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        row["ray_id_host_bookkeeping_downloaded"] = True
        payload["partner_rows"] = (row,)
        with self.assertRaisesRegex(GraphValidationError, "ray IDs"):
            rt.validate_v3_m17_partner_device_ray_prepare_no_hidden_copy_payload(payload)

    def test_validator_rejects_prepare_device_to_host_copy(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        classification = dict(row["prepare_transfer_counter_classification"])
        classification["observed_device_to_host_calls"] = 1
        row["prepare_transfer_counter_classification"] = classification
        payload["partner_rows"] = (row,)
        with self.assertRaisesRegex(GraphValidationError, "device_to_host"):
            rt.validate_v3_m17_partner_device_ray_prepare_no_hidden_copy_payload(payload)

    def test_pod_artifact_and_report_capture_prepare_gate(self) -> None:
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_v3_m17_partner_device_ray_prepare_no_hidden_copy_payload(payload)
        self.assertTrue(validation["ray_columns_partner_owned"])
        self.assertFalse(validation["ray_id_host_bookkeeping_downloaded"])
        self.assertTrue(validation["prepare_no_hidden_column_copy_ready"])
        self.assertTrue(validation["hot_no_hidden_column_copy_ready"])
        self.assertTrue(validation["true_zero_copy_ready"])

        row = payload["partner_rows"][0]
        self.assertEqual("cupy", row["partner"])
        self.assertEqual(8192, row["ray_count"])
        self.assertEqual([16384, 16384, 16384, 67100672, 8192, 0, 0, 1], row["validation_signature"])
        self.assertEqual("partner_device_columns", row["ray_batch_created_from"])
        self.assertFalse(row["ray_id_host_bookkeeping_downloaded"])
        prepare_summary = row["prepare_transfer_counter_summary"]
        self.assertEqual(5, prepare_summary["sample_count"])
        self.assertLessEqual(prepare_summary["max_observed_host_to_device_bytes"], 4096)
        prepare_classification = row["prepare_transfer_counter_classification"]
        self.assertEqual(0, prepare_classification["observed_device_to_host_calls"])
        self.assertEqual(0, prepare_classification["observed_device_to_device_calls"])
        self.assertEqual(0, prepare_classification["observed_unknown_calls"])
        hot_classification = row["transfer_counter_classification"]
        self.assertEqual(0, hot_classification["observed_device_to_host_calls"])
        self.assertEqual(0, hot_classification["observed_device_to_device_calls"])
        self.assertEqual(0, hot_classification["observed_unknown_calls"])

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("M17 Partner-Device-Ray Prepare No-Hidden-Copy Evidence", report)
        self.assertIn("ray-id host bookkeeping", report)


def _snapshot(*, d2h_calls: int = 0, d2h_bytes: int = 0, h2d_calls: int = 0, h2d_bytes: int = 0) -> dict[str, object]:
    return {
        "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
        "total_calls": d2h_calls + h2d_calls,
        "total_bytes": d2h_bytes + h2d_bytes,
        "host_to_device_calls": h2d_calls,
        "host_to_device_bytes": h2d_bytes,
        "device_to_host_calls": d2h_calls,
        "device_to_host_bytes": d2h_bytes,
        "device_to_device_calls": 0,
        "device_to_device_bytes": 0,
        "unknown_calls": 0,
        "unknown_bytes": 0,
    }


def _synthetic_payload() -> dict[str, object]:
    prepare_classification = rt.classify_no_hidden_copy_transfer_snapshot(
        _snapshot(),
        min_named_column_bytes=32,
        measured_window="partner_device_ray_batch_prepare_from_device_columns_before_hot_path",
        readiness_source="v3_m17_partner_device_ray_prepare_transfer_counter_classification",
    )
    hot_classification = rt.classify_no_hidden_copy_transfer_snapshot(
        _snapshot(h2d_calls=1, h2d_bytes=88),
        min_named_column_bytes=8192,
        measured_window=(
            "partner_device_ray_prepare_native_producer_enqueue_to_same_stream_"
            "hit_stream_row_reduction_before_summary_materialization"
        ),
        readiness_source="v3_m17_partner_device_ray_hot_path_transfer_counter_classification",
    )
    metadata = rt.annotate_no_hidden_copy_metadata(
        {
            "prepare_evidence": {
                "event_pair_scope": "partner_device_ray_batch_prepare_from_device_columns_before_hot_path",
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": _snapshot(),
                "ray_columns_partner_owned": True,
                "ray_batch_created_from": "partner_device_columns",
                "source_protocols": ("cupy",),
                "ray_id_host_bookkeeping_downloaded": False,
                "host_ray_ids_available": False,
                "prepared_rays_resident_on_device": True,
            },
            "same_stream_evidence": {
                "event_pair_scope": "partner_device_ray_prepare_native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization",
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": _snapshot(h2d_calls=1, h2d_bytes=88),
                "prepared_ray_batch_used": True,
                "ray_columns_partner_owned": True,
                "ray_batch_created_from": "partner_device_columns",
                "source_protocols": ("cupy",),
                "query_rays_uploaded_each_run": False,
                "prepared_rays_resident_on_device": True,
                "host_row_materialization_before_consumer": False,
            },
        },
        hot_classification,
        all_samples_ready=True,
        readiness_source="v3_m17_partner_device_ray_prepare_and_hot_path_transfer_counter_classification",
    )
    return {
        "version": rt.V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_VERSION,
        "status": rt.V3_M17_PARTNER_DEVICE_RAY_PREPARE_NO_HIDDEN_COPY_STATUS,
        "graph_id": rt.V3_M17_GRAPH_ID,
        "contract_key": rt.V3_M17_CONTRACT_KEY,
        "partner_rows": (
            {
                "partner": "cupy",
                "backend": "optix",
                "validation_signature": (16, 16, 16, 28, 8, 0, 0, 1),
                "ray_count": 8,
                "metadata": metadata,
                "prepare_transfer_counter_classification": prepare_classification,
                "transfer_counter_classification": hot_classification,
                "same_stream_ready": True,
                "transfer_counter_observed": True,
                "prepare_transfer_counter_observed": True,
                "prepared_ray_batch_used": True,
                "ray_columns_partner_owned": True,
                "ray_batch_created_from": "partner_device_columns",
                "ray_id_host_bookkeeping_downloaded": False,
                "host_ray_ids_available": False,
                "query_rays_uploaded_each_run": False,
                "prepare_no_hidden_column_copy_ready": True,
                "hot_no_hidden_column_copy_ready": True,
                "no_hidden_column_copy_ready": True,
                "true_zero_copy_ready": True,
                "public_claim_authorized": False,
            },
        ),
        "comparison": {
            "signature_match": True,
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "prepare_transfer_counter_observed": True,
            "prepared_ray_batch_used": True,
            "ray_columns_partner_owned": True,
            "ray_id_host_bookkeeping_downloaded": False,
            "query_rays_uploaded_each_run": False,
            "prepare_no_hidden_column_copy_ready": True,
            "hot_no_hidden_column_copy_ready": True,
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
