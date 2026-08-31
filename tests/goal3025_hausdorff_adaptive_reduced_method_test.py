from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_function.py"


class Goal3025HausdorffAdaptiveReducedMethodTest(unittest.TestCase):
    def test_method_is_wired_through_cli_and_programmatic_api(self) -> None:
        source = APP.read_text(encoding="utf-8")
        method = "rtdl_rt_grouped_adaptive_reduced_nearest_witness"
        self.assertIn(method, source)
        self.assertIn("def _directed_rt_grouped_adaptive_reduced_nearest_witness", source)
        self.assertIn("def hausdorff_distance_2d_rt_grouped_adaptive_reduced_nearest_witness", source)
        self.assertIn(f'if method == "{method}":', source)
        self.assertIn(f'elif args.method == "{method}":', source)

    def test_method_composes_generic_primitives_without_hausdorff_native_customization(self) -> None:
        source = APP.read_text(encoding="utf-8")
        start = source.index("def _directed_rt_grouped_adaptive_reduced_nearest_witness")
        end = source.index("def hausdorff_distance_2d_rt_nearest_witness", start)
        block = source[start:end]
        self.assertIn("prepare_optix_point_group_nearest_witness_2d", block)
        self.assertIn("prepared.threshold_flags", block)
        self.assertIn("prepared.nearest_max_distance_row", block)
        self.assertIn("point_group_nearest_max_distance_with_threshold_flags", block)
        self.assertNotIn("nearest_witness_rows", block)
        self.assertNotIn("rtdl_optix_run_hausdorff", block)
        self.assertNotIn("hausdorff-specific native", block.lower())


if __name__ == "__main__":
    unittest.main()
