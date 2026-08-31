from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4973ExactLsiCostDecompositionTest(unittest.TestCase):
    def test_native_extended_segment_pair_timing_getter_exists(self) -> None:
        symbol = "rtdl_optix_segment_pair_intersection_get_last_extended_phase_timings"
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(symbol, workloads)
        for phase in (
            "scaled_cache_ensure",
            "grouped_range_ensure",
            "exact_pipeline_ensure",
            "split_kernel_ensure",
            "device_alloc",
            "param_upload",
            "optix_launch",
            "count_download",
            "split_kernel_launch",
            "total_native",
        ):
            self.assertIn(phase, workloads)

    def test_runtime_exposes_extended_timings_without_breaking_old_getter(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("def get_last_segment_pair_extended_phase_timings", runtime)
        self.assertIn("def _get_last_segment_pair_extended_phase_timings_from_library", runtime)
        self.assertIn('result["extended"] = extended', runtime)
        self.assertIn("def last_extended_phase_timings", runtime)

    def test_app_reports_lsi_and_downstream_decomposition(self) -> None:
        app = APP.read_text(encoding="utf-8")
        self.assertIn("def run_lsi_bounded_exact_repeat_diagnostic", app)
        self.assertIn("--bounded-exact-lsi-repeat-diagnostic", app)
        self.assertIn("build_lsi_cost_decomposition", app)
        self.assertIn("build_downstream_floor_breakdown", app)
        self.assertIn('"lsi_cost_decomposition"', app)
        self.assertIn('"downstream_floor_breakdown"', app)
        self.assertIn('"bounded_exact_lsi_repeat_diagnostic"', app)
        self.assertIn("no_author_comparison", app)


if __name__ == "__main__":
    unittest.main()
