from __future__ import annotations

from pathlib import Path
import importlib
import json
from unittest import mock
import unittest

import rtdsl as rt
from examples.benchmark_apps.rtnn import rtdl_rtnn_benchmark_app as app
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py"
MODULE = ROOT / "src/rtdsl/v3_0_m19_ranked_summary_bridge.py"
RUNNER = ROOT / "scripts/v3_0_m110_rtnn_chunked_bridge_measure.py"
PACKET = ROOT / "docs/reports/goal4506_v3_0_m110_rtnn_chunked_runtime_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4506_v3_0_m110_rtnn_chunked_runtime_2026-06-17.md"
RAW = ROOT / "docs/reports/goal4506_rtnn_chunked_uniform_1048576q1048576_w1r3_2026-06-17.json"
README = ROOT / "examples/benchmark_apps/rtnn/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4506V30M110RtnnChunkedRuntimeTest(unittest.TestCase):
    def test_m19_module_defines_chunked_runtime_without_replacing_single_graph(self) -> None:
        module = MODULE.read_text(encoding="utf-8")

        self.assertIn("run_v3_m19_ranked_summary_bridge_chunked_case", module)
        self.assertIn("validate_v3_m19_ranked_summary_bridge_chunked_payload", module)
        self.assertIn("prepared_scene_reused_across_chunks", module)
        self.assertIn("prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner_chunked", module)
        self.assertIn("run_v3_m19_ranked_summary_bridge_case", module)

    def test_chunked_validator_accepts_synthetic_payload_and_rejects_public_claim(self) -> None:
        payload = _synthetic_chunked_payload()
        validation = rt.validate_v3_m19_ranked_summary_bridge_chunked_payload(payload)

        self.assertEqual(rt.V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_STATUS, validation["status"])
        self.assertEqual(2, validation["partner_count"])
        self.assertEqual(2, validation["chunk_count"])
        self.assertTrue(validation["signature_match"])

        payload["claim_boundary"] = dict(payload["claim_boundary"])
        payload["claim_boundary"]["public_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "public_speedup"):
            rt.validate_v3_m19_ranked_summary_bridge_chunked_payload(payload)

    def test_app_exposes_chunked_runtime_mode_with_explicit_transfer_counter(self) -> None:
        chunked_payload = _synthetic_chunked_payload()
        with mock.patch.object(
            app.rt,
            "run_v3_m19_ranked_summary_bridge_chunked_case",
            return_value=chunked_payload,
        ) as run, mock.patch.object(
            app.rt,
            "validate_v3_m19_ranked_summary_bridge_chunked_payload",
            return_value={"signature_match": True, "partner_count": 2, "chunk_count": 2},
        ) as validate:
            payload = app.run_app(
                "prepared_ranked_summary_graph_partner_bridge_chunked",
                copies=131_072,
                query_count=131_072,
                distribution="uniform",
                warmups=1,
                repeats=3,
                transfer_counter_library="build/fake_counter.so",
                hardware="unit-test",
            )

        run.assert_called_once()
        self.assertEqual(131_072, run.call_args.kwargs["point_count"])
        self.assertEqual(131_072, run.call_args.kwargs["query_count"])
        self.assertEqual(1, run.call_args.kwargs["warmups"])
        self.assertEqual(3, run.call_args.kwargs["repeats"])
        validate.assert_called_once_with(chunked_payload)
        self.assertEqual("prepared_ranked_summary_graph_partner_bridge_chunked", payload["mode"])
        self.assertTrue(payload["claim_boundary"]["large_chunked_runtime_evidence"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_runner_uses_chunked_app_mode_and_transfer_counter_bootstrap(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        app_source = APP.read_text(encoding="utf-8")

        self.assertIn("prepared_ranked_summary_graph_partner_bridge_chunked", runner)
        self.assertIn("_ensure_transfer_counter_preloaded", runner)
        self.assertIn("_ensure_numba_toolchain_preexec", runner)
        self.assertIn("configure_numba_cuda_toolchain_environment", runner)
        self.assertIn("compact_summary", runner)
        self.assertIn("prepared_ranked_summary_graph_partner_bridge_chunked", app_source)
        self.assertIn("run_v3_m19_ranked_summary_bridge_chunked_case", app_source)

    def test_m110_report_packet_and_current_registry_capture_runtime_evidence(self) -> None:
        module = importlib.import_module("scripts.goal4506_m110_rtnn_chunked_runtime")
        packet = module.build_packet(ROOT)

        self.assertEqual("rtdl.v3_0.rtnn_chunked_runtime.goal4506.v1", packet["version"])
        self.assertEqual(16, packet["input"]["chunk_count"])
        self.assertEqual(1_048_576, packet["input"]["query_count"])
        self.assertTrue(packet["runtime"]["signature_match"])
        self.assertTrue(packet["runtime"]["hot_no_hidden_column_copy_ready"])
        self.assertLess(packet["runtime"]["cupy_hot_device_run_seconds_median_sum"], 0.09)
        self.assertLess(packet["runtime"]["numba_hot_device_run_seconds_median_sum"], 0.09)
        self.assertFalse(packet["claim_boundary"]["aggregate_only_full_batch_direct_comparison_authorized"])

        checked_in = json.loads(PACKET.read_text(encoding="utf-8"))
        raw = json.loads(RAW.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}["rtnn"]

        self.assertEqual("rtdl.v3_0.rtnn_chunked_runtime.goal4506.v1", checked_in["version"])
        self.assertEqual(16, raw["compact_summary"]["chunk_count"])
        self.assertIn("Goal4506", report)
        self.assertIn("0.082908s", report)
        self.assertIn("not aggregate-only full-batch direct evidence", report)
        self.assertIn("Goal4506", readme)
        self.assertIn("Goal4506 RTNN chunked partner runtime", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4507.v1", adequacy["version"])
        self.assertIn("Goal4506", route["evidence_refs"])
        self.assertIn("Goal4506", adequacy["evidence_refs"])
        self.assertIn("0.083s", route["current_reader_decision"])
        self.assertIn("prepared_ranked_summary_graph_partner_bridge_chunked", adequacy["current_recommended_path"])


def _chunk_row(partner: str, chunk_index: int) -> dict[str, object]:
    return {
        "partner": partner,
        "backend": "optix",
        "route": "prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner",
        "chunk_index": chunk_index,
        "query_start_inclusive": chunk_index * 65_536,
        "query_end_exclusive": (chunk_index + 1) * 65_536,
        "prepared_scene_used": True,
        "prepared_query_points_used": True,
        "cuda_graph_replay_used": True,
        "same_stream_partner_device_reduction_used": True,
        "device_resident_partial_rows_for_partner": True,
        "host_scalar_read_before_consumer": False,
        "host_partial_materialization_before_consumer": False,
        "device_result_materialized_in_hot_window": False,
        "device_result_materialization_after_hot_window": True,
        "validation_signature": ((65_536, 100 + chunk_index, 200, 300, 400),),
        "hot_device_run_seconds_median": 0.001 + chunk_index * 0.0001,
        "materialize_seconds_median": 0.0001,
        "hot_no_hidden_column_copy_ready": True,
        "public_claim_authorized": False,
    }


def _partner_row(partner: str) -> dict[str, object]:
    rows = (_chunk_row(partner, 0), _chunk_row(partner, 1))
    return {
        "partner": partner,
        "backend": "optix",
        "route": "prepared_fixed_radius_ranked_summary_graph_partials_same_stream_partner_chunked",
        "chunk_count": 2,
        "chunk_rows": rows,
        "prepared_scene_reused_across_chunks": True,
        "prepared_query_points_per_chunk": True,
        "cuda_graph_per_chunk": True,
        "same_stream_partner_device_reduction_per_chunk": True,
        "device_resident_partial_rows_for_partner": True,
        "host_scalar_read_before_consumer": False,
        "host_partial_materialization_before_consumer": False,
        "device_result_materialized_in_hot_window": False,
        "device_result_materialization_after_hot_window": True,
        "combined_validation_signature": ((131_072, 201, 400, 600, 800),),
        "chunk_hot_device_run_seconds_medians": (0.001, 0.0011),
        "chunk_materialize_seconds_medians": (0.0001, 0.0001),
        "hot_device_run_seconds_median_sum": 0.0021,
        "materialize_seconds_median_sum": 0.0002,
        "hot_no_hidden_column_copy_ready": True,
        "public_claim_authorized": False,
    }


def _synthetic_chunked_payload() -> dict[str, object]:
    plan = rt.plan_v3_m19_ranked_summary_bridge_chunks(
        point_count=131_072,
        query_count=131_072,
        max_query_count=65_536,
        distribution="uniform",
    )
    return {
        "version": rt.V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_VERSION,
        "status": rt.V3_M19_CHUNKED_RANKED_SUMMARY_BRIDGE_STATUS,
        "graph_id": rt.V3_M19_GRAPH_ID,
        "contract_key": rt.V3_M19_CONTRACT_KEY,
        "parameters": {
            "point_count": 131_072,
            "query_count": 131_072,
            "distribution": "uniform",
            "request_count": 1,
            "max_query_count": 65_536,
            "chunk_count": 2,
            "warmups": 1,
            "repeats": 3,
        },
        "execution_path_plan": plan,
        "preparation": {
            "prepared_scene_used": True,
            "prepared_scene_reused_across_chunks": True,
            "prepared_query_points_per_chunk": True,
            "cuda_graph_per_chunk": True,
            "initial_host_to_device_upload_expected": True,
            "chunk_preparation_rows": (),
        },
        "partner_rows": (_partner_row("cupy"), _partner_row("numba")),
        "comparison": {
            "signature_match": True,
            "partners": rt.V3_M19_PARTNERS,
            "chunk_count": 2,
            "chunked_runtime_executed": True,
            "hot_no_hidden_column_copy_ready": True,
            "device_result_materialization_after_hot_window": True,
            "prepared_scene_reused_across_chunks": True,
            "cuda_graph_per_chunk": True,
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "large_chunked_runtime_evidence": True,
        },
    }


if __name__ == "__main__":
    unittest.main()
