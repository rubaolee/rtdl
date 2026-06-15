from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
MODULE = ROOT / "src/rtdsl/v3_0_m21_max_nearest_device_reduction.py"
RUNNER = ROOT / "scripts/v3_0_m21_max_nearest_device_reduction_measure.py"
REPORT = ROOT / "docs/reports/goal4418_v3_0_m21_max_nearest_device_reduction_2026-06-15.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4418_v3_0_m21_max_nearest_device_reduction_65536_2026-06-15.json"
)


class Goal4418V30M21MaxNearestDeviceReductionTest(unittest.TestCase):
    def test_native_and_runtime_expose_device_query_column_path(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("load_point_group_nearest_query", core)
        self.assertIn("params.use_device_columns", core)
        self.assertIn("const double* query_x", core)
        self.assertIn("const double* query_y", core)
        self.assertIn("write_prepared_point_group_nearest_witness_2d_device_query_columns_optix", workloads)
        self.assertIn("lp.query_points = nullptr", workloads)
        self.assertIn("lp.use_device_columns = 1u", workloads)
        self.assertIn("split_point_group_nearest_columns", workloads)
        symbol = "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns"
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, runtime)
        self.assertIn("write_device_nearest_witness_columns_from_device_query_columns", runtime)
        self.assertIn("pack_optix_fixed_radius_count_threshold_2d_device_point_inputs", runtime)
        self.assertIn("query_point_columns_true_zero_copy_authorized", runtime)
        self.assertIn("output_columns_true_zero_copy_authorized", runtime)

    def test_numba_argmax_can_skip_hot_window_host_valid_count_check(self) -> None:
        continuation = (ROOT / "src/rtdsl/numba_partner_continuation.py").read_text(encoding="utf-8")
        adapters = (ROOT / "src/rtdsl/partner_adapters.py").read_text(encoding="utf-8")
        self.assertIn("validate_non_empty_on_host: bool = True", continuation)
        self.assertIn("if validate_non_empty_on_host:", continuation)
        self.assertIn('"host_valid_count_check_used": bool(validate_non_empty_on_host)', continuation)
        self.assertIn("validate_non_empty_on_host: bool = True", adapters)
        self.assertIn("validate_non_empty_on_host=validate_non_empty_on_host", adapters)
        self.assertIn('"host_valid_count_check_used": bool(result.get("host_valid_count_check_used"))', adapters)

    def test_m21_module_and_runner_define_two_partner_device_reduction_bridge(self) -> None:
        module = MODULE.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('V3_M21_PARTNERS = ("cupy", "numba")', module)
        self.assertIn("prepared_point_group_nearest_device_query_partner_reduction", module)
        self.assertIn("write_device_nearest_witness_columns_from_device_query_columns", module)
        self.assertIn("global_argmax_u32_f64_partner_columns", module)
        self.assertIn("validate_non_empty_on_host=False", module)
        self.assertIn("_run_cupy_global_argmax_device", module)
        self.assertIn("cp.cuda.runtime.deviceSynchronize()", module)
        self.assertIn("hot_device_synchronized_before_timer_stop", module)
        self.assertIn("host_query_upload_in_hot_window", module)
        self.assertIn("device_result_materialized_in_hot_window", module)
        self.assertIn("LD_PRELOAD", runner)
        self.assertIn("--numba-cuda-home", runner)
        self.assertIn("run_v3_m21_max_nearest_device_reduction_case", runner)

    def test_validator_accepts_synthetic_m21_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m21_max_nearest_device_reduction_payload(payload)
        self.assertEqual(2, validation["partner_count"])
        self.assertTrue(validation["signature_match"])
        self.assertTrue(validation["hot_no_hidden_column_copy_ready"])

    def test_validator_rejects_signature_mismatch(self) -> None:
        payload = _synthetic_payload()
        rows = [dict(row) for row in payload["partner_rows"]]
        rows[1]["validation_signature"] = (2, 3, 4, 5, 6)
        payload["partner_rows"] = tuple(rows)
        with self.assertRaisesRegex(GraphValidationError, "signatures"):
            rt.validate_v3_m21_max_nearest_device_reduction_payload(payload)

    def test_validator_rejects_hot_query_upload_and_public_claims(self) -> None:
        payload = _synthetic_payload()
        rows = [dict(row) for row in payload["partner_rows"]]
        rows[0]["host_query_upload_in_hot_window"] = True
        payload["partner_rows"] = tuple(rows)
        with self.assertRaisesRegex(GraphValidationError, "host_query_upload_in_hot_window"):
            rt.validate_v3_m21_max_nearest_device_reduction_payload(payload)

        payload = _synthetic_payload()
        payload["claim_boundary"] = dict(payload["claim_boundary"])
        payload["claim_boundary"]["rt_core_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "rt_core_speedup_claim_authorized"):
            rt.validate_v3_m21_max_nearest_device_reduction_payload(payload)

    def test_report_and_pod_artifact_capture_m21_boundaries_if_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("max-nearest device-reduction bridge", report)
        self.assertIn("CuPy and Numba", report)
        self.assertIn("not a public speedup claim", report)
        self.assertIn("device query columns", report)
        if not EVIDENCE_JSON.exists():
            self.skipTest("M21 pod evidence JSON has not been generated on this checkout")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_v3_m21_max_nearest_device_reduction_payload(payload)
        self.assertTrue(validation["signature_match"])
        rows = {row["partner"]: row for row in payload["partner_rows"]}
        self.assertEqual({"cupy", "numba"}, set(rows))
        self.assertEqual(rows["cupy"]["validation_signature"], rows["numba"]["validation_signature"])
        for row in rows.values():
            self.assertTrue(row["prepared_query_columns_used"])
            self.assertTrue(row["prepared_output_columns_used"])
            self.assertTrue(row["device_query_columns_used"])
            self.assertTrue(row["device_output_columns_used"])
            self.assertFalse(row["host_query_upload_in_hot_window"])
            self.assertFalse(row["device_result_materialized_in_hot_window"])
            self.assertTrue(row["device_result_materialization_after_hot_window"])
            self.assertTrue(row["hot_no_hidden_column_copy_ready"])
            self.assertFalse(row["consumer_host_valid_count_check_used"])


def _classification() -> dict[str, object]:
    return rt.classify_no_hidden_copy_transfer_snapshot(
        _snapshot(),
        min_named_column_bytes=8192,
        measured_window="prepared_point_group_nearest_device_query_columns_to_partner_global_max_before_materialization",
        readiness_source="synthetic_m21_test",
    )


def _snapshot() -> dict[str, object]:
    return {
        "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
        "total_calls": 1,
        "total_bytes": 64,
        "host_to_device_calls": 1,
        "host_to_device_bytes": 64,
        "device_to_host_calls": 0,
        "device_to_host_bytes": 0,
        "device_to_device_calls": 0,
        "device_to_device_bytes": 0,
        "unknown_calls": 0,
        "unknown_bytes": 0,
    }


def _row(partner: str) -> dict[str, object]:
    classification = _classification()
    return {
        "partner": partner,
        "backend": "optix",
        "route": "prepared_point_group_nearest_device_query_columns_partner_global_max",
        "prepared_scene_used": True,
        "prepared_query_columns_used": True,
        "prepared_output_columns_used": True,
        "device_query_columns_used": True,
        "device_output_columns_used": True,
        "same_stream_or_default_stream_ordering_used": True,
        "host_query_upload_in_hot_window": False,
        "host_row_materialization_before_consumer": False,
        "device_result_materialized_in_hot_window": False,
        "device_result_materialization_after_hot_window": True,
        "consumer_host_valid_count_check_used": False,
        "validation_signature": (42, 99, 42, 123456789, 65536),
        "hot_device_run_samples_seconds": (0.001, 0.0012),
        "materialize_samples_seconds": (0.0001, 0.0002),
        "hot_device_run_seconds_median": 0.0011,
        "materialize_seconds_median": 0.00015,
        "transfer_counter_samples": (_snapshot(),),
        "transfer_counter_classifications": (classification,),
        "transfer_counter_classification": classification,
        "transfer_counter_summary": rt.summarize_no_hidden_copy_classifications((classification,)),
        "hot_transfer_counter_observed": True,
        "hot_no_hidden_column_copy_ready": True,
        "metadata": {
            "device_execution_metadata": {
                "device_query_columns_used": True,
                "device_output_columns_used": True,
                "host_query_upload_in_hot_window": False,
            },
            "materialization_metadata": {
                "result_materialization_after_device_window": True,
            },
        },
        "public_claim_authorized": False,
    }


def _synthetic_payload() -> dict[str, object]:
    return {
        "version": rt.V3_M21_MAX_NEAREST_DEVICE_REDUCTION_VERSION,
        "status": rt.V3_M21_MAX_NEAREST_DEVICE_REDUCTION_STATUS,
        "graph_id": rt.V3_M21_GRAPH_ID,
        "contract_key": rt.V3_M21_CONTRACT_KEY,
        "parameters": {
            "point_count": 65536,
            "query_count": 65536,
            "group_count": 4096,
            "group_axis": 64,
            "radius": 0.025,
            "warmups": 1,
            "repeats": 2,
            "partners": rt.V3_M21_PARTNERS,
        },
        "preparation": {
            "prepared_scene_used": True,
            "prepared_query_columns_used": True,
            "prepared_output_columns_used": True,
            "initial_host_to_device_upload_expected": True,
            "prepare_seconds": 0.1,
            "prepare_transfer_counter_snapshot": {},
        },
        "partner_rows": (_row("cupy"), _row("numba")),
        "comparison": {
            "signature_match": True,
            "partners": rt.V3_M21_PARTNERS,
            "device_query_columns_used": True,
            "device_output_columns_used": True,
            "hot_no_hidden_column_copy_ready": True,
            "device_result_materialization_after_hot_window": True,
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "paper_or_author_parity_claim_authorized": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
