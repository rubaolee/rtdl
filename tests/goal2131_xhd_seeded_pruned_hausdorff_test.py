import pathlib
import re
import unittest

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2131_xhd_seeded_pruned_hausdorff_2026-05-16.md"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = ROOT / "examples" / "rtdl_hausdorff_v2_function.py"
PUBLIC_PERF = ROOT / "scripts" / "goal2126_public_hausdorff_dataset_perf.py"


def _text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class Goal2131XhdSeededPrunedHausdorffTest(unittest.TestCase):
    def test_generic_threshold_flags_symbol_is_wired_without_app_terms(self) -> None:
        symbol = "rtdl_optix_write_prepared_point_group_threshold_flags_2d"
        for path in (PRELUDE, API, OPTIX_RUNTIME):
            with self.subTest(path=path.name):
                self.assertIn(symbol, _text(path))
        native_surface = "\n".join(
            line
            for line in (_text(PRELUDE) + _text(CORE) + _text(WORKLOADS) + _text(API)).splitlines()
            if "point_group" in line.lower() or "PointGroup" in line or "threshold_flags" in line
        )
        self.assertIn("threshold_flags", native_surface)
        self.assertNotRegex(native_surface, re.compile("hausdorff|x-hd|xdh", re.IGNORECASE))

    def test_python_binding_exposes_per_query_threshold_flags(self) -> None:
        runtime = _text(OPTIX_RUNTIME)
        self.assertIn("def threshold_flags", runtime)
        self.assertIn("np.ctypeslib.as_array(flags).copy()", runtime)
        self.assertIn("rtdl_optix_write_prepared_point_group_threshold_flags_2d", runtime)

    def test_seeded_pruned_app_method_is_wired(self) -> None:
        app = _text(APP)
        public_perf = _text(PUBLIC_PERF)
        for needle in (
            "_directed_rt_grouped_seeded_pruned_nearest_witness",
            "hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness",
            "rtdl_rt_grouped_seeded_pruned_nearest_witness",
            "prepared.threshold_flags",
            "unsafe_indices",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, app)
        self.assertIn("_run_rtdl_grouped_seeded_pruned", public_perf)
        self.assertIn("rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio", public_perf)

    def test_seed_sampler_preserves_extreme_source_candidates(self) -> None:
        from examples import rtdl_hausdorff_v2_function as hd

        columns = hd._as_point_columns(
            np.asarray(
                [
                    [0.0, 0.5],
                    [2.0, 0.1],
                    [1.0, 3.0],
                    [1.5, -2.0],
                    [0.3, 0.2],
                    [0.4, 0.9],
                ],
                dtype=np.float64,
            ),
            name="points",
        )
        _sample, indices = hd._seed_sample_point_columns(columns, sample_count=4, seed=2131)
        self.assertIn(0, indices.tolist())
        self.assertIn(1, indices.tolist())
        self.assertIn(2, indices.tolist())
        self.assertIn(3, indices.tolist())

    def test_point_column_packing_uses_vectorized_owner_buffer(self) -> None:
        from examples import rtdl_hausdorff_v2_function as hd
        from rtdsl.embree_runtime import pack_points

        packed = pack_points(
            ids=np.arange(8, dtype=np.int64),
            x=np.linspace(0.0, 1.0, 8, dtype=np.float64),
            y=np.linspace(1.0, 2.0, 8, dtype=np.float64),
            dimension=2,
        )
        self.assertEqual(packed.count, 8)
        self.assertEqual(packed.dimension, 2)
        self.assertIsNotNone(packed.owner)
        self.assertEqual(int(packed.records[7].id), 7)
        self.assertAlmostEqual(float(packed.records[7].x), 1.0)
        optix_packed = hd._pack_point_columns_for_optix(
            {
                "ids": np.arange(8, dtype=np.int64),
                "x": np.linspace(0.0, 1.0, 8, dtype=np.float64),
                "y": np.linspace(1.0, 2.0, 8, dtype=np.float64),
            }
        )
        self.assertIsNotNone(optix_packed.owner)

    def test_report_records_boundary_and_pod_requirement(self) -> None:
        report = _text(REPORT)
        self.assertIn("sample-seeded threshold pruning", report)
        self.assertIn("generic point-group threshold flags", report)
        self.assertIn("Engine app-agnostic boundary: `accept`", report)
        self.assertIn("Outperform optimized grouped CuPy: `needs-pod-evidence`", report)


if __name__ == "__main__":
    unittest.main()
