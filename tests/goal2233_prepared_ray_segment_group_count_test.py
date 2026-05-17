from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PY_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2233_prepared_ray_segment_group_count_2026-05-17.md"


def _function_body(text: str, name: str) -> str:
    start = text.index(name)
    brace = text.index("{", start)
    depth = 0
    for index in range(brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise AssertionError(f"could not parse function body for {name}")


class Goal2233PreparedRaySegmentGroupCountTest(unittest.TestCase):
    def test_native_prepared_abi_is_present(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_prepare_ray_segment_group_count_2d",
            "rtdl_optix_run_prepared_ray_segment_group_count_2d",
            "rtdl_optix_destroy_prepared_ray_segment_group_count_2d",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
        self.assertIn("prepare_ray_segment_group_count_2d_optix", api)
        self.assertIn("run_prepared_ray_segment_group_count_2d_optix", api)
        self.assertIn("delete reinterpret_cast<PreparedRaySegmentGroupCount2D*>", api)

    def test_prepared_workload_reuses_segment_pair_scene(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("struct PreparedRaySegmentGroupCount2D", workloads)
        self.assertIn("std::unique_ptr<PreparedSegmentPairIntersectionBuild> segment_pairs", workloads)
        self.assertIn("ray_segments_from_finite_rays", workloads)
        self.assertIn("finalize_ray_segment_group_count_rows", workloads)
        body = _function_body(workloads, "run_prepared_ray_segment_group_count_2d_optix")
        self.assertIn("run_prepared_segment_pair_intersection_optix", body)
        self.assertIn("prepared->segment_pairs.get()", body)
        self.assertIn("prepared->group_by_segment_id", body)

    def test_python_prepared_context_manager_and_symbols(self) -> None:
        text = PY_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("class PreparedOptixRaySegmentGroupCount2D", text)
        self.assertIn("def prepare_ray_segment_group_count_2d_optix", text)
        self.assertIn('"rtdl_optix_prepare_ray_segment_group_count_2d"', text)
        self.assertIn('"rtdl_optix_run_prepared_ray_segment_group_count_2d"', text)
        self.assertIn('"rtdl_optix_destroy_prepared_ray_segment_group_count_2d"', text)
        self.assertIn("def __enter__(self) -> \"PreparedOptixRaySegmentGroupCount2D\"", text)
        self.assertIn("def __exit__(self, exc_type, exc, tb) -> None", text)

    def test_report_records_perf_reason_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2233", text)
        self.assertIn("prepared", text)
        self.assertIn("40.40x slower", text)
        self.assertIn("does not authorize", text)
        self.assertIn("device-resident grouped reduction", text)
        self.assertIn("app-agnostic", text)


if __name__ == "__main__":
    unittest.main()
