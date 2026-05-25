from __future__ import annotations

import ctypes
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.optix_runtime import PreparedOptixKernel
from rtdsl.optix_runtime import _RtdlRayClosestHitRow
from rtdsl.optix_runtime import grouped_candidate_argmin_host_reference
from rtdsl.reference import Ray3D
from rtdsl.runtime import _identity_cache_token


class Goal2598OptixGenericClosestHitContractTest(unittest.TestCase):
    def test_python_runtime_declares_generic_closest_hit_row_contract(self) -> None:
        self.assertIn("ray_triangle_closest_hit", PreparedOptixKernel._SUPPORTED_PREDICATES)
        runtime_source = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text()
        self.assertIn("def ray_closest_hit_row_arrays", runtime_source)
        self.assertIn("class PreparedOptixRayBatch3D", runtime_source)
        self.assertIn("def prepare_ray_batch", runtime_source)
        self.assertIn("def ray_closest_hit_row_arrays_prepared_rays", runtime_source)
        self.assertIn("def ray_closest_hit_grouped_argmin", runtime_source)
        self.assertIn("class PreparedOptixClosestHitGroupedArgmin3D", runtime_source)
        self.assertIn("class PreparedOptixGroupedCandidateArgmin", runtime_source)
        self.assertIn("def prepare_optix_grouped_candidate_argmin", runtime_source)
        self.assertIn("def grouped_candidate_argmin_host_reference", runtime_source)
        self.assertIn("def ray_closest_hit_prepared_grouped_argmin", runtime_source)
        self.assertIn("def two_scene_ray_closest_hit_prepared_grouped_argmin", runtime_source)
        self.assertIn("PREPARED_TRIANGLE_SCENE_3D_RAY_CLOSEST_HIT_ROW_ARRAYS_V1", runtime_source)
        self.assertIn("PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_CLOSEST_HIT_ROW_ARRAYS_V1", runtime_source)
        self.assertIn("PREPARED_TRIANGLE_SCENE_3D_RAY_CLOSEST_HIT_GROUPED_ARGMIN_V1", runtime_source)
        self.assertIn("PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_CLOSEST_HIT_GROUPED_ARGMIN_V1", runtime_source)
        self.assertIn("PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_PREPARED_GROUPED_ARGMIN_V1", runtime_source)
        self.assertIn("PREPARED_TRIANGLE_SCENE_3D_TWO_PREPARED_RAY_BATCHES_PREPARED_GROUPED_ARGMIN_V1", runtime_source)
        self.assertIn("OPTIX_GROUPED_CANDIDATE_ARGMIN_V1", runtime_source)
        self.assertIn("native_device_grouped_argmin", runtime_source)
        self.assertEqual(
            _RtdlRayClosestHitRow._fields_,
            [
                ("ray_id", ctypes.c_uint32),
                ("triangle_id", ctypes.c_uint32),
                ("t", ctypes.c_double),
            ],
        )
        self.assertEqual(ctypes.sizeof(_RtdlRayClosestHitRow), 16)

    def test_generic_wrapper_allows_optix_backend_source_path(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "generic_primitives.py").read_text()
        self.assertNotIn("backend='optix' is not wired", source)
        self.assertIn("run_optix(", source)
        self.assertIn("generic ray_triangle_closest_hit backend must be one of: cpu, embree, optix", source)

    def test_native_optix_sources_export_app_agnostic_symbol(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text()
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text()
        core = (ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp").read_text()
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text()

        self.assertIn("struct RtdlRayClosestHitRow", prelude)
        self.assertIn("rtdl_optix_run_ray_closest_hit_3d", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows", prelude)
        self.assertIn("rtdl_optix_ray_batch_3d_create", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_rows", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_closest_hit_grouped_argmin", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin", prelude)
        self.assertIn("rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin", prelude)
        self.assertIn("rtdl_optix_grouped_candidate_argmin_inputs_create", prelude)
        self.assertIn("rtdl_optix_grouped_candidate_argmin_finalize", prelude)
        self.assertIn("extern \"C\" int rtdl_optix_run_ray_closest_hit_3d", api)
        self.assertIn("extern \"C\" int rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows", api)
        self.assertIn("extern \"C\" int rtdl_optix_ray_batch_3d_create", api)
        self.assertIn("extern \"C\" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_rows", api)
        self.assertIn("extern \"C\" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin", api)
        self.assertIn("extern \"C\" int rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create", api)
        self.assertIn("extern \"C\" int rtdl_optix_grouped_candidate_argmin_inputs_create", api)
        self.assertIn("extern \"C\" int rtdl_optix_grouped_candidate_argmin_finalize", api)
        self.assertIn("extern \"C\" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin", api)
        self.assertIn(
            "extern \"C\" int rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin",
            api,
        )
        self.assertIn(
            "extern \"C\" int rtdl_optix_static_triangle_scene_3d_ray_closest_hit_grouped_argmin",
            api,
        )
        self.assertIn("kRayClosestHit3DKernelSrc", core)
        self.assertIn("kRayClosestHitGroupedArgminKernelSrc", core)
        self.assertIn("closest_hit_grouped_argmin_merge_two", core)
        self.assertIn("grouped_candidate_argmin_min_key", core)
        self.assertIn("grouped_candidate_argmin_min_index", core)
        self.assertIn("uint8_t* group_has_value", core)
        self.assertIn("__closesthit__rayclosest3d_closesthit", core)
        self.assertIn("run_ray_closest_hit_3d_optix", workloads)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_closest_hit_rows_optix", workloads)
        self.assertIn("PreparedRayBatch3D", workloads)
        self.assertIn("PreparedClosestHitGroupedArgmin3D", workloads)
        self.assertIn("PreparedGroupedCandidateArgmin", workloads)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_rows_optix", workloads)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin_optix", workloads)
        self.assertIn("run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_optix", workloads)
        self.assertIn("run_prepared_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin_optix", workloads)
        self.assertIn("run_prepared_grouped_candidate_argmin_optix", workloads)
        self.assertNotIn("materialize_args", workloads)
        self.assertIn(
            "run_prepared_static_triangle_scene_3d_ray_closest_hit_grouped_argmin_optix",
            workloads,
        )
        self.assertNotIn("GPU-RMQ", core[core.find("kRayClosestHit3DKernelSrc"):core.find("kRayClosestHit3DKernelSrc") + 5000])
        self.assertNotIn("rmq", workloads[workloads.find("run_ray_closest_hit_3d_optix"):workloads.find("run_ray_closest_hit_3d_optix") + 5000].lower())

    def test_grouped_candidate_argmin_host_reference_ignores_nan_and_breaks_ties(self) -> None:
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy is optional for local source-tree tests")
        result = grouped_candidate_argmin_host_reference(
            np.asarray([0, 1, 0, 1, 1, 2], dtype=np.uint32),
            np.asarray([3.0, 7.0, 2.0, 2.0, 2.0, float("nan")], dtype=np.float64),
            np.asarray([30, 70, 20, 11, 9, 99], dtype=np.uint32),
            group_count=4,
        )
        self.assertEqual(result["has_value"].tolist(), [1, 1, 0, 0])
        self.assertEqual(result["index"].tolist()[:2], [20, 9])
        self.assertEqual(result["value"].tolist()[:2], [2.0, 2.0])

    def test_identity_cache_token_owns_payload_identity(self) -> None:
        left = (Ray3D(1, 0.0, 0.0, -1.0, 0.0, 0.0, 1.0, 10.0),)
        right = (Ray3D(2, 0.0, 0.0, -1.0, 0.0, 0.0, 1.0, 10.0),)
        left_token = _identity_cache_token("rays", left)
        right_token = _identity_cache_token("rays", right)

        self.assertIsNotNone(left_token)
        self.assertIsNotNone(right_token)
        self.assertIs(left_token.payload, left)
        self.assertEqual(left_token, _identity_cache_token("rays", left))
        self.assertNotEqual(left_token, right_token)

    def test_validation_driver_cpu_smoke(self) -> None:
        output = subprocess.check_output(
            [
                sys.executable,
                str(ROOT / "scripts" / "goal2598_optix_closest_hit_validation.py"),
                "--backend",
                "cpu",
                "--skip-gpu-rmq",
            ],
            cwd=ROOT,
            text=True,
        )
        payload = json.loads(output)
        self.assertEqual(payload["backend"], "cpu")
        self.assertTrue(payload["closest_hit"]["matches_cpu_reference"])
        self.assertTrue(payload["overall_matches_cpu_reference"])


if __name__ == "__main__":
    unittest.main()
