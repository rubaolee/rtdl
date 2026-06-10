from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
APP = ROOT / "examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"
COMPOSITE = ROOT / "scripts/goal3612_rayjoin_safe_mixed_route_composite.py"
REPORT = ROOT / "docs/reports/goal3704_segment_pair_prepared_left_exact_count_route_2026-06-07.md"


class Goal3704SegmentPairPreparedLeftExactCountRouteTest(unittest.TestCase):
    def test_native_prepared_left_stores_candidate_and_exact_buffers(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("struct PreparedSegmentPairLeftSet", 1)[1].split(
            "static void ensure_segment_pair_intersection_pipeline",
            1,
        )[0]

        self.assertIn("DevPtr d_left;", block)
        self.assertIn("DevPtr d_left_exact;", block)
        self.assertIn("upload(d_left.ptr, gpu_left.data(), gpu_left.size());", block)
        self.assertIn("upload(d_left_exact.ptr, left, count);", block)

    def test_native_abi_and_runtime_expose_prepared_left_scalar_count(self) -> None:
        symbol = "rtdl_optix_count_prepared_segment_pair_intersection_prepared_left"

        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_SYMBOL", runtime)
        self.assertIn("def count_prepared_left", runtime)
        self.assertIn('"count_prepared_left"', runtime)

    def test_prepared_left_count_uses_one_pass_exact_route_without_left_upload(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        block = source.split("static void count_prepared_segment_pair_intersection_prepared_left_optix", 1)[1].split(
            "static void run_prepared_segment_first_hit_optix",
            1,
        )[0]

        self.assertIn("reset_segment_pair_phase_timings(6u);", block)
        self.assertIn("prepared_left->d_left.ptr", block)
        self.assertIn("prepared_left->d_left_exact.ptr", block)
        self.assertIn("count_segment_pair_intersection_exact_one_pass_optix", block)
        self.assertNotIn("upload(", block)

    def test_rayjoin_helper_opts_in_explicitly_and_records_metadata(self) -> None:
        app = APP.read_text(encoding="utf-8")
        composite = COMPOSITE.read_text(encoding="utf-8")

        self.assertIn("prepare_left_for_count: bool = False", app)
        self.assertIn("prepare_segment_pair_left_set_optix", app)
        self.assertIn("prepared.count_prepared_left_exact_intersections(prepared_left)", app)
        self.assertIn('"segment_pair_count_route"', app)
        self.assertIn('"front_door_schema"', app)
        self.assertIn('"prepared_left_for_count"', app)
        self.assertIn("prepare_left_for_count=True", composite)
        self.assertIn('"prepared_left_for_count"', composite)

    def test_report_keeps_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("prepare right once + prepare left once", report)
        self.assertIn("not a RayJoin-specific engine path", report)
        self.assertIn("requires pod evidence", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
