from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
COUNTER_SOURCE = ROOT / "src/native/tools/rtdl_cuda_transfer_counter.c"
RUNNER = ROOT / "scripts/v3_0_m11_no_hidden_copy_measure.py"
MODULE = ROOT / "src/rtdsl/v3_0_m11_no_hidden_copy_evidence.py"


class Goal4407V30M11NoHiddenCopyEvidenceTest(unittest.TestCase):
    def test_transfer_counter_intercepts_cuda_copy_symbols(self) -> None:
        text = COUNTER_SOURCE.read_text(encoding="utf-8")
        for symbol in (
            "cuMemcpyHtoD_v2",
            "cuMemcpyDtoH_v2",
            "cuMemcpyDtoD_v2",
            "cuMemcpyAsync_v2",
            "cudaMemcpyAsync",
            "rtdl_cuda_transfer_counter_snapshot",
            "rtdl_cuda_transfer_counter_set_enabled",
        ):
            self.assertIn(symbol, text)
        self.assertIn("RTDL_COPY_HOST_TO_DEVICE", text)
        self.assertIn("RTDL_COPY_DEVICE_TO_HOST", text)
        self.assertIn('dlopen("libcuda.so.1"', text)
        self.assertIn("RTDL_DRIVER_ORIGINAL_OR_ALT", text)

    def test_runner_builds_and_preloads_counter_before_rtdsl_import(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("-shared", text)
        self.assertIn("LD_PRELOAD", text)
        self.assertIn("os.execvpe", text)
        self.assertIn('"reason": "already_preloaded"', text)
        self.assertLess(text.index("already_preloaded ="), text.index("_build_transfer_counter"))
        self.assertLess(text.index("_ensure_transfer_counter_preloaded"), text.index("import rtdsl as rt"))
        self.assertIn("run_v3_m11_no_hidden_copy_evidence_case", text)

    def test_module_exports_strict_m11_contract(self) -> None:
        text = MODULE.read_text(encoding="utf-8")
        self.assertIn("V3_M11_NO_HIDDEN_COPY_STATUS", text)
        self.assertIn("classify_transfer_counter_snapshot", text)
        self.assertIn("device_to_host_copy_observed", text)
        self.assertIn("host_to_device_bytes_exceed_allowed_launch_parameter_scope", text)
        self.assertIn("true_zero_copy_ready", text)

    def test_transfer_snapshot_classifier_allows_small_launch_param_upload(self) -> None:
        classification = rt.classify_transfer_counter_snapshot(
            {
                "total_calls": 1,
                "total_bytes": 128,
                "host_to_device_calls": 1,
                "host_to_device_bytes": 128,
                "device_to_host_calls": 0,
                "device_to_host_bytes": 0,
                "device_to_device_calls": 0,
                "device_to_device_bytes": 0,
                "unknown_calls": 0,
                "unknown_bytes": 0,
            },
            point_count=8192,
        )
        self.assertTrue(classification["no_hidden_column_copy_ready"])
        self.assertTrue(classification["true_zero_copy_ready"])
        self.assertEqual(32768, classification["min_named_column_bytes"])

    def test_transfer_snapshot_classifier_rejects_device_to_host_copy(self) -> None:
        classification = rt.classify_transfer_counter_snapshot(
            {
                "total_calls": 1,
                "total_bytes": 64,
                "host_to_device_calls": 0,
                "host_to_device_bytes": 0,
                "device_to_host_calls": 1,
                "device_to_host_bytes": 64,
                "device_to_device_calls": 0,
                "device_to_device_bytes": 0,
                "unknown_calls": 0,
                "unknown_bytes": 0,
            },
            point_count=8192,
        )
        self.assertFalse(classification["no_hidden_column_copy_ready"])
        self.assertIn("device_to_host_copy_observed", classification["disallowed_reasons"])

    def test_validator_accepts_synthetic_counter_backed_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m11_no_hidden_copy_payload(payload)
        self.assertTrue(validation["same_stream_ready"])
        self.assertTrue(validation["transfer_counter_observed"])
        self.assertTrue(validation["true_zero_copy_ready"])
        self.assertFalse(validation["public_claim_authorized"])

    def test_validator_rejects_hidden_copy_observed(self) -> None:
        payload = _synthetic_payload()
        row = dict(payload["partner_rows"][0])
        classification = dict(row["transfer_counter_classification"])
        classification["hidden_copy_observed"] = True
        classification["no_hidden_column_copy_ready"] = False
        classification["true_zero_copy_ready"] = False
        classification["observed_device_to_host_calls"] = 1
        row["transfer_counter_classification"] = classification
        row["no_hidden_column_copy_ready"] = False
        row["true_zero_copy_ready"] = False
        payload["partner_rows"] = (row, payload["partner_rows"][1])
        with self.assertRaises(GraphValidationError):
            rt.validate_v3_m11_no_hidden_copy_payload(payload)


def _synthetic_payload() -> dict[str, object]:
    rows = tuple(_synthetic_row(partner) for partner in rt.V3_M11_PARTNERS)
    return {
        "version": rt.V3_M11_NO_HIDDEN_COPY_VERSION,
        "status": rt.V3_M11_NO_HIDDEN_COPY_STATUS,
        "partner_rows": rows,
        "comparison": {
            "signature_match": True,
            "same_stream_ready": True,
            "transfer_counter_observed": True,
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


def _synthetic_row(partner: str) -> dict[str, object]:
    snapshot = {
        "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
        "total_calls": 1,
        "total_bytes": 128,
        "host_to_device_calls": 1,
        "host_to_device_bytes": 128,
        "device_to_host_calls": 0,
        "device_to_host_bytes": 0,
        "device_to_device_calls": 0,
        "device_to_device_bytes": 0,
        "unknown_calls": 0,
        "unknown_bytes": 0,
    }
    classification = rt.classify_transfer_counter_snapshot(snapshot, point_count=8192)
    return {
        "partner": partner,
        "validation_signature": (2, 2),
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "no_hidden_column_copy_ready": True,
        "true_zero_copy_ready": True,
        "public_claim_authorized": False,
        "transfer_counter_classification": classification,
        "metadata": {
            "same_stream_evidence": {
                "evidence_source": f"{partner}_cuda_event_pair",
                "event_pair_scope": f"prepared_native_optix_launch_to_{partner}_label_kernel_on_same_stream",
                "cuda_stream_ptr": 100,
                "native_metadata_cuda_stream_ptr": 100,
                "native_synchronized_before_return": False,
                "validation_materialization_after_measured_window": True,
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": snapshot,
            }
        },
        "instrumentation": {
            "claim_readiness": {
                "same_stream_ready": True,
                "true_zero_copy_ready": True,
            }
        },
    }


if __name__ == "__main__":
    unittest.main()
