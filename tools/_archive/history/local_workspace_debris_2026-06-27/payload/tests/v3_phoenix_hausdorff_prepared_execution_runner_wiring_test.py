from __future__ import annotations

import inspect
import unittest
from unittest import mock

from examples import rtdl_hausdorff_distance_app as app
from rtdsl.prepared_execution import PREPARED_EXECUTION_SESSION_RUNNER_STATUS
from rtdsl.prepared_execution import PREPARED_EXECUTION_SESSION_RUNNER_VERSION
from rtdsl.prepared_execution import PreparedExecutionSessionResult
from rtdsl.prepared_execution import run_fixed_radius_threshold_reached_count_2d_prepared_session


def _fake_threshold_runner_result(*, query_count: int, repeat: int, warmup: int) -> PreparedExecutionSessionResult:
    outputs = tuple(
        {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "threshold_reached_count": query_count,
            "native_scalar_count_used": True,
            "threshold_summary_rows_materialized_on_host": False,
            "hot_path_host_materialization": False,
            "prepared_search_structure_resident_between_rtdl_phases": True,
            "query_points_device_resident_between_rtdl_phases": False,
            "internal_device_residency_between_rtdl_phases": True,
            "internal_residency_scope": "prepared_search_structure_only_query_points_not_device_resident",
            "run_phases": {
                "query_fixed_radius_threshold_reached_count_sec": 0.001,
            },
        }
        for _ in range(repeat)
    )
    metadata = {
        "schema": PREPARED_EXECUTION_SESSION_RUNNER_VERSION,
        "status": PREPARED_EXECUTION_SESSION_RUNNER_STATUS,
        "runtime_executed": True,
        "productized_execution_path": "prepared_execution_session_runner",
        "prepared_session": {"cache_hit": False},
        "prepared_execution_report": {
            "summary_sec": {"setup": 0.001},
            "phase_timings": [
                {"phase": "warmup", "repeat_seconds": [0.0005 for _ in range(warmup)]},
            ],
        },
        "prepared_execution_report_validation": {"status": "accept"},
        "outer_prepare_sec": 0.0015,
        "outer_cache_load_sec": 0.0,
        "native_prepare_sec": 0.0009,
        "legacy_aligned_prepare_sec": 0.0009,
        "measured_repeat_seconds": tuple(0.002 for _ in range(repeat)),
        "measured_repeat_count": repeat,
        "output_finalize_sec": 0.0,
        "runtime_trunk_executes_end_to_end": True,
        "material_probe_repeat_requirement_met": repeat >= 5,
        "repeat5_material_probe_candidate": repeat >= 5,
        "native_scalar_count_used": True,
        "threshold_summary_rows_materialized_on_host": False,
        "hot_path_host_materialization": False,
        "prepared_search_structure_resident_between_rtdl_phases": True,
        "query_points_device_resident_between_rtdl_phases": False,
        "internal_device_residency_between_rtdl_phases": True,
        "internal_residency_scope": "prepared_search_structure_only_query_points_not_device_resident",
        "large_input_fingerprint_hot_path_avoided": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
    }
    return PreparedExecutionSessionResult(
        prepared_value=object(),
        output=outputs,
        validation_output=None,
        metadata=metadata,
    )


