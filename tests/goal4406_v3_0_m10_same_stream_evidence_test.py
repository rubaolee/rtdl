from __future__ import annotations

from pathlib import Path
import json
import unittest

from rtdsl.v3_0_execution_graph import GraphValidationError
from rtdsl.v3_0_m10_same_stream_evidence import V3_M10_PARTNERS
from rtdsl.v3_0_m10_same_stream_evidence import V3_M10_SAME_STREAM_STATUS
from rtdsl.v3_0_m10_same_stream_evidence import V3_M10_SAME_STREAM_VERSION
from rtdsl.v3_0_m10_same_stream_evidence import build_v3_m10_same_stream_instrumentation
from rtdsl.v3_0_m10_same_stream_evidence import validate_v3_m10_same_stream_payload


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
RUNNER = ROOT / "scripts/v3_0_m10_same_stream_evidence_measure.py"
REPORT = ROOT / "docs/reports/goal4406_v3_0_m10_same_stream_evidence_2026-06-15.md"
ARTIFACT_8192 = ROOT / "docs/reports/goal4406_v3_0_m10_same_stream_evidence_8192_2026-06-15.json"
ARTIFACT_65536 = ROOT / "docs/reports/goal4406_v3_0_m10_same_stream_evidence_65536_2026-06-15.json"


