import pathlib
import re
import unittest

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2121_xhd_point_group_hausdorff_optix_enhancement_2026-05-16.md"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = ROOT / "examples" / "rtdl_hausdorff_v2_function.py"
LAB = ROOT / "examples" / "rtdl_hausdorff_v2_language_lab.py"


def _text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class Goal2121XhdPointGroupHausdorffOptixEnhancementTest(unittest.TestCase):
    def test_generic_native_point_group_abi_is_wired(self) -> None:
        prelude = _text(PRELUDE)
        self.assertIn("struct RtdlPointGroupBounds2D", prelude)
        for symbol in (
            "rtdl_optix_prepare_point_group_nearest_witness_2d",
            "rtdl_optix_count_prepared_point_group_threshold_reached_2d",
            "rtdl_optix_run_prepared_point_group_nearest_witness_2d",
            "rtdl_optix_destroy_prepared_point_group_nearest_witness_2d",
        ):
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, prelude)
                self.assertIn(symbol, _text(API))
                self.assertIn(symbol, _text(OPTIX_RUNTIME))
                self.assertNotRegex(symbol, re.compile("hausdorff", re.IGNORECASE))

    def test_grouped_optix_kernels_use_bounds_and_not_app_names(self) -> None:
        core = _text(CORE)
        workloads = _text(WORKLOADS)
        for needle in (
            "kPointGroupThresholdRtKernelSrc",
            "kPointGroupNearestRtKernelSrc",
            "min_distance_sq_to_group",
            "nearest_min_distance_sq_to_group",
            "PointGroupThresholdRtLaunchParams",
            "PointGroupNearestRtLaunchParams",
            "PreparedPointGroupNearestWitness2D",
        ):
            self.assertIn(needle, core + workloads)
        native_new_surface = "\n".join(
            line for line in (core + workloads + _text(API) + _text(PRELUDE)).splitlines()
            if "point_group" in line.lower() or "PointGroup" in line
        )
        self.assertNotRegex(native_new_surface, re.compile("hausdorff|x-hd|xdh", re.IGNORECASE))

    def test_python_public_binding_and_language_lab_include_grouped_path(self) -> None:
        runtime = _text(OPTIX_RUNTIME)
        app = _text(APP)
        lab = _text(LAB)
        self.assertIn("class PreparedOptixPointGroupNearestWitness2D", runtime)
        self.assertIn("def prepare_optix_point_group_nearest_witness_2d", runtime)
        self.assertIn("hausdorff_distance_2d_rt_grouped_nearest_witness", app)
        self.assertIn("hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness", app)
        self.assertIn("_directed_rt_grouped_adaptive_nearest_witness", app)
        self.assertIn("_build_uniform_point_groups", app)
        self.assertIn("rtdl_rt_grouped_nearest_witness", app)
        self.assertIn("rtdl_rt_grouped_nearest_witness", lab)
        self.assertIn("rtdl_rt_grouped_adaptive_nearest_witness", lab)

    def test_uniform_group_builder_preserves_original_point_ids(self) -> None:
        from examples import rtdl_hausdorff_v2_function as hd

        columns = hd._as_point_columns(
            np.array(
                [
                    [0.0, 0.0],
                    [10.0, 10.0],
                    [0.1, 0.2],
                    [10.2, 10.1],
                ],
                dtype=np.float64,
            ),
            name="points",
        )
        points, groups = hd._build_uniform_point_groups(columns, target_points_per_group=2)
        self.assertEqual(sorted(point.id for point in points), [0, 1, 2, 3])
        self.assertGreaterEqual(len(groups), 2)
        for group in groups:
            offset = int(group["point_offset"])
            count = int(group["point_count"])
            self.assertGreater(count, 0)
            xs = [points[index].x for index in range(offset, offset + count)]
            ys = [points[index].y for index in range(offset, offset + count)]
            self.assertEqual(float(group["min_x"]), min(xs))
            self.assertEqual(float(group["max_x"]), max(xs))
            self.assertEqual(float(group["min_y"]), min(ys))
            self.assertEqual(float(group["max_y"]), max(ys))

    def test_report_records_claim_boundary(self) -> None:
        report = _text(REPORT)
        self.assertIn("X-HD uniform-grid grouping", report)
        self.assertIn("worklist", report)
        self.assertIn("Generic engine boundary: `accept`", report)
        self.assertIn("Outperform pure CUDA on X-HD datasets: `needs-more-evidence`", report)
        self.assertIn("The native engine never receives a Hausdorff-specific ABI name", report)


if __name__ == "__main__":
    unittest.main()
