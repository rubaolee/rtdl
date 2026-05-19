from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2430_rt_dbscan_prepared_adjacency_stream_prototype_2026-05-19.md"
NATIVE = ROOT / "src" / "native"


class Goal2430RtDbscanPreparedAdjacencyStreamPrototypeTest(unittest.TestCase):
    def test_generic_adjacency_stream_api_is_wired(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("PreparedCupyRadiusGraphAdjacency3D", adapters)
        self.assertIn("prepare_radius_graph_adjacency_3d_cupy_partner_columns", adapters)
        self.assertIn("radius_graph_components_3d_cupy_prepared_adjacency_partner_columns", adapters)
        self.assertIn("generic_prepared_cupy_directed_radius_graph_adjacency_component_labels_3d", adapters)
        self.assertIn("edge_stream_policy", adapters)
        self.assertIn("PreparedCupyRadiusGraphAdjacency3D", init_text)
        self.assertIn("prepare_radius_graph_adjacency_3d_cupy_partner_columns", init_text)
        self.assertIn("partner_cupy_prepared_adjacency_components_3d", app)
        self.assertIn("partner_cupy_prepared_adjacency_components_3d", readme)

    def test_boundary_stays_partner_side_and_app_agnostic(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        native_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in NATIVE.rglob("*")
            if path.is_file()
        ).lower()

        self.assertIn("partner-side CuPy work first", report)
        self.assertIn("does not claim RT-core acceleration", report)
        self.assertIn("does not add native DBSCAN ABI", report)
        self.assertIn("generic fixed-radius graph adjacency contract", report)
        self.assertNotIn("rtdl_optix_dbscan", native_text)


if __name__ == "__main__":
    unittest.main()
