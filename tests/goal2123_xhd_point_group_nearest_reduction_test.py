import pathlib
import re
import unittest

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2123_xhd_point_group_nearest_reduction_2026-05-16.md"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_function.py"
LAB = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_language_lab.py"


def _text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class Goal2123XhdPointGroupNearestReductionTest(unittest.TestCase):
    def test_generic_native_reduce_symbol_is_wired_without_app_terms(self) -> None:
        symbol = "rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d"
        for path in (PRELUDE, API, OPTIX_RUNTIME):
            with self.subTest(path=path.name):
                self.assertIn(symbol, _text(path))
        native_surface = "\n".join(
            line
            for line in (_text(PRELUDE) + _text(CORE) + _text(WORKLOADS) + _text(API)).splitlines()
            if "point_group" in line.lower() or "PointGroup" in line or "nearest_max" in line
        )
        self.assertNotRegex(native_surface, re.compile("hausdorff|x-hd|xdh", re.IGNORECASE))
        self.assertIn("kPointGroupNearestMaxReduceKernelSrc", _text(CORE))
        self.assertIn("reduce_prepared_point_group_nearest_max_distance_2d_optix", _text(WORKLOADS))

    def test_python_binding_exposes_one_row_reduction(self) -> None:
        runtime = _text(OPTIX_RUNTIME)
        self.assertIn("def nearest_max_distance_row", runtime)
        self.assertIn("rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d", runtime)
        self.assertIn('{"query_id": 0xFFFFFFFF, "neighbor_id": 0xFFFFFFFF, "distance": float("inf")}', runtime)

    def test_app_uses_reduction_as_v2_language_method(self) -> None:
        app = _text(APP)
        lab = _text(LAB)
        self.assertIn("hausdorff_distance_2d_rt_grouped_reduced_nearest_witness", app)
        self.assertIn("_directed_rt_grouped_reduced_nearest_witness", app)
        self.assertIn("nearest_max_distance_row", app)
        self.assertIn("point_group_nearest_max_distance", app)
        self.assertIn("rtdl_rt_grouped_reduced_nearest_witness", lab)

    def test_scalar_reducer_preserves_exact_python_distance_from_native_witness_ids(self) -> None:
        from examples import rtdl_hausdorff_v2_function as hd

        source = hd._as_point_columns(np.array([[0.0, 0.0], [3.0, 4.0]], dtype=np.float64), name="source")
        target = hd._as_point_columns(np.array([[0.0, 0.0], [6.0, 8.0]], dtype=np.float64), name="target")
        reduced = hd._reduce_nearest_max_distance_row(source, target, {"query_id": 1, "neighbor_id": 0, "distance": 5.0})
        self.assertEqual(reduced["source_index"], 1)
        self.assertEqual(reduced["target_index"], 0)
        self.assertEqual(reduced["row_count"], 1)
        self.assertEqual(reduced["distance"], 5.0)

    def test_report_records_performance_boundary_and_next_xhd_gaps(self) -> None:
        report = _text(REPORT)
        self.assertIn("one-row device reduction", report)
        self.assertIn("Outperform pure CUDA on large synthetic sets: `accept-with-boundary`", report)
        self.assertIn("Outperform pure CUDA on X-HD paper datasets: `needs-more-evidence`", report)
        self.assertIn("heavy-cell CUDA fallback", report)
        self.assertIn("device worklist", report)


if __name__ == "__main__":
    unittest.main()