class V3PhoenixHausdorffPreparedExecutionRunnerWiringTest(unittest.TestCase):
    def test_runner_mode_routes_both_directed_legs_through_productized_helper(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_runner(**kwargs):
            calls.append(dict(kwargs))
            return _fake_threshold_runner_result(
                query_count=len(tuple(kwargs["query_points"])),
                repeat=int(kwargs["measured_repeat_count"]),
                warmup=int(kwargs["warmup_count"]),
            )

        with mock.patch.object(
            app.rt,
            "run_fixed_radius_threshold_reached_count_2d_prepared_session",
            side_effect=fake_runner,
        ):
            payload = app.run_app(
                "optix",
                copies=1,
                optix_summary_mode="directed_threshold_prepared_runner",
                hausdorff_threshold=0.4,
                require_rt_core=True,
                query_repeat=5,
                warmup=1,
            )

        self.assertEqual(len(calls), 2)
        self.assertTrue(all(call["backend"] == "optix" for call in calls))
        self.assertTrue(all(call["partner"] == "none" for call in calls))
        self.assertTrue(all(call["require_repeat5_material_probe"] for call in calls))
        self.assertTrue(all(call["retain_repeat_outputs"] for call in calls))
        self.assertTrue(all(call["search_fingerprint"] for call in calls))
        self.assertTrue(all(call["query_fingerprint"] for call in calls))
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(
            payload["directed_a_to_b"]["run_phases"]["query_fixed_radius_threshold_reached_count_sec"],
            0.001,
        )
        self.assertEqual(payload["directed_a_to_b"]["run_phases"]["scene_prepare_sec"], 0.0009)
        self.assertEqual(payload["directed_a_to_b"]["run_phases"]["runner_outer_prepare_sec"], 0.0015)
        self.assertEqual(payload["run_phases"]["runner_native_prepare_sec"], 0.0018)
        self.assertEqual(payload["run_phases"]["runner_outer_prepare_sec"], 0.003)
        self.assertEqual(payload["directed_a_to_b"]["run_phases"]["runner_outer_query_sec"], 0.002)
        self.assertEqual(payload["run_phases"]["runner_outer_query_sec"], 0.004)
        self.assertEqual(
            payload["directed_a_to_b"]["query_repeat_protocol"]["reported_query_metric"],
            "inner_primitive_query_median_with_runner_outer_metric_disclosed",
        )
        self.assertEqual(
            payload["directed_a_to_b"]["query_repeat_protocol"]["reported_prepare_metric"],
            "legacy_aligned_native_prepare_with_runner_outer_metric_disclosed",
        )
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count_prepared_execution_runner")
        runner = payload["prepared_execution_session_runner"]
        self.assertTrue(runner["used"])
        self.assertEqual(runner["productized_execution_path"], "prepared_execution_session_runner")
        self.assertTrue(runner["both_directed_legs_runtime_executed"])
        self.assertEqual(runner["runtime_executed_count"], 2)
        self.assertTrue(runner["both_directed_legs_runtime_trunk_end_to_end"])
        self.assertTrue(runner["both_directed_legs_no_threshold_rows_materialized_on_host"])
        self.assertTrue(runner["both_directed_legs_internal_device_residency_between_rtdl_phases"])
        self.assertIn("prepared_execution_report_validation", runner["directed_a_to_b"])
        self.assertIn("output_finalize_sec", runner["directed_a_to_b"])
        self.assertFalse(runner["release_authorized"])
        self.assertFalse(runner["all_app_rerun_authorized"])
        self.assertFalse(runner["public_speedup_claim_authorized"])
        self.assertFalse(runner["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(runner["whole_hausdorff_speedup_claim_authorized"])
        self.assertFalse(runner["true_zero_copy_claim_authorized"])
        self.assertFalse(runner["v4_external_buffer_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_hausdorff_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["all_app_rerun_authorized"])

    def test_runner_mode_is_exposed_without_erasing_legacy_mode(self) -> None:
        source = inspect.getsource(app.main)

        self.assertIn("directed_threshold_prepared", source)
        self.assertIn("directed_threshold_prepared", app.DIRECTED_THRESHOLD_PREPARED_MODES)
        self.assertIn("directed_threshold_prepared_runner", app.DIRECTED_THRESHOLD_PREPARED_MODES)

    def test_generic_threshold_runner_helper_is_app_name_free(self) -> None:
        source = inspect.getsource(run_fixed_radius_threshold_reached_count_2d_prepared_session)

        self.assertNotIn("hausdorff", source.lower())
        self.assertIn("fixed_radius_threshold_reached_count_2d", source)
        self.assertIn("prepared_execution_session_runner", source)


if __name__ == "__main__":
    unittest.main()
