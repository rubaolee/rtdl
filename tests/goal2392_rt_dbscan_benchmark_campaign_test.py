from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
RESEARCH_README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2392_rt_dbscan_benchmark_campaign_2026-05-19.md"
POD_RUNNER = ROOT / "scripts" / "goal2392_rt_dbscan_pod_runner.sh"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
NATIVE_DIR = ROOT / "src" / "native"


class Goal2392RtDbscanBenchmarkCampaignTest(unittest.TestCase):
    def _run_app(self, mode: str) -> dict[str, object]:
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--mode",
                mode,
                "--dataset",
                "tiny",
                "--include-rows",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def test_cpu_reference_and_rtdl_row_path_match_tiny_fixture(self) -> None:
        reference = self._run_app("cpu_reference")
        rtdl_rows = self._run_app("rtdl_cpu_rows")

        self.assertEqual(reference["app"], "rt_dbscan_benchmark")
        self.assertTrue(reference["matches_reference"])
        self.assertTrue(rtdl_rows["matches_reference"])
        self.assertEqual(rtdl_rows["signature"], reference["signature"])
        self.assertEqual(reference["signature"]["cluster_sizes"], {"1": 4, "2": 4})
        self.assertEqual(reference["signature"]["noise_count"], 1)

    def test_partner_adapters_expose_generic_3d_radius_graph_contracts(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_count_threshold_3d_partner_columns", adapters)
        self.assertIn("radius_graph_components_3d_spatial_bucket_partner_columns", adapters)
        self.assertIn("radius_graph_components_3d_cupy_grid_partner_columns", adapters)
        self.assertIn("generic_fixed_radius_count_threshold_3d", adapters)
        self.assertIn("generic_spatial_bucket_radius_graph_component_labels_3d", adapters)
        self.assertIn("generic_cupy_grid_radius_graph_component_labels_3d", adapters)
        self.assertIn('"fixed_radius_count_threshold_3d_partner_columns"', init_text)
        self.assertIn('"radius_graph_components_3d_spatial_bucket_partner_columns"', init_text)
        self.assertIn('"radius_graph_components_3d_cupy_grid_partner_columns"', init_text)

    def test_docs_record_paper_boundary_and_research_benchmark_location(self) -> None:
        readme = README.read_text(encoding="utf-8")
        research_readme = RESEARCH_README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware", readme)
        self.assertIn("10.1109/IPDPS54959.2023.00100", readme)
        self.assertIn("No DBSCAN-specific native ABI is added", readme)
        self.assertIn("rt_dbscan/", research_readme)
        self.assertIn("not a paper-speedup", report)
        self.assertIn("device-resident radius-graph component continuation", report)
        self.assertIn("scripts/goal2392_rt_dbscan_pod_runner.sh", report)
        self.assertIn("partner_cupy_grid_components_3d", readme)
        self.assertIn("CuPy device-grid", report)

    def test_pod_runner_records_progress_and_bounded_claims(self) -> None:
        runner = POD_RUNNER.read_text(encoding="utf-8")

        self.assertIn("[goal2392]", runner)
        self.assertIn("STEP_TIMEOUT_SECONDS", runner)
        self.assertIn("RTDL_OPTIX_LIBRARY", runner)
        self.assertIn("INSTALL_CUPY_IF_MISSING", runner)
        self.assertIn("INSTALL_OPTIX_SDK_IF_MISSING", runner)
        self.assertIn("cupy-cuda12x", runner)
        self.assertIn("https://github.com/NVIDIA/optix-sdk", runner)
        self.assertIn("partner_spatial_bucket_3d", runner)
        self.assertIn("partner_cupy_grid_components_3d", runner)
        self.assertIn("optix_prepared_rows", runner)

    def test_no_dbscan_specific_native_abi_was_added(self) -> None:
        hits: list[str] = []
        pattern = re.compile(r"\brtdl_[a-z0-9_]*dbscan[a-z0-9_]*\b", re.IGNORECASE)
        for path in NATIVE_DIR.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
