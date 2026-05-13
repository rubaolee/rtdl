from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "run_goal1828_optix_device_column_pod_validation.py"
REPORT = ROOT / "docs" / "reports" / "goal1834_optix_whole_primitive_input_zero_copy_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1834_optix_whole_primitive_input_zero_copy_pod_validation.json"


class Goal1834OptixWholePrimitiveInputZeroCopyTest(unittest.TestCase):
    def test_native_abi_and_pipeline_use_borrowed_triangle_inputs(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        self.assertIn("build_custom_accel_from_borrowed_device_aabbs", core)
        self.assertIn("owns_aabb_buf", core)
        self.assertIn("g_rayanyhit_count_device_columns", core)
        self.assertIn("RayAnyHitCountDeviceColumnsLaunchParams", workloads)
        self.assertIn("load_triangle_column(prim)", workloads)
        self.assertIn("triangle_columns_zero_copy", workloads)
        self.assertIn("rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs", api)
        self.assertIn("rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs", prelude)

    def test_python_public_surface_and_script_use_zero_copy_scene_contract(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("pack_optix_ray_any_hit_2d_device_triangle_zero_copy_scene_inputs", runtime)
        self.assertIn("prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene", runtime)
        self.assertIn("device_triangle_columns_aabb_zero_copy_gas_build", runtime)
        self.assertIn("rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs", runtime)
        self.assertIn("pack_optix_ray_any_hit_2d_device_triangle_zero_copy_scene_inputs", init)
        self.assertIn("prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene", init)
        self.assertIn("triangle_aabbs", script)
        self.assertIn('"true_zero_copy_authorized"', script)
        self.assertIn('"v2_0_release_authorized": False', script)

    def test_pod_artifact_authorizes_exact_input_zero_copy_only(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal1834")
        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["observed_count"], artifact["expected_count"])
        self.assertEqual(artifact["device"], "NVIDIA RTX A4500")
        self.assertTrue(artifact["claim_boundary"]["ray_column_true_zero_copy_observed"])
        self.assertTrue(artifact["claim_boundary"]["triangle_scene_true_zero_copy_observed"])
        self.assertTrue(artifact["claim_boundary"]["whole_primitive_true_zero_copy_authorized"])
        self.assertTrue(artifact["claim_boundary"]["true_zero_copy_authorized"])
        self.assertFalse(artifact["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])
        self.assertEqual(
            artifact["triangle_metadata"]["transfer_mode"],
            "device_triangle_columns_aabb_zero_copy_gas_build",
        )
        self.assertTrue(artifact["triangle_metadata"]["native_acceleration_structure_required"])

    def test_report_preserves_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("`accept-with-boundary`", report)
        self.assertIn("whole-primitive\ninput true zero-copy", report)
        self.assertIn("GAS output remains\n  native OptiX acceleration state", report)
        self.assertIn("v2.0 release readiness", report)
        self.assertIn("rt_core_speedup_claim_authorized", report)


if __name__ == "__main__":
    unittest.main()
