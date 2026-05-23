from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal2490_robot_collision_optix_count_only_result_2026-05-22.md"
NATIVE_FILES = (
    ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
    ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp",
    ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h",
    ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp",
)
FORBIDDEN_NATIVE_RE = re.compile(
    r"\b(robot|collision|link|pose|joint|kinematic|planner)\b",
    re.IGNORECASE,
)


class Goal2490RobotCollisionOptixCountOnlyResultTest(unittest.TestCase):
    def test_native_abi_declares_app_agnostic_count_result(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(
            encoding="utf-8"
        )
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(
            encoding="utf-8"
        )
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )

        symbol = "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_count"
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn(
            "run_prepared_static_triangle_scene_3d_grouped_segment_query_any_hit_count_optix",
            workloads,
        )
        self.assertIn("flagged_group_count_out", prelude)

    def test_python_runtime_exposes_count_only_result_metadata(self) -> None:
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")

        self.assertIn("run_native_prepared_grouped_segment_any_hit_count", runtime)
        self.assertIn("uint32_flagged_group_count", runtime)
        self.assertIn('"group_flags_downloaded_to_python": False', runtime)
        self.assertIn('"python_group_flags_materialized": False', runtime)
        self.assertIn('"true_zero_copy_authorized": False', runtime)

    def test_robot_app_exposes_count_only_screening_mode(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn('"optix_prepared_device_count"', app)
        self.assertIn("reuse_native_device_query_count", app)
        self.assertIn("probe_reference_flagged_group_count", app)
        self.assertIn('"Goal2490"', app)

    def test_native_files_remain_free_of_app_vocabulary(self) -> None:
        hits: list[str] = []
        for path in NATIVE_FILES:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if FORBIDDEN_NATIVE_RE.search(text):
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_report_records_count_only_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2490", report)
        self.assertIn("count-only", report)
        self.assertIn("not true zero-copy", report)
        self.assertIn("no robot-specific native ABI", report)
        self.assertIn("public speedup claim is not authorized", report)


if __name__ == "__main__":
    unittest.main()
