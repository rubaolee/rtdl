from __future__ import annotations

import importlib
import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
RUNNER = ROOT / "scripts" / "goal2392_rt_dbscan_pod_runner.sh"
REPEAT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2417_rt_dbscan_prepared_cupy_grid_continuation_2026-05-19.md"
NATIVE = ROOT / "src" / "native"


def _cupy_or_skip():
    try:
        cupy = importlib.import_module("cupy")
        if int(cupy.cuda.runtime.getDeviceCount()) < 1:
            raise RuntimeError("no CUDA device")
        cupy.zeros((1,), dtype=cupy.float32).sum().item()
        return cupy
    except Exception as exc:  # pragma: no cover - environment dependent
        raise unittest.SkipTest(f"CuPy/CUDA unavailable: {exc}") from exc


class Goal2417RtDbscanPreparedCupyGridContinuationTest(unittest.TestCase):
    def test_static_wiring_is_generic_and_python_side_only(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        repeat = REPEAT.read_text(encoding="utf-8")
        native_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in NATIVE.rglob("*") if path.is_file())

        self.assertIn("PreparedCupyRadiusGraphComponents3DGrid", adapters)
        self.assertIn("prepare_radius_graph_components_3d_cupy_grid_partner_columns", adapters)
        self.assertIn("radius_graph_components_3d_cupy_prepared_grid_partner_columns", adapters)
        self.assertIn("generic_prepared_cupy_grid_radius_graph_component_labels_3d", adapters)
        self.assertIn("PreparedCupyRadiusGraphComponents3DGrid", init)
        self.assertIn("optix_rt_core_flags_cupy_prepared_grid_components_3d", app)
        self.assertIn("optix_rt_core_flags_cupy_prepared_grid_components_3d", readme)
        self.assertIn("optix_rt_core_flags_cupy_prepared_grid_components_3d", runner)
        self.assertIn("PREPARED_GRID_MODE", repeat)
        self.assertIn("prepared_grid_reused", repeat)
        self.assertNotIn("rtdl_optix_dbscan", native_text.lower())
        self.assertNotIn("prepared_grid_components", native_text)

    def test_report_records_pivot_from_microcell_and_pod_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("prepared CuPy grid continuation", report)
        self.assertIn("microcell path was performance-negative", report)
        self.assertIn("No native RTDL engine ABI was added", report)
        self.assertIn("pod steady-state evidence is still required", report)

    def test_prepared_grid_reuses_state_and_matches_plain_grid_when_cupy_available(self) -> None:
        cupy = _cupy_or_skip()
        columns = {
            "ids": cupy.arange(4, dtype=cupy.uint32),
            "x": cupy.asarray([0.0, 0.05, 0.10, 0.90], dtype=cupy.float64),
            "y": cupy.asarray([0.0, 0.03, 0.02, 0.90], dtype=cupy.float64),
            "z": cupy.asarray([0.0, 0.01, 0.04, 0.90], dtype=cupy.float64),
        }

        plain = rt.radius_graph_components_3d_cupy_grid_partner_columns(
            columns,
            radius=0.15,
            min_neighbors=3,
            partner="cupy",
            return_metadata=True,
        )
        prepared = rt.prepare_radius_graph_components_3d_cupy_grid_partner_columns(
            columns,
            radius=0.15,
            partner="cupy",
        )
        first = rt.radius_graph_components_3d_cupy_prepared_grid_partner_columns(
            prepared,
            min_neighbors=3,
            return_metadata=True,
        )
        second = rt.radius_graph_components_3d_cupy_prepared_grid_partner_columns(
            prepared,
            min_neighbors=3,
            return_metadata=True,
        )

        plain_labels = cupy.asnumpy(plain["columns"]["component_labels"]).tolist()
        first_labels = cupy.asnumpy(first["columns"]["component_labels"]).tolist()
        second_labels = cupy.asnumpy(second["columns"]["component_labels"]).tolist()
        self.assertEqual(first_labels, plain_labels)
        self.assertEqual(second_labels, plain_labels)
        self.assertFalse(first["metadata"]["prepared_grid_reused"])
        self.assertTrue(second["metadata"]["prepared_grid_reused"])
        self.assertEqual(second["metadata"]["prepared_run_count"], 2)
        self.assertTrue(second["metadata"]["output_workspace_reused"])


if __name__ == "__main__":
    unittest.main()
