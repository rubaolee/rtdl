from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
RTDSL_INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
RUNNER = ROOT / "scripts" / "goal2392_rt_dbscan_pod_runner.sh"
REPEAT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"


class Goal2405RtDbscanRtCountThresholdDeviceColumnsTest(unittest.TestCase):
    def test_native_surface_is_generic_and_rt_count_threshold_shaped(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        self.assertIn("kFixedRadiusCountThreshold3DRtKernelSrc", core)
        self.assertIn("__anyhit__frn3d_count_threshold_anyhit", core)
        self.assertIn("optixSetPayload_1", core)
        self.assertIn("optixTerminateRay", core)
        self.assertIn("PreparedFixedRadiusCountThreshold3DRt", workloads)
        self.assertIn("write_prepared_fixed_radius_count_threshold_3d_device_outputs_optix", workloads)
        self.assertIn("rtdl_optix_prepare_fixed_radius_count_threshold_3d", api)
        self.assertIn("rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs", prelude)
        for symbol_text in (api, prelude):
            self.assertNotIn("rtdl_optix_dbscan", symbol_text.lower())
            self.assertNotIn("rtdl_optix_run_dbscan", symbol_text.lower())

    def test_python_partner_surface_exposes_device_columns_without_app_abi(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        init = RTDSL_INIT.read_text(encoding="utf-8")

        self.assertIn("PreparedOptixFixedRadiusCountThreshold3D", runtime)
        self.assertIn("prepare_optix_fixed_radius_count_threshold_3d", runtime)
        self.assertIn("prepared_rt_core_count_threshold_3d", runtime)
        self.assertIn("fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns", adapters)
        self.assertIn("allocate_fixed_radius_count_threshold_3d_partner_device_output_columns", adapters)
        self.assertIn("generic_fixed_radius_count_threshold_3d_device_columns", adapters)
        self.assertIn("PreparedOptixFixedRadiusCountThreshold3D", init)
        self.assertIn("fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns", init)

    def test_rt_dbscan_app_uses_new_mode_as_composition_only(self) -> None:
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        repeat = REPEAT.read_text(encoding="utf-8")

        self.assertIn("optix_rt_core_flags_cupy_grid_components_3d", app)
        self.assertIn("fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns", app)
        self.assertIn("rt_core_accelerated", app)
        self.assertIn("materializes_neighbor_rows", app)
        self.assertIn("True RT traversal core flags", readme)
        self.assertIn("clustered3d_optix_rt_core_flags_cupy_grid_4096", runner)
        self.assertIn("optix_rt_core_flags_cupy_grid_components_3d", repeat)
        self.assertIn("optix_rt_count_threshold_sec", repeat)


if __name__ == "__main__":
    unittest.main()