class Goal4406V30M10SameStreamEvidenceTest(unittest.TestCase):
    def test_native_on_stream_abi_is_present(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        symbol = (
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_"
            "with_extended_telemetry_and_execution_options_on_stream"
        )
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn("apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix_on_stream", workloads)
        self.assertIn("d_grouped_union_params", workloads)
        self.assertIn("uint64_t cuda_stream_ptr", workloads)
        self.assertIn("CUstream stream = reinterpret_cast<CUstream>(cuda_stream_ptr)", workloads)
        self.assertIn("bool synchronize_after_launch = true", workloads)
        self.assertIn("if (synchronize_after_launch) {\n        CU_CHECK(cuStreamSynchronize(stream));", workloads)

    def test_python_runtime_exposes_on_stream_symbol(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")
        self.assertIn(
            "_OPTIX_PREPARED_FIXED_RADIUS_GROUPED_UNION_3D_SELF_DEVICE_OUTPUT_"
            "EXTENDED_TELEMETRY_EXECUTION_OPTIONS_ON_STREAM_SYMBOL",
            text,
        )
        self.assertIn("def apply_device_grouped_union_self_on_stream", text)
        self.assertIn("ctypes.c_uint64(cuda_stream_ptr)", text)
        self.assertIn("native_synchronized_before_return", text)
        self.assertIn("host_enqueue_timer_only_cuda_events_required_for_kernel_time", text)

    def test_partner_adapters_record_exact_event_evidence(self) -> None:
        text = ADAPTERS.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("def run_same_stream_evidence"), 2)
        self.assertIn("cupy_cuda_event_pair", text)
        self.assertIn("numba_cuda_event_pair", text)
        self.assertIn("prepared_native_optix_launch_to_cupy_label_kernel_on_same_stream", text)
        self.assertIn("prepared_native_optix_launch_to_numba_label_kernel_on_same_stream", text)
        self.assertIn('"transfer_counter_observed": False', text)
        self.assertIn('"true_zero_copy_ready": False', text)

    def test_runner_exists_for_pod_regeneration(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("run_v3_m10_same_stream_evidence_case", text)
        self.assertIn("--component-threshold", text)
        self.assertIn("default=7", text)
        self.assertIn("validate_v3_m10_same_stream_payload", text)

    def test_pod_artifacts_validate_and_report_states_boundary(self) -> None:
        self.assertTrue(REPORT.exists())
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("M10 is complete for same-stream evidence", report)
        self.assertIn("true_zero_copy_ready=false", report)
        for path in (ARTIFACT_8192, ARTIFACT_65536):
            self.assertTrue(path.exists(), f"missing {path}")
            payload = json.loads(path.read_text(encoding="utf-8"))
            validation = validate_v3_m10_same_stream_payload(payload)
            self.assertTrue(validation["same_stream_ready"])
            self.assertFalse(validation["true_zero_copy_ready"])
            for row in payload["partner_rows"]:
                evidence = row["metadata"]["same_stream_evidence"]
                self.assertEqual(evidence["cuda_stream_ptr"], evidence["native_metadata_cuda_stream_ptr"])
                self.assertFalse(evidence["native_synchronized_before_return"])

    def test_validator_accepts_strict_synthetic_payload(self) -> None:
        payload = _synthetic_payload()
        validation = validate_v3_m10_same_stream_payload(payload)
        self.assertEqual(V3_M10_SAME_STREAM_STATUS, validation["status"])
        self.assertTrue(validation["same_stream_ready"])
        self.assertFalse(validation["true_zero_copy_ready"])

    def test_validator_rejects_missing_event_evidence(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        metadata = dict(row["metadata"])
        evidence = dict(metadata["same_stream_evidence"])
        evidence["evidence_source"] = "pointer_identity"
        metadata["same_stream_evidence"] = evidence
        row["metadata"] = metadata
        payload["partner_rows"] = (row, payload["partner_rows"][1])
        with self.assertRaises(GraphValidationError):
            validate_v3_m10_same_stream_payload(payload)

    def test_validator_rejects_true_zero_copy_without_transfer_counters(self) -> None:
        payload = _synthetic_payload()
        payload["comparison"] = dict(payload["comparison"])
        payload["comparison"]["true_zero_copy_ready"] = True
        with self.assertRaises(GraphValidationError):
            validate_v3_m10_same_stream_payload(payload)

    def test_instrumentation_readiness_is_scoped(self) -> None:
        packet = build_v3_m10_same_stream_instrumentation(
            partner="cupy",
            hardware="unit_test_gpu",
            prepare_seconds=0.1,
            host_run_seconds=0.03,
            native_event_seconds=0.01,
            partner_event_seconds=0.002,
            total_event_seconds=0.013,
            validation_seconds=0.001,
            data_ptrs={"component_labels": 1234},
            metadata={
                "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query_on_stream",
                "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
            },
            same_stream_evidence=_synthetic_evidence("cupy"),
        )
        self.assertTrue(packet.claim_readiness["same_stream_ready"])
        self.assertTrue(packet.claim_readiness["device_resident_ready"])
        self.assertFalse(packet.claim_readiness["true_zero_copy_ready"])
        self.assertFalse(packet.claim_readiness["public_claim_authorized"])


def _synthetic_payload() -> dict[str, object]:
    rows = tuple(_synthetic_row(partner) for partner in V3_M10_PARTNERS)
    return {
        "version": V3_M10_SAME_STREAM_VERSION,
        "status": V3_M10_SAME_STREAM_STATUS,
        "partner_rows": rows,
        "comparison": {
            "signature_match": True,
            "same_stream_ready": True,
            "true_zero_copy_ready": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
    }


def _synthetic_row(partner: str) -> dict[str, object]:
    evidence = _synthetic_evidence(partner)
    return {
        "partner": partner,
        "validation_signature": (2, 2),
        "same_stream_ready": True,
        "true_zero_copy_ready": False,
        "public_claim_authorized": False,
        "metadata": {
            "same_stream_evidence": evidence,
        },
        "instrumentation": {
            "claim_readiness": {
                "same_stream_ready": True,
                "true_zero_copy_ready": False,
            }
        },
    }


def _synthetic_evidence(partner: str) -> dict[str, object]:
    return {
        "partner": partner,
        "evidence_source": f"{partner}_cuda_event_pair",
        "cuda_stream_ptr": 100,
        "native_start_event_ptr": 10,
        "native_done_event_ptr": 11,
        "partner_done_event_ptr": 12,
        "native_event_ms": 1.0,
        "partner_event_ms": 0.2,
        "total_event_ms": 1.3,
        "event_pair_scope": f"prepared_native_optix_launch_to_{partner}_label_kernel_on_same_stream",
        "native_symbol": "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_extended_telemetry_and_execution_options_on_stream",
        "native_metadata_cuda_stream_ptr": 100,
        "native_synchronized_before_return": False,
        "validation_materialization_after_measured_window": True,
        "transfer_counter_observed": False,
        "true_zero_copy_ready": False,
        "same_stream_ready": True,
    }


if __name__ == "__main__":
    unittest.main()
