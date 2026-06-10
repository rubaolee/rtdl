from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/rt_dbscan/README.md"
REPORT = ROOT / "docs/reports/goal3744_rt_dbscan_optix_numba_bridge_2026-06-07.md"
ARTIFACT = ROOT / "docs/reports/goal3744_rt_dbscan_optix_numba_bridge_a5000/summary.json"


class Goal3744RtDbscanOptixNumbaBridgeTest(unittest.TestCase):
    def test_app_and_readme_expose_explicit_optix_numba_mode(self) -> None:
        app_text = APP.read_text(encoding="utf-8")
        readme_text = README.read_text(encoding="utf-8")
        mode = "optix_rt_core_flags_numba_prepared_grid_components_3d"
        self.assertIn(mode, app_text)
        self.assertIn(mode, readme_text)
        self.assertIn('partner="numba"', app_text)
        self.assertIn("cuda_array_interface", (ROOT / "src/rtdsl/partner.py").read_text(encoding="utf-8"))

    def test_report_and_artifact_keep_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("OptiX to Numba", text)
        self.assertIn("No DBSCAN-specific native ABI", text)
        self.assertIn("does not authorize", text)
        self.assertIn("true-zero-copy", text)
        self.assertTrue(ARTIFACT.exists())

    def test_artifact_records_mixed_performance_not_universal_win(self) -> None:
        import json

        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        ratios = data["ratios"]
        self.assertTrue(any(float(row["optix_numba_vs_optix_cupy_speedup"]) > 1.0 for row in ratios))
        self.assertTrue(any(float(row["optix_numba_vs_optix_cupy_speedup"]) < 1.0 for row in ratios))
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
