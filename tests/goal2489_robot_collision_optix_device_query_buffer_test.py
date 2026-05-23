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
REPORT = ROOT / "docs" / "reports" / "goal2489_robot_collision_optix_device_query_buffers_2026-05-21.md"
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
CONTRACT = "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1"


class Goal2489RobotCollisionOptixDeviceQueryBufferTest(unittest.TestCase):
    def test_python_surface_exports_native_device_query_preparer(self) -> None:
        init_py = (ROOT / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")

        self.assertIn("from .optix_runtime import prepare_optix_grouped_segment_query_3d", init_py)
        self.assertIn("from .optix_runtime import PreparedOptixGroupedSegmentQuery3D", init_py)
        self.assertIn('"prepare_optix_grouped_segment_query_3d"', init_py)
        self.assertIn('"PreparedOptixGroupedSegmentQuery3D"', init_py)
        self.assertIn("class PreparedOptixGroupedSegmentQuery3D", runtime)
        self.assertIn(f'contract = "{CONTRACT}"', runtime)

    def test_native_abi_declares_app_agnostic_prepared_query_handle(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(encoding="utf-8")

        for symbol in (
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_create",
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_flags",
            "rtdl_optix_static_triangle_scene_3d_grouped_segment_query_destroy",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)

        self.assertIn("struct PreparedGroupedSegmentQuery3D", workloads)
        self.assertIn("RayAnyHitGroupFlags3DLaunchParams", workloads)
        self.assertIn("ray_anyhit_group_flags_kernel_source_3d", workloads)
        self.assertIn("native OptiX device query/output buffers", APP.read_text(encoding="utf-8"))

    def test_runtime_metadata_records_not_true_zero_copy(self) -> None:
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")

        self.assertIn("native_device_query_buffers_reused", runtime)
        self.assertIn('"query_segments_uploaded_each_run": False', runtime)
        self.assertIn('"per_segment_records_materialized": False', runtime)
        self.assertIn('"per_segment_records_downloaded_to_host": False', runtime)
        self.assertIn('"group_flags_downloaded_to_host": True', runtime)
        self.assertIn('"true_zero_copy_authorized": False', runtime)

    def test_robot_app_exposes_optix_prepared_device_buffer_mode(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn('"optix_prepared_device_buffers"', app)
        self.assertIn("reuse_native_device_query_buffers", app)
        self.assertIn("run_native_prepared_grouped_segment_any_hit_flags", app)
        self.assertIn('"Goal2489"', app)

    def test_native_files_remain_free_of_app_vocabulary(self) -> None:
        hits: list[str] = []
        for path in NATIVE_FILES:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if FORBIDDEN_NATIVE_RE.search(text):
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_report_records_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2489", report)
        self.assertIn("device-resident grouped 3D segment query buffers", report)
        self.assertIn("not true zero-copy", report)
        self.assertIn("does not add robot", report)
        self.assertIn("public speedup claim is not authorized", report)


if __name__ == "__main__":
    unittest.main()
