from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_ray_triangle as rt_v4

OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"


class V4RayTriangleDeviceArrayApiTest(unittest.TestCase):
    def test_claim_boundary_distinguishes_measured_and_unmeasured_partners(self) -> None:
        torch_boundary = rt_v4.closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4("torch")
        cupy_boundary = rt_v4.closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4("cupy")

        self.assertEqual("v4_closest_hit_grouped_argmin_3d_device_arrays", torch_boundary["v4_api_surface"])
        self.assertTrue(torch_boundary["measured_partner"])
        self.assertEqual("measured_on_v4_section8_pod", torch_boundary["partner_claim_status"])
        self.assertFalse(cupy_boundary["measured_partner"])
        self.assertEqual("declared_unmeasured_not_performance_ready", cupy_boundary["partner_claim_status"])
        self.assertFalse(torch_boundary["release_claim_authorized"])
        self.assertFalse(torch_boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(torch_boundary["tier3_callback_claim_authorized"])

    def test_any_hit_claim_boundary_distinguishes_measured_and_unmeasured_partners(self) -> None:
        torch_boundary = rt_v4.ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4("torch")
        cupy_boundary = rt_v4.ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4("cupy")

        self.assertEqual("v4_ray_triangle_any_hit_flags_2d_device_arrays", torch_boundary["v4_api_surface"])
        self.assertTrue(torch_boundary["measured_partner"])
        self.assertEqual("measured_on_v4_section8_pod", torch_boundary["partner_claim_status"])
        self.assertFalse(cupy_boundary["measured_partner"])
        self.assertEqual("declared_unmeasured_not_performance_ready", cupy_boundary["partner_claim_status"])
        self.assertFalse(torch_boundary["release_claim_authorized"])
        self.assertFalse(torch_boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(torch_boundary["tier3_callback_claim_authorized"])

    def test_grouped_i64_claim_boundary_is_measured_with_optix8_scope(self) -> None:
        torch_boundary = rt_v4.primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4("torch")
        cupy_boundary = rt_v4.primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4("cupy")

        self.assertEqual(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            torch_boundary["v4_api_surface"],
        )
        self.assertTrue(torch_boundary["measured_partner"])
        self.assertEqual(("torch",), torch_boundary["measured_partners"])
        self.assertEqual(("cupy",), torch_boundary["partner_support_declared_unmeasured"])
        self.assertEqual(
            "measured_on_v4_goal4617_pod_optix8",
            torch_boundary["partner_claim_status"],
        )
        self.assertEqual("8.0", torch_boundary["validated_optix_abi"])
        self.assertFalse(torch_boundary["optix_9_1_validated"])
        self.assertFalse(cupy_boundary["measured_partner"])
        self.assertEqual("declared_unmeasured_not_performance_ready", cupy_boundary["partner_claim_status"])
        self.assertFalse(torch_boundary["release_claim_authorized"])
        self.assertFalse(torch_boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(torch_boundary["tier3_callback_claim_authorized"])

    def test_weighted_sum_claim_boundary_is_measured_for_torch_only(self) -> None:
        torch_boundary = rt_v4.ray_triangle_any_hit_weighted_sum_3d_device_array_claim_boundary_v4("torch")
        cupy_boundary = rt_v4.ray_triangle_any_hit_weighted_sum_3d_device_array_claim_boundary_v4("cupy")

        self.assertEqual(
            "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            torch_boundary["v4_api_surface"],
        )
        self.assertTrue(torch_boundary["measured_partner"])
        self.assertEqual(("torch",), torch_boundary["measured_partners"])
        self.assertEqual((), torch_boundary["pod_candidate_partners"])
        self.assertEqual("tier2_measured_pod_validated_not_release", torch_boundary["surface_status"])
        self.assertEqual("measured_on_v4_goal4633_pod_optix8", torch_boundary["partner_claim_status"])
        self.assertEqual("same_operator_comparable_route", torch_boundary["comparison_class"])
        self.assertEqual("largest_shape_barely_clears_1_20x_floor_not_large_speedup", torch_boundary["performance_caveat"])
        self.assertEqual(
            "caller_initiated_v4_prepare_static_triangle_scene_from_device_triangle_columns",
            torch_boundary["scene_preparation_ownership"],
        )
        self.assertEqual("rtdl_allocated_uint64_device_scalar", torch_boundary["output_scalar_primary_allocation"])
        self.assertFalse(torch_boundary["true_zero_copy_authorized"])
        self.assertFalse(torch_boundary["release_claim_authorized"])
        self.assertFalse(torch_boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(torch_boundary["tier3_callback_claim_authorized"])
        self.assertFalse(cupy_boundary["measured_partner"])
        self.assertEqual("declared_unmeasured_not_performance_ready", cupy_boundary["partner_claim_status"])

    def test_session_run_uses_device_hot_path_and_device_output_copy_metadata(self) -> None:
        output_columns = {
            "group_has_value": object(),
            "group_index": object(),
            "group_value": object(),
        }
        scene = _FakeScene()
        grouped = _FakeGrouped()
        session = rt_v4.V4ClosestHitGroupedArgmin3DDeviceArraySession(
            prepared_scene=scene,
            ray_batch=_FakeRayBatch(),
            grouped_inputs=grouped,
            partner="torch",
            group_count=3,
        )
        session._output_handoff_cache_key = (
            id(output_columns["group_has_value"]),
            id(output_columns["group_index"]),
            id(output_columns["group_value"]),
        )
        session._output_handoff_cache = {"prevalidated": object()}

        result = session.run(output_columns=output_columns)

        self.assertIs(result["columns"], output_columns)
        metadata = result["metadata"]
        self.assertEqual("v4_closest_hit_grouped_argmin_3d_device_arrays", metadata["adapter"])
        self.assertEqual("CLOSEST_HIT_GROUPED_ARGMIN_3D", metadata["generic_primitive"])
        self.assertTrue(metadata["native_device_grouped_argmin"])
        self.assertTrue(metadata["native_direct_device_output_columns"])
        self.assertFalse(metadata["grouped_result_device_to_device_export"])
        self.assertFalse(metadata["grouped_results_downloaded_to_host_in_hot_path"])
        self.assertFalse(metadata["host_materialization_in_hot_path"])
        self.assertEqual(1, scene.run_calls)
        self.assertEqual(1, scene.prevalidated_handoff_calls)
        self.assertEqual(0, grouped.copy_calls)

    def test_any_hit_session_run_uses_device_flags_hot_path(self) -> None:
        output_flags = object()
        scene = _FakeAnyHitScene()
        session = rt_v4.V4RayTriangleAnyHitFlags2DDeviceArraySession(
            prepared_scene=scene,
            partner="torch",
        )

        result = session.run(
            {"ids": _FakeShapeColumn(4), "ox": object(), "oy": object(), "dx": object(), "dy": object(), "tmax": object()},
            output_flags=output_flags,
        )

        self.assertIs(result["columns"]["any_hit_flags"], output_flags)
        metadata = result["metadata"]
        self.assertEqual("v4_ray_triangle_any_hit_flags_2d_device_arrays", metadata["adapter"])
        self.assertEqual("RAY_TRIANGLE_ANY_HIT_FLAGS_2D", metadata["generic_primitive"])
        self.assertTrue(metadata["native_direct_device_output_columns"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["ray_results_downloaded_to_host_in_hot_path"])
        self.assertFalse(metadata["host_materialization_in_hot_path"])
        self.assertFalse(metadata["release_claim_authorized"])
        self.assertEqual(1, scene.flag_calls)

    def test_grouped_i64_session_uses_direct_device_output_hot_path(self) -> None:
        output_columns = {
            "group_counts": object(),
            "group_sums": object(),
            "group_mins": object(),
            "group_maxs": object(),
        }
        scene = _FakeScene()
        payload = _FakePrimitivePayload()
        session = rt_v4.V4PrimitiveGroupedI64Reduction3DDeviceArraySession(
            prepared_scene=scene,
            ray_batch=_FakeRayBatch(),
            primitive_payload=payload,
            partner="torch",
            group_count=3,
        )
        session._output_handoff_cache_key = (
            id(output_columns["group_counts"]),
            id(output_columns["group_sums"]),
            id(output_columns["group_mins"]),
            id(output_columns["group_maxs"]),
        )
        session._output_handoff_cache = {"prevalidated": object()}

        result = session.run(reduction="sum", output_columns=output_columns)

        self.assertIs(result["columns"], output_columns)
        metadata = result["metadata"]
        self.assertEqual(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            metadata["adapter"],
        )
        self.assertEqual("RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D", metadata["generic_primitive"])
        self.assertTrue(metadata["native_direct_device_output_columns"])
        self.assertFalse(metadata["group_rows_downloaded_to_host_in_hot_path"])
        self.assertFalse(metadata["host_materialization_in_hot_path"])
        self.assertEqual(1, scene.grouped_i64_device_output_calls)
        self.assertEqual(1, scene.prevalidated_grouped_i64_handoff_calls)

    def test_weighted_sum_session_uses_device_output_executor_hot_path(self) -> None:
        output_scalar = object()
        scene = _FakeWeightedSumScene()
        session = rt_v4.V4RayTriangleAnyHitWeightedSum3DDeviceArraySession(
            prepared_scene=scene,
            ray_batch=_FakeRayBatch(),
            ray_weights=object(),
            partner="torch",
        )

        result = session.run(output_scalar=output_scalar, cuda_stream=7)

        self.assertIs(result["columns"]["weighted_hit_sum"], output_scalar)
        metadata = result["metadata"]
        self.assertEqual("v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays", metadata["adapter"])
        self.assertEqual("RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_3D", metadata["generic_primitive"])
        self.assertEqual("tier2_measured_pod_validated_not_release", metadata["surface_status"])
        self.assertTrue(metadata["device_output_used"])
        self.assertTrue(metadata["native_direct_device_output_scalar"])
        self.assertFalse(metadata["host_scalar_read_before_consumer"])
        self.assertFalse(metadata["host_materialization_in_hot_path"])
        self.assertFalse(metadata["weighted_sum_downloaded_to_host_in_hot_path"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertEqual("caller_supplied_override", metadata["output_scalar_allocation"])
        self.assertEqual(
            "caller_initiated_v4_prepare_static_triangle_scene_from_device_triangle_columns",
            metadata["scene_preparation_ownership"],
        )
        self.assertEqual(1, scene.executor_prepare_calls)
        self.assertEqual(1, scene.executor.launch_calls)

    def test_prepare_closes_scene_when_ray_prepare_fails(self) -> None:
        original_prepare = rt_v4.prepare_optix_static_triangle_scene_3d_device_triangles
        fake_scene = _FailingPrepareScene()
        try:
            rt_v4.prepare_optix_static_triangle_scene_3d_device_triangles = lambda _columns: fake_scene
            with self.assertRaisesRegex(RuntimeError, "ray prepare failed"):
                rt_v4.prepare_closest_hit_grouped_argmin_3d_device_arrays_v4(
                    {"ids": object()},
                    {"ids": object()},
                    per_ray_group_ids=object(),
                    candidate_values=object(),
                    candidate_indices=object(),
                    group_count=1,
                )
        finally:
            rt_v4.prepare_optix_static_triangle_scene_3d_device_triangles = original_prepare
        self.assertTrue(fake_scene.closed)

    def test_prepare_any_hit_wraps_zero_copy_triangle_scene(self) -> None:
        original_prepare = rt_v4.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene
        fake_scene = _FakeAnyHitScene()
        try:
            rt_v4.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene = (
                lambda triangle_columns, triangle_aabbs: fake_scene
            )
            session = rt_v4.prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(
                {"ids": object()},
                object(),
                partner="torch",
            )
        finally:
            rt_v4.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene = original_prepare
        self.assertIs(session.prepared_scene, fake_scene)
        session.close()
        self.assertTrue(fake_scene.closed)

    def test_prepare_weighted_sum_closes_scene_when_ray_prepare_fails(self) -> None:
        original_prepare = rt_v4.prepare_optix_static_triangle_scene_3d_device_triangles
        fake_scene = _FailingPrepareScene()
        try:
            rt_v4.prepare_optix_static_triangle_scene_3d_device_triangles = lambda _columns: fake_scene
            with self.assertRaisesRegex(RuntimeError, "ray prepare failed"):
                rt_v4.prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4(
                    {"ids": object()},
                    {"ids": object()},
                    object(),
                    partner="torch",
                )
        finally:
            rt_v4.prepare_optix_static_triangle_scene_3d_device_triangles = original_prepare
        self.assertTrue(fake_scene.closed)

    def test_native_device_output_symbols_are_wired(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        direct_symbol = (
            "rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_"
            "prepared_grouped_argmin_device_outputs"
        )
        copy_symbol = "rtdl_optix_closest_hit_grouped_argmin_inputs_3d_copy_device_outputs"
        self.assertIn(direct_symbol, runtime)
        self.assertIn(direct_symbol, prelude)
        self.assertIn(direct_symbol, api)
        self.assertIn(copy_symbol, runtime)
        self.assertIn("copy_prepared_closest_hit_grouped_argmin_3d_device_outputs_optix", workloads)
        self.assertIn("cuMemcpyDtoD", workloads)
        self.assertIn("ray_closest_hit_prepared_grouped_argmin_device_outputs", runtime)
        self.assertIn("copy_grouped_results_to_device_outputs", runtime)

    def test_any_hit_device_output_symbols_are_wired(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        prepare_symbol = "rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs"
        flag_symbol = "rtdl_optix_write_prepared_ray_anyhit_2d_device_flags"
        self.assertIn(prepare_symbol, runtime)
        self.assertIn(prepare_symbol, prelude)
        self.assertIn(prepare_symbol, api)
        self.assertIn(flag_symbol, runtime)
        self.assertIn(flag_symbol, prelude)
        self.assertIn(flag_symbol, api)
        self.assertIn("write_prepared_ray_anyhit_2d_device_flags_optix", workloads)

    def test_grouped_i64_device_output_symbols_are_wired(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        symbol = (
            "rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_"
            "primitive_grouped_i64_reduction_device_outputs"
        )
        self.assertIn(symbol, runtime)
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn("primitive_grouped_i64_reduction_device_outputs_optix", workloads)
        self.assertIn("group_rows_downloaded_to_host", runtime)

    def test_weighted_sum_device_output_executor_symbols_are_wired(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        prepare_symbol = (
            "rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_"
            "weighted_sum_device_weights_prepare_graph_executor"
        )
        launch_symbol = (
            "rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_"
            "weighted_sum_device_weights_launch_graph_executor_on_stream"
        )
        release_symbol = (
            "rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_"
            "weighted_sum_device_weights_release_graph_executor"
        )
        self.assertIn(prepare_symbol, runtime)
        self.assertIn(prepare_symbol, prelude)
        self.assertIn(prepare_symbol, api)
        self.assertIn(launch_symbol, runtime)
        self.assertIn(launch_symbol, prelude)
        self.assertIn(launch_symbol, api)
        self.assertIn(release_symbol, runtime)
        self.assertIn(release_symbol, prelude)
        self.assertIn(release_symbol, api)
        self.assertIn("prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor", runtime)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum", workloads)
        self.assertIn("optixLaunch", workloads)


class _FakeRayBatch:
    pass


class _FakeGrouped:
    def __init__(self) -> None:
        self.copy_calls = 0
        self.closed = False

    def copy_grouped_results_to_device_outputs(self, output_columns):
        self.copy_calls += 1
        return {
            "metadata": {
                "device_outputs_copied_to_caller_columns": True,
                "device_to_device_copy": True,
                "grouped_results_downloaded_to_host": False,
            }
        }

    def close(self) -> None:
        self.closed = True


class _FakePrimitivePayload:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _FakeScene:
    def __init__(self) -> None:
        self.run_calls = 0
        self.prevalidated_handoff_calls = 0
        self.grouped_i64_device_output_calls = 0
        self.prevalidated_grouped_i64_handoff_calls = 0
        self.closed = False

    def ray_closest_hit_prepared_grouped_argmin_device_outputs(
        self,
        ray_batch,
        grouped_inputs,
        output_columns,
        *,
        prevalidated_handoffs=None,
    ):
        self.run_calls += 1
        if prevalidated_handoffs is not None:
            self.prevalidated_handoff_calls += 1
        return {
            "metadata": {
                "native_device_grouped_argmin": True,
                "native_direct_device_output_columns": True,
                "grouped_result_device_to_device_export": False,
                "rows_materialized": False,
                "grouped_results_materialized": False,
            }
        }

    def ray_batch_prepared_primitive_grouped_i64_reduction_device_outputs(
        self,
        ray_batch,
        primitive_payload,
        output_columns,
        *,
        reduction,
        prevalidated_handoffs=None,
    ):
        self.grouped_i64_device_output_calls += 1
        if prevalidated_handoffs is not None:
            self.prevalidated_grouped_i64_handoff_calls += 1
        return {
            "metadata": {
                "native_direct_device_output_columns": True,
                "rows_materialized": False,
                "group_rows_downloaded_to_host": False,
                "reduction": reduction,
            }
        }

    def close(self) -> None:
        self.closed = True


class _FakeShapeColumn:
    def __init__(self, length: int) -> None:
        self.shape = (length,)


class _FakeAnyHitScene:
    def __init__(self) -> None:
        self.flag_calls = 0
        self.closed = False

    def write_device_any_hit_flags(self, ray_columns, output_flags):
        self.flag_calls += 1
        return {
            "metadata": {
                "native_symbol": "rtdl_optix_write_prepared_ray_anyhit_2d_device_flags",
                "ray_count": ray_columns["ids"].shape[0],
                "direct_device_handoff_authorized": True,
                "ray_columns_true_zero_copy_authorized": True,
                "output_flags_true_zero_copy_authorized": True,
                "triangle_scene_true_zero_copy_authorized": True,
                "true_zero_copy_authorized": True,
            }
        }

    def close(self) -> None:
        self.closed = True


class _FakeWeightedSumExecutor:
    def __init__(self) -> None:
        self.launch_calls = 0
        self.closed = False

    def launch(self, cuda_stream) -> dict[str, object]:
        self.launch_calls += 1
        return {
            "backend": "optix",
            "contract": "PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_WEIGHTED_SUM_DEVICE_OUTPUT_GRAPH_EXECUTOR_V1",
            "device_output_used": True,
            "host_scalar_read_before_consumer": False,
            "host_row_materialization_before_consumer": False,
            "query_rays_uploaded_each_run": False,
            "ray_weights_uploaded_each_run": False,
            "cuda_stream_ptr_nonzero": bool(cuda_stream),
            "public_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            "prepared_ray_batch_used": True,
            "device_output_used": True,
            "host_scalar_read_before_consumer": False,
            "host_row_materialization_before_consumer": False,
            "query_rays_uploaded_each_run": False,
            "ray_weights_uploaded_each_run": False,
            "public_speedup_claim_authorized": False,
        }

    def close(self) -> None:
        self.closed = True


class _FakeWeightedSumScene:
    def __init__(self) -> None:
        self.executor_prepare_calls = 0
        self.executor = _FakeWeightedSumExecutor()
        self.closed = False

    def prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor(
        self,
        ray_batch,
        ray_weights,
        output_scalar,
    ):
        self.executor_prepare_calls += 1
        return self.executor

    def close(self) -> None:
        self.closed = True


class _FailingPrepareScene:
    def __init__(self) -> None:
        self.closed = False

    def prepare_ray_batch_device_columns(self, ray_columns):
        raise RuntimeError("ray prepare failed")

    def close(self) -> None:
        self.closed = True


if __name__ == "__main__":
    unittest.main()
