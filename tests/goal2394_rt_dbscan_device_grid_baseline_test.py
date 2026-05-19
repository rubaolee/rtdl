from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2394_rt_dbscan_device_grid_baseline_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2394_rt_dbscan_device_grid_local_linux"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2394RtDbscanDeviceGridBaselineTest(unittest.TestCase):
    def test_generic_cupy_grid_component_primitive_is_exported(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("radius_graph_components_3d_cupy_grid_partner_columns", adapters)
        self.assertIn("generic_cupy_grid_radius_graph_component_labels_3d", adapters)
        self.assertIn("_CUPY_RADIUS_GRAPH_COMPONENTS_3D_GRID_KERNELS", adapters)
        self.assertIn('"radius_graph_components_3d_cupy_grid_partner_columns"', init_text)
        self.assertIn("partner_cupy_grid_components_3d", app)
        self.assertIn("Strong CUDA-core baseline", readme)

    def test_local_linux_artifacts_validate_device_grid_baseline(self) -> None:
        tiny = _load("tiny_cupy_grid.json")
        validated = _load("clustered512_cupy_grid_validated.json")
        grid = _load("clustered4096_cupy_grid.json")
        host = _load("clustered4096_host_bucket.json")

        self.assertTrue(tiny["matches_reference"])
        self.assertTrue(validated["matches_reference"])
        self.assertEqual(grid["signature"], host["signature"])
        self.assertFalse(grid["claim_boundary"]["rt_core_accelerated"])
        self.assertFalse(grid["claim_boundary"]["paper_speedup_claim_authorized"])
        self.assertTrue(grid["metadata"]["device_grid_index_used"])
        self.assertFalse(grid["metadata"]["host_bucket_index_used"])
        self.assertTrue(host["metadata"]["host_bucket_index_used"])
        self.assertLess(grid["elapsed_sec"], host["elapsed_sec"])

    def test_report_keeps_claim_boundary_and_next_gap_explicit(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("not an RTX/RT-core claim", report)
        self.assertIn("OptiX fixed-radius device output -> device-resident grouped/component continuation", report)
        self.assertIn("2.72x faster than the host-bucket continuation", report)
        self.assertIn("accept-with-boundary", report)


if __name__ == "__main__":
    unittest.main()
