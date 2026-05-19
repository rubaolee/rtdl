from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPEAT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2423_prepared_optix_cupy_radius_graph_components_2026-05-19.md"
POD_SMOKE = ROOT / "docs" / "reports" / "goal2423_prepared_optix_cupy_radius_graph_components_pod_smoke"
NATIVE = ROOT / "src" / "native"


class Goal2423PreparedOptixCupyRadiusGraphComponentsTest(unittest.TestCase):
    def test_generic_composite_wiring_is_public_and_python_side_only(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        repeat = REPEAT.read_text(encoding="utf-8")
        native_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in NATIVE.rglob("*") if path.is_file())

        self.assertIn("PreparedOptixCupyRadiusGraphComponents3D", adapters)
        self.assertIn("prepare_optix_cupy_radius_graph_components_3d", adapters)
        self.assertIn("radius_graph_components_3d_optix_cupy_prepared_partner_columns", adapters)
        self.assertIn("generic_prepared_optix_cupy_radius_graph_component_labels_3d", adapters)
        self.assertIn("prepare_optix_cupy_radius_graph_components_3d", init)
        self.assertIn("radius_graph_components_3d_optix_cupy_prepared_partner_columns", init)
        self.assertIn("prepare_optix_cupy_radius_graph_components_3d", app)
        self.assertIn("prepare_optix_cupy_radius_graph_components_3d", readme)
        self.assertIn("prepare_optix_cupy_radius_graph_components_3d", repeat)
        self.assertNotIn("rtdl_optix_dbscan", native_text.lower())

    def test_metadata_and_report_keep_boundaries(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("automatic_hidden_dispatcher", adapters)
        self.assertIn("materializes_neighbor_rows", adapters)
        self.assertIn("prepared_composite_reused", adapters)
        self.assertIn("does not add a native DBSCAN ABI", report)
        self.assertIn("device-resident radius-graph edge stream", report)
        self.assertIn("cleaner baseline", report)

    def test_pod_smoke_records_composite_reuse(self) -> None:
        direct = json.loads((POD_SMOKE / "direct_composite_smoke.json").read_text(encoding="utf-8"))
        repeat = json.loads((POD_SMOKE / "clustered3d_32768_repeat3.json").read_text(encoding="utf-8"))

        self.assertFalse(direct["first_metadata"]["prepared_composite_reused"])
        self.assertTrue(direct["second_metadata"]["prepared_composite_reused"])
        self.assertTrue(direct["second_metadata"]["prepared_cupy_grid_reused"])
        self.assertTrue(repeat["signatures_match"])
        prepared_rows = [
            row for row in repeat["rows"]
            if row["mode"] == "optix_rt_core_flags_cupy_prepared_grid_components_3d"
        ]
        self.assertEqual([row.get("prepared_composite_reused") for row in prepared_rows], [False, True, True])


if __name__ == "__main__":
    unittest.main()
