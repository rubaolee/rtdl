from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
HAUSDORFF_APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_function.py"
LANGUAGE_LAB = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_language_lab.py"


class Goal3026HausdorffAdaptiveRawRowViewTest(unittest.TestCase):
    def _point_group_class_source(self) -> str:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        start = source.index("class PreparedOptixPointGroupNearestWitness2D")
        end = source.index("def prepare_optix_point_group_nearest_witness_2d", start)
        return source[start:end]

    def test_runtime_exposes_generic_point_group_nearest_raw_view(self) -> None:
        source = self._point_group_class_source()
        self.assertIn("def nearest_witness_raw(self, query_points, *, radius: float) -> OptixRowView:", source)
        block = source[source.index("def nearest_witness_raw"):source.index("def nearest_witness_rows")]
        self.assertIn("rtdl_optix_run_prepared_point_group_nearest_witness_2d", block)
        self.assertIn("OptixRowView(", block)
        self.assertIn('field_names=("query_id", "neighbor_id", "distance")', block)
        self.assertIn("_make_owned_row_view", block)

    def test_dict_rows_delegate_to_raw_view_and_close_it(self) -> None:
        source = self._point_group_class_source()
        block = source[source.index("def nearest_witness_rows"):source.index("def nearest_max_distance_row")]
        self.assertIn("rows = self.nearest_witness_raw(query_points, radius=radius)", block)
        self.assertIn("rows.to_dict_rows()", block)
        self.assertIn("rows.close()", block)
        self.assertNotIn("rtdl_optix_run_prepared_point_group_nearest_witness_2d", block)

    def test_hausdorff_raw_adaptive_path_avoids_dict_materialization(self) -> None:
        source = HAUSDORFF_APP.read_text(encoding="utf-8")
        self.assertIn("def _directed_rt_grouped_adaptive_raw_nearest_witness", source)
        block = source[
            source.index("def _directed_rt_grouped_adaptive_raw_nearest_witness"):
            source.index("def _directed_rt_grouped_adaptive_reduced_nearest_witness")
        ]
        self.assertIn("prepared.nearest_witness_raw", block)
        self.assertIn("raw_rows.rows_ptr[local_index]", block)
        self.assertIn("raw_rows.close()", block)
        self.assertNotIn("nearest_witness_rows", block)
        self.assertNotIn("to_dict_rows", block)
        self.assertIn("rt_grouped_adaptive_raw_radius", block)

    def test_user_entrypoints_include_raw_adaptive_method(self) -> None:
        source = HAUSDORFF_APP.read_text(encoding="utf-8")
        self.assertIn("def hausdorff_distance_2d_rt_grouped_adaptive_raw_nearest_witness", source)
        self.assertIn('method="rtdl_rt_grouped_adaptive_raw_nearest_witness"', source)
        self.assertIn('"rtdl_rt_grouped_adaptive_raw_nearest_witness",', source)
        self.assertIn('if method == "rtdl_rt_grouped_adaptive_raw_nearest_witness":', source)

    def test_language_lab_can_run_raw_adaptive_method(self) -> None:
        source = LANGUAGE_LAB.read_text(encoding="utf-8")
        self.assertIn('"rtdl_rt_grouped_adaptive_raw_nearest_witness",', source)
        self.assertIn('"preferred current RT path using generic raw row views', source)
        self.assertIn("hd.hausdorff_distance_2d_rt_grouped_adaptive_raw_nearest_witness", source)


if __name__ == "__main__":
    unittest.main()
