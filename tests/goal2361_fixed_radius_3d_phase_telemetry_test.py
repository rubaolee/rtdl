from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2361_fixed_radius_3d_phase_telemetry_2026-05-19.md"


class Goal2361FixedRadius3DPhaseTelemetryTest(unittest.TestCase):
    def test_native_exports_generic_phase_timing_probe(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_fixed_radius_neighbors_3d_get_last_phase_timings", workloads)
        self.assertIn("rtdl_optix_fixed_radius_neighbors_3d_get_last_phase_timings", prelude)
        self.assertIn("g_optix_last_fixed_radius_3d_prepare_s", workloads)
        self.assertIn("g_optix_last_fixed_radius_3d_count_download_s", workloads)
        self.assertIn("g_optix_last_fixed_radius_3d_row_offset_upload_s", workloads)
        self.assertIn("g_optix_last_fixed_radius_3d_raw_candidate_count", workloads)

    def test_modes_are_generic_and_cover_current_execution_paths(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("reset_fixed_radius_3d_phase_timings(1u)", workloads)
        self.assertIn("reset_fixed_radius_3d_phase_timings(2u)", workloads)
        self.assertIn("reset_fixed_radius_3d_phase_timings(3u)", workloads)
        self.assertIn('"all_pairs_cuda"', runtime)
        self.assertIn('"uniform_cell_compact"', runtime)
        self.assertIn('"simple_rt_traversal"', runtime)
        self.assertNotIn("RTNN", workloads)

    def test_python_runtime_and_runner_surface_telemetry_without_required_hardware(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("get_last_fixed_radius_neighbors_3d_phase_timings", runtime)
        self.assertIn("get_last_fixed_radius_neighbors_3d_phase_timings", init)
        self.assertIn("phase_timings = rt.get_last_fixed_radius_neighbors_3d_phase_timings()", runner)
        self.assertIn('"phase_timings": phase_timings', runner)

    def test_report_keeps_next_step_as_prepared_generic_primitive(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("prepared_bounded_neighbor_search_3d", text)
        self.assertIn("not RTNN-specific", text)
        self.assertIn("phase telemetry", text)
        self.assertIn("not a release claim", text)
        self.assertIn("docs/reports/goal2361_rtdl_3d_neighbor_phase/", text)
        self.assertIn("reusable host/device grid preparation", text)


if __name__ == "__main__":
    unittest.main()
