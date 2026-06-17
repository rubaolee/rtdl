from __future__ import annotations

import importlib.util
import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4489M93DirectStatusPointColumnsSourceTest(unittest.TestCase):
    def test_public_surface_and_claim_boundary_are_present(self) -> None:
        for name in (
            "prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_point_columns_preview_3d",
            "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d",
        ):
            self.assertTrue(hasattr(rt, name), name)

        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("def _prepare_direct_status_union_runtime_columns_from_cupy_point_columns_3d")
        end = source.index("def _run_direct_status_union_signature_from_prepared_columns_cupy_3d")
        section = source[start:end]

        self.assertNotIn("dbscan", section.lower())
        self.assertNotIn("cluster", section.lower())
        for fragment in (
            "caller_owned_cupy_device_columns",
            "coordinate_upload_avoided=True",
            "mark_phase(\"row_xyz_extract_sec\")",
            "mark_phase(\"coordinate_columns_sec\")",
        ):
            self.assertIn(fragment, section)
        self.assertIn("point_columns[{name!r}] must have dtype cupy.float64", source)

        builder_start = source.index("def _build_direct_status_union_runtime_columns_from_cupy_xyz_3d")
        builder_end = source.index("def _prepare_direct_status_union_runtime_columns_cupy_3d")
        builder = source[builder_start:builder_end]
        self.assertIn('"point_coordinate_upload_avoided": coordinate_upload_avoided', builder)


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4489M93DirectStatusPointColumnsRuntimeTest(unittest.TestCase):
    def _rows(self):
        return (
            rt.Point3D(0, 0.0, 0.0, 0.0),
            rt.Point3D(1, 0.01, 0.0, 0.0),
            rt.Point3D(2, 0.02, 0.0, 0.0),
            rt.Point3D(3, 1.0, 1.0, 1.0),
            rt.Point3D(4, 1.01, 1.0, 1.0),
            rt.Point3D(5, 4.0, 4.0, 4.0),
        )

    def _columns(self):
        import cupy

        rows = self._rows()
        return {
            "x": cupy.asarray([row.x for row in rows], dtype=cupy.float64),
            "y": cupy.asarray([row.y for row in rows], dtype=cupy.float64),
            "z": cupy.asarray([row.z for row in rows], dtype=cupy.float64),
        }

    def test_direct_status_point_columns_match_row_prepare_signature(self) -> None:
        row_prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(
            self._rows(),
            radius=0.05,
            cell_factor=0.5,
        )
        column_prepared = (
            rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_point_columns_preview_3d(
                self._columns(),
                radius=0.05,
                cell_factor=0.5,
            )
        )

        row_result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
            row_prepared
        )
        column_result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
            column_prepared
        )

        self.assertEqual(row_result["columns"], column_result["columns"])
        prepare_metadata = column_prepared.to_metadata()["prepare_metadata"]
        self.assertEqual("caller_owned_cupy_device_columns", prepare_metadata["point_coordinate_host_extraction"])
        self.assertTrue(prepare_metadata["point_coordinate_upload_avoided"])
        self.assertTrue(prepare_metadata["point_coordinate_host_intermediate_tuple_avoided"])

        with self.assertRaisesRegex(ValueError, "requires original point rows"):
            column_prepared.run_component_signature(validate_against_materialized_signature=True)

    def test_predicate_point_columns_match_expected_signature(self) -> None:
        import cupy

        prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d(
            self._columns(),
            radius=0.05,
            cell_factor=0.5,
        )
        flags = cupy.asarray([1, 1, 1, 0, 0, 0], dtype=cupy.uint32)
        counts = cupy.asarray([3, 3, 3, 0, 0, 0], dtype=cupy.uint32)
        result = rt.run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d(
            prepared,
            predicate_flags=flags,
            neighbor_counts=counts,
        )
        self.assertEqual(result["metadata"]["status"], "accept")
        self.assertTrue(result["metadata"]["prepared_predicate_direct_status_union_reused"])
        label_counts = tuple(int(value) for value in result["columns"]["label_counts"].get().tolist())
        self.assertEqual((3,), tuple(value for value in label_counts if value))
        self.assertEqual(3, int(result["columns"]["flag_true_count"].get()[0]))
        self.assertEqual(3, int(result["columns"]["negative_label_count"].get()[0]))


if __name__ == "__main__":
    unittest.main()
