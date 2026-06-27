from __future__ import annotations

import importlib.util
import py_compile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py"
APP_SIM = ROOT / "examples" / "current" / "apps" / "simulation" / "rtdl_barnes_hut_force_app.py"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
PREPARED_SESSION_RESIDENCY = ROOT / "src" / "rtdsl" / "prepared_session_residency.py"
RTDSL_INIT = ROOT / "src" / "rtdsl" / "__init__.py"


class V3PhoenixBarnesHutPreparedExecutionRunnerWiringTest(unittest.TestCase):
    def _load_app_module(self):
        module_name = "_phoenix_v3_m72_barnes_hut_benchmark_app_for_test"
        spec = importlib.util.spec_from_file_location(module_name, APP)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        previous = sys.modules.get(module_name)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            if previous is None:
                sys.modules.pop(module_name, None)
            else:
                sys.modules[module_name] = previous
        return module

    def test_app_wires_fused_vector_sum_to_productized_runner(self) -> None:
        source = APP.read_text(encoding="utf-8")

        for phrase in (
            '"prepared_execution_fused_vector_sum_numba_cuda"',
            '"native_fused_vector_sum_cuda_device"',
            "def _prepared_execution_fused_vector_sum_numba_cuda_payload",
            "def _native_fused_vector_sum_cuda_device_payload",
            "run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session",
            "prepared_execution_session_runner",
            "aggregate_tree_fused_weighted_vector_sum_2d",
            "explicit_numba_cuda_partner_force_interpretation",
            "native_cuda_device_resident_force_interpretation",
            '"runtime_trunk_executes_end_to_end"',
            '"internal_device_residency_between_rtdl_phases"',
            '"hot_path_host_materialization"',
            '"phoenix_v3_m72"',
            '"id": "set_a_barnes_hut_app_geomean_0_844x"',
            '"scorecard_blocker_bound"',
            '"scorecard_blocker_app"',
            '"scorecard_blocker_current_value"',
            '"scorecard_blocker_route_kind"',
            '"win_source"',
            '"m43_reuse_scope"',
            '"v4_embedding_or_external_zero_copy_authorized"',
            '"full_all_app_rerun_authorized_by_this_packet"',
        ):
            self.assertIn(phrase, source)

        self.assertIn('"app": "barnes_hut"', source)
        self.assertIn('"current_value": 0.844', source)
        self.assertIn('"route_kind": "trunk_fix_candidate"', source)
        self.assertIn('win_source="partner_continuation"', source)
        self.assertIn('win_source="kernel"', source)
        self.assertIn('partner="native_cuda"', source)
        self.assertIn('"optix_trace_used": False', source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"broad_v3_faster_than_v2_claim_authorized": False', source)
        self.assertIn('"true_zero_copy_claim_authorized": False', source)
        self.assertIn('"automatic_partner_selection_authorized": False', source)
        self.assertIn('"rt_core_speedup_claim_authorized": False', source)
        self.assertNotIn('"public_speedup_claim_authorized": True', source)
        self.assertNotIn('"true_zero_copy_claim_authorized": True', source)
        self.assertNotIn('"full_all_app_rerun_authorized_by_this_packet": True', source)

    def test_prepared_execution_mode_dispatches_to_runtime_runner_payload(self) -> None:
        module = self._load_app_module()
        calls: list[dict[str, object]] = []

        def fake_payload(**kwargs):
            calls.append(dict(kwargs))
            return {
                "boundary": "m72 dispatch stub",
                "stub_payload_reached": True,
            }

        original = module._prepared_execution_fused_vector_sum_numba_cuda_payload
        module._prepared_execution_fused_vector_sum_numba_cuda_payload = fake_payload
        try:
            payload = module.run_benchmark(
                "prepared_execution_fused_vector_sum_numba_cuda",
                body_count=17,
                theta=0.61,
                bucket_size=64,
                max_depth=19,
                skip_validation=True,
                query_repeat=5,
                warmup=2,
                force_output_mode="force_summary",
            )
        finally:
            module._prepared_execution_fused_vector_sum_numba_cuda_payload = original

        self.assertEqual(
            calls,
            [
                {
                    "body_count": 17,
                    "theta": 0.61,
                    "bucket_size": 64,
                    "max_depth": 19,
                    "skip_validation": True,
                    "query_repeat": 5,
                    "warmup": 2,
                    "force_output_mode": "force_summary",
                }
            ],
        )
        self.assertTrue(payload["stub_payload_reached"])
        self.assertEqual(payload["app_boundary"], "m72 dispatch stub")
        metadata = payload["benchmark_metadata"]
        self.assertEqual(metadata["mode"], "prepared_execution_fused_vector_sum_numba_cuda")
        self.assertIn("prepared_execution_session_runner", metadata["contract"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_native_device_mode_dispatches_and_rejects_rt_core_claim(self) -> None:
        module = self._load_app_module()
        calls: list[dict[str, object]] = []

        def fake_payload(**kwargs):
            calls.append(dict(kwargs))
            return {
                "boundary": "native m72 dispatch stub",
                "stub_payload_reached": True,
            }

        original = module._native_fused_vector_sum_cuda_device_payload
        module._native_fused_vector_sum_cuda_device_payload = fake_payload
        try:
            payload = module.run_benchmark(
                "native_fused_vector_sum_cuda_device",
                body_count=19,
                theta=0.62,
                bucket_size=16,
                max_depth=12,
                skip_validation=True,
                query_repeat=7,
                warmup=3,
                force_output_mode="force_summary",
            )
            with self.assertRaisesRegex(ValueError, "require-rt-core"):
                module.run_benchmark("native_fused_vector_sum_cuda_device", require_rt_core=True)
        finally:
            module._native_fused_vector_sum_cuda_device_payload = original

        self.assertEqual(
            calls,
            [
                {
                    "body_count": 19,
                    "theta": 0.62,
                    "bucket_size": 16,
                    "max_depth": 12,
                    "skip_validation": True,
                    "query_repeat": 7,
                    "warmup": 3,
                    "force_output_mode": "force_summary",
                }
            ],
        )
        self.assertTrue(payload["stub_payload_reached"])
        metadata = payload["benchmark_metadata"]
        self.assertEqual(metadata["mode"], "native_fused_vector_sum_cuda_device")
        self.assertIn("native_cuda_device_resident_force_interpretation", metadata["contract"])
        self.assertFalse(metadata["rt_core_accelerated"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_runtime_helper_is_generic_not_app_named(self) -> None:
        source = PREPARED_EXECUTION.read_text(encoding="utf-8")

        self.assertIn("def run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session", source)
        self.assertIn('primitive="aggregate_tree_fused_weighted_vector_sum_2d"', source)
        self.assertIn('"run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session"', source)
        helper_start = source.index("def run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session")
        helper_end = source.index("def describe_prepared_execution_user_pattern", helper_start)
        helper_body = source[helper_start:helper_end]
        self.assertNotIn("barnes", helper_body.lower())
        self.assertIn("native_cuda", helper_body)
        self.assertIn("runtime_trunk_executes_end_to_end", helper_body)
        self.assertIn("external_device_buffer_interop_authorized", helper_body)
        self.assertIn("focused_material_gain_required_before_all_app", helper_body)
        self.assertIn("full_all_app_rerun_authorized_by_this_packet", helper_body)

    def test_public_import_and_partner_backend_are_available(self) -> None:
        init_source = RTDSL_INIT.read_text(encoding="utf-8")
        residency_source = PREPARED_SESSION_RESIDENCY.read_text(encoding="utf-8")

        self.assertIn(
            "from .prepared_execution import run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session",
            init_source,
        )
        self.assertIn('"run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session"', init_source)
        self.assertIn('"partner"', residency_source)

    def test_node_coverage_uses_generic_prepared_query_points(self) -> None:
        source = APP_SIM.read_text(encoding="utf-8")

        self.assertIn("prepared.prepare_query_points(_body_points(bodies))", source)
        self.assertIn("prepared.count_threshold_reached(prepared_query_points", source)
        self.assertIn('"query_points_prepare_sec"', source)
        self.assertIn('"query_points_prepared_once": True', source)
        self.assertIn('"query_points_prepacked_by_caller": True', source)

    def test_modified_python_files_compile(self) -> None:
        py_compile.compile(str(APP), doraise=True)
        py_compile.compile(str(APP_SIM), doraise=True)
        py_compile.compile(str(PREPARED_EXECUTION), doraise=True)
        py_compile.compile(str(PREPARED_SESSION_RESIDENCY), doraise=True)
        py_compile.compile(str(RTDSL_INIT), doraise=True)


if __name__ == "__main__":
    unittest.main()
