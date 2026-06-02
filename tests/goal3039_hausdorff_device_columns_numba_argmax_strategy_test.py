from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_function.py"
OPTIX_RUNTIME = REPO_ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3039_hausdorff_device_columns_numba_argmax_strategy_2026-06-02.md"


class Goal3039HausdorffDeviceColumnsNumbaArgmaxStrategyTest(unittest.TestCase):
    def test_hausdorff_strategy_composes_generic_producer_and_consumer(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("_directed_rt_grouped_device_columns_numba_argmax_nearest_witness", source)
        self.assertIn("hausdorff_distance_2d_rt_grouped_device_columns_numba_argmax_nearest_witness", source)
        self.assertIn("write_device_nearest_witness_columns", source)
        self.assertIn("global_argmax_u32_f64_partner_columns", source)
        self.assertIn("host_row_materialization_used_on_new_path", source)
        self.assertIn("rtdl_rt_grouped_device_columns_numba_argmax_nearest_witness", source)

    def test_strategy_is_app_level_not_native_engine_customization(self) -> None:
        source = APP.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        helper_start = source.index("_directed_rt_grouped_device_columns_numba_argmax_nearest_witness")
        helper_end = source.index("def hausdorff_distance_2d_rt_nearest_witness", helper_start)
        helper = source[helper_start:helper_end]

        self.assertIn("numba_global_argmax_u32_f64", helper)
        self.assertIn("generic_point_group_nearest_witness_2d_device_columns", runtime)
        self.assertNotIn("rtdl_optix_run_hausdorff", runtime.lower())
        self.assertNotIn("hausdorff", runtime[runtime.index("class PreparedOptixPointGroupNearestWitness2D"):runtime.index("def prepare_optix_point_group_nearest_witness_2d")].lower())

    def test_user_facing_dispatcher_and_cli_include_new_method(self) -> None:
        source = APP.read_text(encoding="utf-8")
        method = "rtdl_rt_grouped_device_columns_numba_argmax_nearest_witness"

        self.assertIn(f'if method == "{method}"', source)
        self.assertIn(f'"{method}"', source)
        self.assertIn("radius=args.rt_nearest_radius", source)
        self.assertIn("target_points_per_group=args.target_points_per_group", source)

    def test_report_keeps_performance_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3039",
            "rtdl_rt_grouped_device_columns_numba_argmax_nearest_witness",
            "app-level code only",
            "does not authorize",
            "next goal must run it on a pod",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
