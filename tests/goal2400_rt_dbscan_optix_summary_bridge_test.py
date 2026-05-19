from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
RUNNER = ROOT / "scripts" / "goal2392_rt_dbscan_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2400_rt_dbscan_optix_summary_to_cupy_component_bridge_2026-05-19.md"
NATIVE_DIR = ROOT / "src" / "native"


class Goal2400RtDbscanOptixSummaryBridgeTest(unittest.TestCase):
    def test_cupy_component_primitive_accepts_caller_supplied_core_flags(self) -> None:
        text = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("core_flags=None", text)
        self.assertIn("neighbor_counts=None", text)
        self.assertIn("caller_supplied_core_flags", text)
        self.assertIn('"core_flag_source": str(core_flag_source)', text)
        self.assertIn("if not caller_supplied_core_flags:", text)

    def test_benchmark_app_exposes_optix_summary_bridge_mode(self) -> None:
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("optix_core_flags_cupy_grid_components_3d", app)
        self.assertIn("_optix_ranked_summaries_to_cupy_core_columns", app)
        self.assertIn("optix_ranked_fixed_radius_summary_threshold", app)
        self.assertIn("materializes_neighbor_rows", app)
        self.assertIn("Hybrid OptiX + Partner Run", readme)
        self.assertIn("clustered3d_optix_core_flags_cupy_grid_4096", runner)

    def test_report_and_native_boundary_are_app_agnostic(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        pattern = re.compile(r"\brtdl_[a-z0-9_]*dbscan[a-z0-9_]*\b", re.IGNORECASE)
        native_hits: list[str] = []
        for path in NATIVE_DIR.rglob("*"):
            if not path.is_file():
                continue
            if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                native_hits.append(str(path.relative_to(ROOT)))

        self.assertEqual(native_hits, [])
        self.assertIn("No DBSCAN-specific native ABI is added", report)
        self.assertIn("not the final paper-style device-output continuation", report)
        self.assertIn("min_neighbors <= 64", report)


if __name__ == "__main__":
    unittest.main()
