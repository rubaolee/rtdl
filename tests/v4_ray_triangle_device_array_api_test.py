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


class _FakeScene:
    def __init__(self) -> None:
        self.run_calls = 0
        self.prevalidated_handoff_calls = 0
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
