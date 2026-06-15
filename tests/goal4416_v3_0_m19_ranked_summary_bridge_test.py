from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
MODULE = ROOT / "src/rtdsl/v3_0_m19_ranked_summary_bridge.py"
RUNNER = ROOT / "scripts/v3_0_m19_ranked_summary_bridge_measure.py"
REPORT = ROOT / "docs/reports/goal4416_v3_0_m19_ranked_summary_bridge_2026-06-15.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4416_v3_0_m19_ranked_summary_bridge_uniform_65536_2026-06-15.json"
)


class Goal4416V30M19RankedSummaryBridgeTest(unittest.TestCase):
    def test_runtime_splits_device_reduction_from_materialization_for_cupy_and_numba(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("_OptixFixedRadiusRankedSummaryAggregateDeviceResult3D", runtime)
        self.assertIn("replay_same_stream_device_partials_summary_cupy_device", runtime)
        self.assertIn("replay_same_stream_device_partials_summary_numba_device", runtime)
        self.assertIn("_run_fixed_radius_graph_partials_same_stream_summary_cupy_device", runtime)
        self.assertIn("_run_fixed_radius_graph_partials_same_stream_summary_numba_device", runtime)
        self.assertIn("cp.cuda.ExternalStream(int(cuda_stream_ptr))", runtime)
        self.assertIn("cuda.external_stream(int(cuda_stream_ptr))", runtime)
        self.assertIn("DeviceNDArray", runtime)
        self.assertIn('"result_materialization_after_device_window": True', runtime)
        self.assertIn('"host_partial_materialization_before_consumer": False', runtime)

    def test_m19_module_and_runner_define_benchmark_shaped_two_partner_bridge(self) -> None:
        module = MODULE.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('V3_M19_PARTNERS = ("cupy", "numba")', module)
        self.assertIn("prepared_ranked_summary_graph_partner_bridge", module)
        self.assertIn("point_count: int = 65_536", module)
        self.assertIn("prepared_scene_and_query_resident_before_hot_window", module)
        self.assertIn("initial_host_to_device_upload_expected", module)
        self.assertIn("device_result_materialization_after_hot_window", module)
        self.assertIn("make_v3_m19_ranked_summary_points", module)
        self.assertIn("LD_PRELOAD", runner)
        self.assertIn("--numba-cuda-home", runner)
        self.assertIn("runner_numba_cuda_home", runner)
        self.assertIn("run_v3_m19_ranked_summary_bridge_case", runner)

    def test_validator_accepts_synthetic_m19_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m19_ranked_summary_bridge_payload(payload)
        self.assertEqual(2, validation["partner_count"])
        self.assertTrue(validation["signature_match"])
        self.assertTrue(validation["hot_no_hidden_column_copy_ready"])

    def test_validator_rejects_hot_window_materialization(self) -> None:
        payload = _synthetic_payload()
        rows = [dict(row) for row in payload["partner_rows"]]
        rows[0]["device_result_materialized_in_hot_window"] = True
        payload["partner_rows"] = tuple(rows)
        with self.assertRaisesRegex(GraphValidationError, "materialized_in_hot_window"):
            rt.validate_v3_m19_ranked_summary_bridge_payload(payload)

    def test_validator_rejects_public_speedup_claim(self) -> None:
        payload = _synthetic_payload()
        payload["claim_boundary"] = dict(payload["claim_boundary"])
        payload["claim_boundary"]["public_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "public_speedup"):
            rt.validate_v3_m19_ranked_summary_bridge_payload(payload)

    def test_report_and_pod_artifact_capture_m19_boundaries(self) -> None:
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_v3_m19_ranked_summary_bridge_payload(payload)
        self.assertTrue(validation["signature_match"])
        self.assertEqual(2, validation["partner_count"])
        rows = {row["partner"]: row for row in payload["partner_rows"]}
        self.assertEqual({"cupy", "numba"}, set(rows))
        self.assertEqual(rows["cupy"]["validation_signature"], rows["numba"]["validation_signature"])
        self.assertTrue(payload["preparation"]["initial_host_to_device_upload_expected"])
        for row in rows.values():
            self.assertTrue(row["cuda_graph_replay_used"])
            self.assertTrue(row["same_stream_partner_device_reduction_used"])
            self.assertTrue(row["hot_no_hidden_column_copy_ready"])
            self.assertFalse(row["device_result_materialized_in_hot_window"])
            self.assertTrue(row["device_result_materialization_after_hot_window"])
            classification = row["transfer_counter_classification"]
            self.assertEqual(0, int(classification["observed_device_to_host_calls"]))
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("RTNN ranked-summary bridge", report)
        self.assertIn("CuPy and Numba", report)
        self.assertIn("hot device window", report)
        self.assertIn("not a public speedup claim", report)


def _classification() -> dict[str, object]:
    return rt.classify_no_hidden_copy_transfer_snapshot(
        {
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
        },
        min_named_column_bytes=8192,
        measured_window=(
            "prepared_ranked_summary_graph_device_partials_to_partner_device_"
            "aggregate_before_materialization"
        ),
        readiness_source="synthetic_m19_test",
    )


def _row(partner: str) -> dict[str, object]:
    classification = _classification()
    signature = ((65536, 1000, 123, 456, 789000), (65536, 2000, 234, 567, 890000))
    return {
        "partner": partner,
        "backend": "optix",
        "route": "prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner",
        "prepared_scene_used": True,
        "prepared_query_points_used": True,
        "cuda_graph_replay_used": True,
        "same_stream_partner_device_reduction_used": True,
        "device_resident_partial_rows_for_partner": True,
        "host_scalar_read_before_consumer": False,
        "host_partial_materialization_before_consumer": False,
        "device_result_materialized_in_hot_window": False,
        "device_result_materialization_after_hot_window": True,
        "validation_signature": signature,
        "hot_device_run_samples_seconds": (0.001, 0.0011),
        "materialize_samples_seconds": (0.0001, 0.0002),
        "hot_device_run_seconds_median": 0.00105,
        "materialize_seconds_median": 0.00015,
        "transfer_counter_classification": classification,
        "transfer_counter_summary": rt.summarize_no_hidden_copy_classifications((classification,)),
        "hot_transfer_counter_observed": True,
        "hot_no_hidden_column_copy_ready": True,
        "metadata": {
            "device_execution_metadata": {
                "device_resident_partial_rows_for_partner": True,
                "host_partial_materialization_before_consumer": False,
            },
            "materialization_metadata": {
                "result_materialization_after_device_window": True,
            },
        },
        "public_claim_authorized": False,
    }


def _synthetic_payload() -> dict[str, object]:
    return {
        "version": rt.V3_M19_RANKED_SUMMARY_BRIDGE_VERSION,
        "status": rt.V3_M19_RANKED_SUMMARY_BRIDGE_STATUS,
        "graph_id": rt.V3_M19_GRAPH_ID,
        "contract_key": rt.V3_M19_CONTRACT_KEY,
        "parameters": {
            "point_count": 65536,
            "query_count": 65536,
            "distribution": "uniform",
            "requests": ({"radius": 0.02, "k_max": 50},),
            "request_count": 1,
            "warmups": 1,
            "repeats": 2,
        },
        "preparation": {
            "prepared_scene_used": True,
            "prepared_query_points_used": True,
            "cuda_graph_prepared": True,
            "prepared_scene_and_query_resident_before_hot_window": True,
            "initial_host_to_device_upload_expected": True,
            "prepare_seconds": 0.01,
            "prepare_transfer_counter_snapshot": {},
        },
        "partner_rows": (_row("cupy"), _row("numba")),
        "comparison": {
            "signature_match": True,
            "partners": rt.V3_M19_PARTNERS,
            "hot_no_hidden_column_copy_ready": True,
            "device_result_materialization_after_hot_window": True,
            "prepared_graph_reused_for_both_partners": True,
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
