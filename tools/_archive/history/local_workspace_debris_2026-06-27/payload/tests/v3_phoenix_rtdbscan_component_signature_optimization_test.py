from __future__ import annotations

import unittest
from pathlib import Path

from examples.current.research_benchmarks.rt_dbscan import (
    rtdl_rt_dbscan_benchmark_app as app,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"


class _FakeDeviceArray:
    def __init__(self, values):
        self._values = list(values)

    def copy_to_host(self):
        return self

    def tolist(self):
        return list(self._values)

    def __getitem__(self, index):
        return self._values[index]


class _FakeRunnerResult:
    def __init__(self, *, cache_hit: bool, measured_repeat_count: int = 1, retain_outputs: bool = False):
        output = {
            "columns": {
                "label_counts": _FakeDeviceArray([0, 2, 1]),
                "flag_true_count": _FakeDeviceArray([2]),
                "negative_label_count": _FakeDeviceArray([0]),
                "neighbor_counts": _FakeDeviceArray([2, 2, 1]),
            },
            "metadata": {
                "adapter": "fake_component_signature_runner_route",
                "partner": "numba",
                "internal_device_residency_between_rtdl_phases": True,
                "hot_path_host_materialization": False,
                "external_host_buffer_exposure_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
                "materializes_neighbor_rows": False,
                "materializes_component_labels": False,
            },
        }
        self.output = tuple(output for _ in range(measured_repeat_count)) if retain_outputs else output
        self._metadata = {
            "runtime_executed": True,
            "phoenix_v3_redesign_step": "step1_runtime_trunk_probe",
            "runtime_trunk_family": "fixed_radius_self_query_to_grouped_stream_component_signature_3d",
            "runtime_trunk_executes_end_to_end": True,
            "internal_device_residency_between_rtdl_phases": True,
            "hot_path_host_materialization": False,
            "external_device_buffer_interop_authorized": False,
            "v4_embedding_or_external_zero_copy_authorized": False,
            "focused_material_gain_required_before_all_app": True,
            "prepared_session": {"cache_hit": bool(cache_hit)},
            "repeated_prepared_session_execution": measured_repeat_count > 1,
            "measured_repeat_count": int(measured_repeat_count),
            "measured_repeat_seconds": tuple(0.02 for _ in range(measured_repeat_count)),
            "single_cache_lookup_for_measured_repeats": True,
            "single_report_after_measured_repeats": True,
            "prepared_execution_report": {
                "summary_sec": {
                    "setup": 0.01 if not cache_hit else 0.0,
                    "steady_state": 0.02,
                    "validation": 0.0,
                },
                "phase_timings": [
                    {"phase": "cache_load", "seconds": 0.0 if not cache_hit else 0.001},
                ],
            },
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        }

    def to_metadata(self):
        return dict(self._metadata)


class V3PhoenixRTDBSCANComponentSignatureOptimizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = APP.read_text(encoding="utf-8")

    def test_prepared_grid_column_signature_reuses_generic_numba_label_flag_count(self):
        self.assertIn("_cluster_signature_from_numba_label_columns", self.text)
        self.assertIn("rt.run_numba_label_count_and_flag_count_i64", self.text)
        self.assertIn("numba_label_count_and_flag_count_label_columns", self.text)
        self.assertIn("column_signature_uses_numba_label_count_and_flag_count", self.text)
        self.assertIn('"column_signature_materializes_point_ids": False', self.text)
        self.assertIn('"column_signature_materializes_core_flags": False', self.text)
        self.assertNotIn('"native_dbscan_abi_added": true', self.text)

    def test_grouped_stream_numba_column_signature_routes_through_productized_runner(self):
        self.assertIn("use_productized_runner = column_signature_mode and grouped_stream_partner == \"numba\"", self.text)
        self.assertIn("rt.make_prepared_input_fingerprint(point_rows_for_runner)", self.text)
        self.assertIn("rt.run_radius_graph_component_signature_3d_prepared_session", self.text)
        self.assertIn("point_rows_fingerprint=point_rows_fingerprint", self.text)
        self.assertIn("rt.ExplicitPreparedSessionCache(max_entries=1)", self.text)
        self.assertIn("measured_repeat_count=measured_repeat_count", self.text)
        self.assertIn("retain_repeat_outputs=True", self.text)
        self.assertIn('"prepared_execution_session_runner_used": True', self.text)
        self.assertIn('"productized_execution_path": "prepared_execution_session_runner"', self.text)
        self.assertIn('"prepared_execution_session_runner_runtime_executed_count"', self.text)
        self.assertIn('"runtime_trunk_executes_end_to_end_count"', self.text)
        self.assertIn('"internal_device_residency_between_rtdl_phases"', self.text)
        self.assertIn('"external_device_buffer_interop_authorized": False', self.text)
        self.assertIn('"prepared_execution_session_runner_measured_repeat_count"', self.text)
        self.assertIn('"prepared_execution_session_runner_repeated_execution"', self.text)
        self.assertIn('"prepared_execution_session_runner_cache_hit_count"', self.text)
        self.assertIn('"app_specific_native_engine_logic_allowed": False', self.text)
        self.assertNotIn("native_dbscan_abi_added = True", self.text)

    def test_grouped_stream_numba_column_signature_metadata_exposes_runner(self):
        calls = {"count": 0}
        original = app.rt.run_radius_graph_component_signature_3d_prepared_session

        def fake_runner(**kwargs):
            self.assertEqual(kwargs["partner"], "numba")
            self.assertEqual(kwargs["min_neighbors"], 3)
            self.assertIsNotNone(kwargs["cache"])
            self.assertIn("point_rows_fingerprint", kwargs)
            self.assertEqual(kwargs["point_rows_fingerprint"]["digest_algorithm"], "sha256")
            self.assertEqual(kwargs["warmup_count"], 0)
            self.assertEqual(kwargs["measured_repeat_count"], 3)
            self.assertTrue(kwargs["retain_repeat_outputs"])
            calls["count"] += 1
            return _FakeRunnerResult(
                cache_hit=calls["count"] > 1,
                measured_repeat_count=int(kwargs["measured_repeat_count"]),
                retain_outputs=bool(kwargs["retain_repeat_outputs"]),
            )

        app.rt.run_radius_graph_component_signature_3d_prepared_session = fake_runner
        try:
            payload = app.run_rt_dbscan_benchmark(
                mode="optix_rt_core_grouped_stream_numba_column_signature_3d",
                dataset="tiny",
                point_count=9,
                radius=0.20,
                min_neighbors=3,
                seed=20260519,
                partner="numba",
                include_rows=False,
                repeat=3,
                warmup=0,
                validate=False,
            )
        finally:
            app.rt.run_radius_graph_component_signature_3d_prepared_session = original

        metadata = payload["metadata"]
        self.assertEqual(calls["count"], 1)
        self.assertTrue(metadata["prepared_execution_session_runner_used"])
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(metadata["prepared_execution_session_runner_runtime_executed_count"], 1)
        self.assertEqual(metadata["phoenix_v3_redesign_step"], "step1_runtime_trunk_probe")
        self.assertEqual(
            metadata["runtime_trunk_family"],
            "fixed_radius_self_query_to_grouped_stream_component_signature_3d",
        )
        self.assertEqual(metadata["runtime_trunk_executes_end_to_end_count"], 1)
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertFalse(metadata["external_device_buffer_interop_authorized"])
        self.assertFalse(metadata["v4_embedding_or_external_zero_copy_authorized"])
        self.assertTrue(metadata["focused_material_gain_required_before_all_app"])
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertEqual(metadata["prepared_execution_session_runner_measured_repeat_count"], 3)
        self.assertTrue(metadata["prepared_execution_session_runner_repeated_execution"])
        self.assertTrue(metadata["prepared_execution_session_runner_single_cache_lookup_for_measured_repeats"])
        self.assertTrue(metadata["prepared_execution_session_runner_single_report_after_measured_repeats"])
        self.assertEqual(metadata["prepared_execution_session_runner_cache_hit_count"], 0)
        self.assertEqual(metadata["prepared_query_repeat_protocol"]["measured_run_count"], 3)
        self.assertEqual(metadata["column_signature_strategy"], "numba_direct_component_signature_counts")
        self.assertFalse(metadata["materializes_neighbor_rows"])
        self.assertFalse(metadata["materializes_python_rows"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
