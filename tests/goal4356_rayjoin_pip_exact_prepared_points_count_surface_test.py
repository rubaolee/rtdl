from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal4356_rayjoin_pip_exact_prepared_points_count_surface_2026-06-12.md"


class Goal4356RayJoinPipExactPreparedPointsCountSurfaceTest(unittest.TestCase):
    def test_native_exact_prepared_points_surface_uses_resident_point_columns(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        symbol = "rtdl_optix_count_prepared_point_closed_shape_membership_prepared_points_2d"
        function = "count_prepared_point_closed_shape_membership_prepared_points_2d_optix"
        self.assertIn(function, workloads)
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)

        start = workloads.index(f"static void {function}")
        end = workloads.index(
            "static void count_prepared_point_closed_shape_membership_device_filtered_2d_optix",
            start,
        )
        body = workloads[start:end]
        self.assertIn("PreparedPointProbeColumns2D* prepared_points", body)
        self.assertIn("prepared_points->d_points_x.ptr", body)
        self.assertIn("prepared_points->d_points_y.ptr", body)
        self.assertIn("prepared_points->d_point_ids.ptr", body)
        self.assertIn("prepared_points->points_x_f64[pi]", body)
        self.assertIn("prepared_points->points_y_f64[pi]", body)
        self.assertIn("prepared_points->d_count.ptr", body)
        self.assertIn("prepared_points->d_params.ptr", body)
        self.assertIn("reset_closed_shape_membership_phase_timings(12u)", body)
        self.assertNotIn("const RtdlPoint* points", body)
        self.assertNotIn("std::vector<float> pts_x", body)
        self.assertNotIn("DevPtr d_pts_x", body)

    def test_python_runtime_exposes_exact_prepared_points_count(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        for phrase in (
            "OPTIX_CLOSED_SHAPE_MEMBERSHIP_PREPARED_POINTS_EXACT_COUNT_SYMBOL",
            "rtdl_optix_count_prepared_point_closed_shape_membership_prepared_points_2d",
            "def count_prepared_points_exact",
            "prepared_points_exact_count",
            "optional_count_prepared_closed_shape_membership_prepared_points_exact.argtypes",
        ):
            self.assertIn(phrase, runtime)

    def test_rayjoin_app_has_explicit_claim_bounded_mode(self) -> None:
        app = APP.read_text(encoding="utf-8")

        for phrase in (
            '"exact_prepared_points"',
            "count_prepared_points_exact(prepared_point_columns)",
            "exact_prepared_points_matches_host_exact",
            "point_to_shape_positive_hit_count_exact_prepared_points",
            "partial_exact_prepared_points",
            "validation_exact_query_sec",
        ):
            self.assertIn(phrase, app)

    def test_report_records_boundary_and_next_measurement(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin PIP Exact Prepared-Points Count Surface",
            "removes point repack/reupload from the measured exact query loop",
            "still downloads candidate rows and performs host exact refinement",
            "not a public speedup claim",
            "Next required pod check",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
