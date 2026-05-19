from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPEAT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2424_rt_dbscan_prepared_cupy_fairness_baseline_2026-05-19.md"
NATIVE = ROOT / "src" / "native"


class Goal2424RtDbscanPreparedCupyFairnessBaselineTest(unittest.TestCase):
    def test_prepared_cupy_baseline_is_wired_without_native_dbscan_abi(self) -> None:
        app = APP.read_text(encoding="utf-8")
        repeat = REPEAT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        native_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in NATIVE.rglob("*")
            if path.is_file()
        ).lower()

        self.assertIn("partner_cupy_prepared_grid_components_3d", app)
        self.assertIn("prepare_radius_graph_components_3d_cupy_grid_partner_columns", app)
        self.assertIn("radius_graph_components_3d_cupy_prepared_grid_partner_columns", app)
        self.assertIn("PREPARED_CUPY_GRID_MODE", repeat)
        self.assertIn("partner_cupy_prepared_grid_components_3d", repeat)
        self.assertIn("Fair prepared CUDA-core baseline", readme)
        self.assertNotIn("rtdl_optix_dbscan", native_text)
        self.assertNotIn("rtdl_embree_dbscan", native_text)

    def test_repeat_probe_records_fairness_fields(self) -> None:
        repeat = REPEAT.read_text(encoding="utf-8")

        self.assertIn("prepared_grid_build_sec", repeat)
        self.assertIn("prepared_grid_reused", repeat)
        self.assertIn("prepared_run_count", repeat)
        self.assertIn('"rt_core_accelerated": False', repeat)
        self.assertIn('"cell_graph_granularity": "prepared_radius_grid"', repeat)

    def test_report_narrows_previous_performance_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("not\nthe final fair CUDA-core-versus-RT-core steady-state comparison", report)
        self.assertIn("Any new claim that prepared RT beats pure CuPy", report)
        self.assertIn("partner_cupy_prepared_grid_components_3d", report)
        self.assertIn("If prepared pure CuPy wins on a dataset", report)
        self.assertIn("does not authorize paper-level RT-DBSCAN reproduction", report)


if __name__ == "__main__":
    unittest.main()
