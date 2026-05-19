from __future__ import annotations

import importlib
import math
import pathlib
import unittest

import rtdsl as rt
from rtdsl import partner_adapters


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
RUNNER = ROOT / "scripts" / "goal2392_rt_dbscan_pod_runner.sh"
REPEAT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2414_rt_dbscan_microcell_graph_adapter_2026-05-19.md"
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


class Goal2414RtDbscanMicrocellGraphAdapterTest(unittest.TestCase):
    def test_static_wiring_is_generic_and_python_side_only(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        repeat = REPEAT.read_text(encoding="utf-8")
        native_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in NATIVE.rglob("*") if path.is_file())

        self.assertIn("radius_graph_components_3d_cupy_microcell_graph_partner_columns", adapters)
        self.assertIn("_CUPY_RADIUS_GRAPH_COMPONENTS_3D_MICROCELL_GRAPH_KERNELS", adapters)
        self.assertIn("cell_graph_granularity", adapters)
        self.assertIn("clique_safe_microcell", adapters)
        self.assertIn("radius_graph_components_3d_cupy_microcell_graph_partner_columns", init)
        self.assertIn("optix_rt_core_flags_cupy_microcell_graph_components_3d", app)
        self.assertIn("optix_rt_core_flags_cupy_microcell_graph_components_3d", readme)
        self.assertIn("optix_rt_core_flags_cupy_microcell_graph_components_3d", runner)
        self.assertIn("optix_rt_core_flags_cupy_microcell_graph_components_3d", repeat)
        self.assertNotIn("rtdl_optix_dbscan", native_text.lower())
        self.assertNotIn("microcell_graph_components", native_text)

    def test_report_records_local_boundary_and_pod_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("local implementation complete; pod performance evidence still required", report)
        self.assertIn("microcell_size = radius / sqrt(3)", report)
        self.assertIn("4 tests OK, 2 skipped", report)
        self.assertIn("No native RTDL engine ABI was added", report)

    def test_clique_safe_microcell_size_rejects_the_radius_cell_assumption(self) -> None:
        radius = 1.0
        microcell_size = partner_adapters._fixed_radius_clique_safe_microcell_size(radius)
        neighbor_range = partner_adapters._fixed_radius_microcell_neighbor_range(radius, microcell_size)

        self.assertAlmostEqual(microcell_size, 1.0 / math.sqrt(3.0))
        self.assertEqual(neighbor_range, 2)
        self.assertEqual(math.floor(0.99 / radius), 0)
        self.assertNotEqual(math.floor(0.99 / microcell_size), 0)

    def test_same_radius_cell_disconnected_points_do_not_merge_when_cupy_available(self) -> None:
        cupy = _cupy_or_skip()
        columns = {
            "ids": cupy.arange(2, dtype=cupy.uint32),
            "x": cupy.asarray([0.0, 0.99], dtype=cupy.float64),
            "y": cupy.asarray([0.0, 0.99], dtype=cupy.float64),
            "z": cupy.asarray([0.0, 0.99], dtype=cupy.float64),
        }
        core_flags = cupy.ones((2,), dtype=cupy.uint32)
        neighbor_counts = cupy.ones((2,), dtype=cupy.uint32)

        result = rt.radius_graph_components_3d_cupy_microcell_graph_partner_columns(
            columns,
            radius=1.0,
            min_neighbors=1,
            partner="cupy",
            core_flags=core_flags,
            neighbor_counts=neighbor_counts,
            return_metadata=True,
        )

        labels = cupy.asnumpy(result["columns"]["component_labels"]).tolist()
        self.assertNotEqual(int(labels[0]), int(labels[1]))
        self.assertTrue(result["metadata"]["cell_graph_fast_path_active"])
        self.assertEqual(result["metadata"]["cell_graph_granularity"], "clique_safe_microcell")

    def test_mixed_core_input_falls_back_when_cupy_available(self) -> None:
        cupy = _cupy_or_skip()
        columns = {
            "ids": cupy.arange(2, dtype=cupy.uint32),
            "x": cupy.asarray([0.0, 0.25], dtype=cupy.float64),
            "y": cupy.asarray([0.0, 0.25], dtype=cupy.float64),
            "z": cupy.asarray([0.0, 0.25], dtype=cupy.float64),
        }
        core_flags = cupy.asarray([1, 0], dtype=cupy.uint32)
        neighbor_counts = cupy.asarray([2, 1], dtype=cupy.uint32)

        result = rt.radius_graph_components_3d_cupy_microcell_graph_partner_columns(
            columns,
            radius=1.0,
            min_neighbors=2,
            partner="cupy",
            core_flags=core_flags,
            neighbor_counts=neighbor_counts,
            return_metadata=True,
        )

        self.assertFalse(result["metadata"]["cell_graph_fast_path_active"])
        self.assertEqual(result["metadata"]["fallback_reason"], "not_all_points_core")
        self.assertEqual(result["metadata"]["fallback_adapter"], "radius_graph_components_3d_cupy_grid_partner_columns")
        self.assertEqual(set(result["columns"]), {"point_ids", "component_labels", "is_core", "neighbor_counts"})


if __name__ == "__main__":
    unittest.main()
