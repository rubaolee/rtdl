from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1998_optix_pod_sdk_install_and_custom_pipeline_blocker_2026-05-14.md"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"


class Goal1998OptixPodSdkInstallAndCustomPipelineBlockerTest(unittest.TestCase):
    def test_report_records_sdk_install_fixed_but_custom_pipeline_blocked(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn('no longer "OptiX SDK unavailable."', report)
        self.assertIn("`build/librtdl_optix.so`", report)
        self.assertIn("custom-primitive OptiX ray/triangle any-hit modules fail", report)
        self.assertIn("Unsupported ABI version", report)
        self.assertIn("Invalid cross-device link", report)
        self.assertIn("pod-proven RT hardware", report)

    def test_native_hardening_keeps_compiler_log_and_lazy_prepare(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("OptiX module compile error", core)
        self.assertIn("module_log", core)
        self.assertNotIn(
            "static PreparedRayAnyHit2D* prepare_ray_anyhit_2d_device_triangle_columns_aabbs_optix(\n"
            "        const uint32_t* triangle_ids,\n"
            "        const double* triangle_x0,\n"
            "        const double* triangle_y0,\n"
            "        const double* triangle_x1,\n"
            "        const double* triangle_y1,\n"
            "        const double* triangle_x2,\n"
            "        const double* triangle_y2,\n"
            "        const void* triangle_aabbs,\n"
            "        size_t triangle_count)\n"
            "{\n"
            "    ensure_ray_anyhit_count_2d_pipeline();",
            workloads,
        )
        self.assertIn("failed to specialize OptiX 2-D all-witness candidate intersection", workloads)

    def test_preflight_includes_goal1998(self) -> None:
        preflight = PREFLIGHT.read_text(encoding="utf-8")
        self.assertIn("tests.goal1998_optix_pod_sdk_install_and_custom_pipeline_blocker_test", preflight)


if __name__ == "__main__":
    unittest.main()
