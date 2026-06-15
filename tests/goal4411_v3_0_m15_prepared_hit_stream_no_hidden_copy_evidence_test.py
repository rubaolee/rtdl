from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/rtdsl/v3_0_m15_prepared_hit_stream_no_hidden_copy_evidence.py"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
RUNNER = ROOT / "scripts/v3_0_m15_prepared_hit_stream_no_hidden_copy_measure.py"
REPORT = ROOT / "docs/reports/goal4411_v3_0_m15_prepared_hit_stream_no_hidden_copy_evidence_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4411_v3_0_m15_prepared_hit_stream_no_hidden_copy_evidence_8192_2026-06-15.json"


class Goal4411V30M15PreparedHitStreamNoHiddenCopyEvidenceTest(unittest.TestCase):
    def test_native_symbol_is_declared_wrapped_and_implemented(self) -> None:
        symbol = "rtdl_optix_static_triangle_scene_3d_ray_batch_triangle_hit_stream_into_device_columns_with_status_on_stream"
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(f'extern "C" int {symbol}', API.read_text(encoding="utf-8"))
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(
            "run_prepared_static_triangle_scene_3d_ray_batch_triangle_hit_stream_into_device_columns_with_status_on_stream_optix",
            workloads,
        )
        self.assertIn("lp.rays = reinterpret_cast<const GpuRay3DHost*>(ray_batch->d_rays.ptr)", workloads)
        self.assertNotIn("upload_async(owner->rays", _batch_function_body(workloads))

    def test_runtime_exposes_prepared_ray_batch_same_stream_method(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("OPTIX_RAY_BATCH_TRIANGLE_HIT_STREAM_3D_INTO_DEVICE_COLUMNS_WITH_STATUS_ON_STREAM_SYMBOL", text)
        self.assertIn("ray_batch_triangle_hit_stream_same_stream_row_reduction_summary", text)
        method_start = text.index("def ray_batch_triangle_hit_stream_same_stream_row_reduction_summary")
        method_end = text.index("def ray_triangle_hit_stream_event_ordered_row_reduction_summary", method_start)
        method = text[method_start:method_end]
        self.assertIn("PreparedOptixRayBatch3D", method)
        self.assertIn('"prepared_device_ray_batch_no_per_run_ray_upload"', method)
        self.assertIn('"query_rays_uploaded_each_run": False', method)
        self.assertIn('"prepared_rays_resident_on_device": True', method)
        self.assertIn("transfer_counter_scope: str = \"producer_consumer\"", method)

    def test_m15_module_defines_full_window_no_hidden_copy_contract(self) -> None:
        text = MODULE.read_text(encoding="utf-8")
        self.assertIn("V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_VERSION", text)
        self.assertIn("prepared_ray_batch_hit_stream_full_window_no_hidden_copy_pilot", text)
        self.assertIn("classify_no_hidden_copy_transfer_snapshot", text)
        self.assertIn("validate_no_hidden_copy_payload", text)
        self.assertIn("query_rays_uploaded_each_run", text)
        self.assertIn("prepared_rays_resident_on_device", text)

    def test_runner_preloads_counter_before_rtdsl_import(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("LD_PRELOAD", text)
        self.assertIn("os.execvpe", text)
        self.assertLess(text.index("_ensure_transfer_counter_preloaded"), text.index("import rtdsl as rt"))
        self.assertIn("run_v3_m15_prepared_hit_stream_no_hidden_copy_evidence_case", text)

    def test_validator_accepts_synthetic_m15_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m15_prepared_hit_stream_no_hidden_copy_payload(payload)
        self.assertTrue(validation["prepared_ray_batch_used"])
        self.assertFalse(validation["query_rays_uploaded_each_run"])
        self.assertTrue(validation["true_zero_copy_ready"])

    def test_validator_rejects_per_run_query_ray_upload(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        row["query_rays_uploaded_each_run"] = True
        payload["partner_rows"] = (row,)
        with self.assertRaisesRegex(GraphValidationError, "must not upload query rays"):
            rt.validate_v3_m15_prepared_hit_stream_no_hidden_copy_payload(payload)

    def test_pod_artifact_and_report_capture_prepared_full_window_gate(self) -> None:
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_v3_m15_prepared_hit_stream_no_hidden_copy_payload(payload)
        self.assertTrue(validation["prepared_ray_batch_used"])
        self.assertFalse(validation["query_rays_uploaded_each_run"])
        self.assertTrue(validation["no_hidden_column_copy_ready"])
        self.assertTrue(validation["true_zero_copy_ready"])

        row = payload["partner_rows"][0]
        self.assertEqual("cupy", row["partner"])
        self.assertEqual(8192, row["ray_count"])
        self.assertEqual([16384, 16384, 16384, 67100672, 8192, 0, 0, 1], row["validation_signature"])
        summary = row["transfer_counter_summary"]
        self.assertEqual(5, summary["sample_count"])
        self.assertLessEqual(summary["max_observed_host_to_device_bytes"], 4096)
        self.assertEqual(0, row["transfer_counter_classification"]["observed_device_to_host_calls"])
        self.assertEqual(0, row["transfer_counter_classification"]["observed_device_to_device_calls"])
        self.assertEqual(0, row["transfer_counter_classification"]["observed_unknown_calls"])
        self.assertTrue(row["transfer_counter_classification"]["no_hidden_column_copy_ready"])

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("M15 Prepared Hit-Stream No-Hidden-Copy Evidence", report)
        self.assertIn("no per-run query-ray upload", report)


def _batch_function_body(text: str) -> str:
    start = text.index(
        "static void run_prepared_static_triangle_scene_3d_ray_batch_triangle_hit_stream_into_device_columns_with_status_on_stream_optix"
    )
    end = text.index("static void release_ray_triangle_hit_stream_device_columns_optix", start)
    return text[start:end]


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
            "prepared_ray_batch_native_producer_enqueue_to_same_stream_"
            "hit_stream_row_reduction_before_summary_materialization"
        ),
        readiness_source="v3_m15_prepared_hit_stream_transfer_counter_classification",
    )
    metadata = rt.annotate_no_hidden_copy_metadata(
        {
            "same_stream_evidence": {
                "event_pair_scope": "prepared_ray_batch_native_producer_enqueue_to_cupy_row_reduction_before_summary_materialization",
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": _snapshot(),
                "prepared_ray_batch_used": True,
                "query_rays_uploaded_each_run": False,
                "prepared_rays_resident_on_device": True,
                "host_row_materialization_before_consumer": False,
            }
        },
        classification,
        readiness_source="v3_m15_prepared_hit_stream_transfer_counter_classification",
    )
    return {
        "version": rt.V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_VERSION,
        "status": rt.V3_M15_PREPARED_HIT_STREAM_NO_HIDDEN_COPY_STATUS,
        "graph_id": rt.V3_M15_GRAPH_ID,
        "contract_key": rt.V3_M15_CONTRACT_KEY,
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
