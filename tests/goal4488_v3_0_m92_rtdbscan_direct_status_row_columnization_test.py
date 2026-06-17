from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
SCRIPT = ROOT / "scripts" / "goal4488_m92_rtdbscan_direct_status_row_columnization_matrix.py"


class Goal4488M92DirectStatusRowColumnizationTest(unittest.TestCase):
    def test_direct_status_prepare_has_generic_fast_row_to_column_paths(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("def _point_xyz_host_columns_3d")
        end = source.index("def _point_xyz(row)")
        section = source[start:end]

        self.assertNotIn("dbscan", section.lower())
        self.assertNotIn("cluster", section.lower())
        for fragment in (
            "attribute_xyz_rows_direct",
            "mapping_xyz_rows_direct",
            "sequence_xyz_rows_direct",
            "sequence_id_xyz_rows_direct",
            "generic_normalized_tuple_rows",
            "[float(row.x) for row in raw_rows]",
            "[float(row[\"x\"]) for row in raw_rows]",
            "[float(row[0]) for row in raw_rows]",
        ):
            self.assertIn(fragment, section)

    def test_direct_status_prepare_uses_fast_columnizer_before_cupy_upload(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("def _prepare_direct_status_union_runtime_columns_cupy_3d")
        end = source.index("def _run_direct_status_union_signature_from_prepared_columns_cupy_3d")
        section = source[start:end]

        self.assertIn("_point_xyz_host_columns_3d(raw_rows)", section)
        self.assertIn("mark_phase(\"row_xyz_extract_sec\")", section)
        self.assertIn("cupy.asarray(x_host, dtype=cupy.float64)", section)
        self.assertIn('"point_coordinate_host_extraction": coordinate_source', section)
        self.assertIn(
            '"point_coordinate_host_intermediate_tuple_avoided": coordinate_source != "generic_normalized_tuple_rows"',
            section,
        )

    def test_m92_runner_compares_against_m91_prepare_breakdown(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for fragment in (
            "rtdl.v3_0.rtdbscan_direct_status_row_columnization.goal4488.v1",
            "goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.json",
            "goal4487_v3_0_m91_rtdbscan_direct_status_prepare_breakdown_2026-06-17.json",
            "production_prepare_speedup",
            "point_coordinate_host_extraction",
            "builds host x/y/z lists directly for common",
            "Point3D, mapping, and sequence rows",
        ):
            self.assertIn(fragment, source)


if __name__ == "__main__":
    unittest.main()
