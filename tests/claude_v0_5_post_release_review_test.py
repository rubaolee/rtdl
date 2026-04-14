"""
Claude review test suite: new code after v0.5 (April 14, 2026).

Covers gaps not exercised by goal265-287/328 existing tests:

  1. layout_types — empty layout rejection, require_fields, 3D geometry types
  2. rtnn_perf_audit — summarize_fixed_radius_mismatch edge cases
  3. rtnn_kitti — select_kitti_bounded_frames validation, manifest validation,
     kitti_source_config with valid root, load_kitti_bounded_point_package kind
  4. rtnn_cunsearch_live — precision compile flags, driver source k_max/radius
  5. rtnn_comparison — notes field, duplicate-guard note shape
  6. rtnn_kitti_ready — sample file truncation (at most 5 returned)
"""
from __future__ import annotations

import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.layout_types import layout, field, f32, u32, Layout, GeometryType
from rtdsl.rtnn_cunsearch_live import _precision_compile_flags, _render_cunsearch_driver_source
from rtdsl.rtnn_perf_audit import summarize_fixed_radius_mismatch


# ---------------------------------------------------------------------------
# 1. layout_types
# ---------------------------------------------------------------------------

class LayoutTypesTest(unittest.TestCase):

    def test_empty_layout_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one field"):
            layout("Empty")

    def test_layout_field_names_returns_correct_tuple(self) -> None:
        lay = layout("XY", field("x", f32), field("y", f32))
        self.assertEqual(lay.field_names(), ("x", "y"))

    def test_require_fields_passes_when_all_present(self) -> None:
        lay = layout("XYZ", field("x", f32), field("y", f32), field("z", f32))
        lay.require_fields(("x", "z"))  # no exception

    def test_require_fields_raises_on_missing(self) -> None:
        lay = layout("XY", field("x", f32), field("y", f32))
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            lay.require_fields(("x", "z"))

    def test_require_fields_error_lists_missing_field_names(self) -> None:
        lay = layout("X", field("x", f32))
        with self.assertRaisesRegex(ValueError, "z"):
            lay.require_fields(("x", "z"))

    def test_points3d_has_z_in_required_fields(self) -> None:
        self.assertIn("z", rt.Points3D.required_fields)

    def test_triangles3d_has_z_coordinates_in_required_fields(self) -> None:
        self.assertIn("z0", rt.Triangles3D.required_fields)
        self.assertIn("z1", rt.Triangles3D.required_fields)
        self.assertIn("z2", rt.Triangles3D.required_fields)

    def test_rays3d_has_oz_in_required_fields(self) -> None:
        self.assertIn("oz", rt.Rays3D.required_fields)

    def test_points2d_does_not_have_z_in_required_fields(self) -> None:
        self.assertNotIn("z", rt.Points.required_fields)

    def test_geometry_type_dimensions_are_correct(self) -> None:
        self.assertEqual(rt.Points.dimension, 0)
        self.assertEqual(rt.Segments.dimension, 1)
        self.assertEqual(rt.Polygons.dimension, 2)

    def test_field_to_dict_includes_all_keys(self) -> None:
        f = field("x", f32)
        d = f.to_dict()
        for key in ("name", "scalar_type", "c_type", "cuda_type", "size"):
            self.assertIn(key, d)
        self.assertEqual(d["name"], "x")
        self.assertEqual(d["size"], 4)

    def test_f32_and_u32_scalar_types_have_correct_sizes(self) -> None:
        self.assertEqual(f32.size, 4)
        self.assertEqual(u32.size, 4)

    def test_point3d_layout_has_four_fields(self) -> None:
        self.assertEqual(len(rt.Point3DLayout.fields), 4)
        self.assertEqual(rt.Point3DLayout.field_names(), ("x", "y", "z", "id"))


# ---------------------------------------------------------------------------
# 2. rtnn_perf_audit — summarize_fixed_radius_mismatch
# ---------------------------------------------------------------------------

class RtnnPerfAuditTest(unittest.TestCase):

    def _row(self, query_id: int, neighbor_id: int, distance: float = 0.1) -> dict:
        return {"query_id": query_id, "neighbor_id": neighbor_id, "distance": distance}

    def test_identical_rows_report_no_missing_or_extra(self) -> None:
        rows = (self._row(1, 2), self._row(1, 3))
        summary = summarize_fixed_radius_mismatch(rows, rows, strict_parity_ok=True)
        self.assertTrue(summary.strict_parity_ok)
        self.assertEqual(summary.missing_pair_count, 0)
        self.assertEqual(summary.extra_pair_count, 0)
        self.assertEqual(summary.reference_row_count, 2)
        self.assertEqual(summary.candidate_row_count, 2)
        self.assertIsNone(summary.first_missing_pair)
        self.assertIsNone(summary.first_extra_pair)

    def test_missing_reference_pair_detected(self) -> None:
        reference = (self._row(1, 2), self._row(1, 3))
        candidate = (self._row(1, 2),)
        summary = summarize_fixed_radius_mismatch(reference, candidate, strict_parity_ok=False)
        self.assertFalse(summary.strict_parity_ok)
        self.assertEqual(summary.missing_pair_count, 1)
        self.assertEqual(summary.extra_pair_count, 0)
        self.assertEqual(summary.first_missing_pair, (1, 3))

    def test_extra_candidate_pair_detected(self) -> None:
        reference = (self._row(1, 2),)
        candidate = (self._row(1, 2), self._row(1, 99))
        summary = summarize_fixed_radius_mismatch(reference, candidate, strict_parity_ok=False)
        self.assertEqual(summary.extra_pair_count, 1)
        self.assertEqual(summary.missing_pair_count, 0)
        self.assertEqual(summary.first_extra_pair, (1, 99))

    def test_symmetric_mismatch_counts_both_missing_and_extra(self) -> None:
        reference = (self._row(1, 2), self._row(1, 3))
        candidate = (self._row(1, 2), self._row(1, 4))
        summary = summarize_fixed_radius_mismatch(reference, candidate, strict_parity_ok=False)
        self.assertEqual(summary.missing_pair_count, 1)  # (1,3) missing
        self.assertEqual(summary.extra_pair_count, 1)    # (1,4) extra
        self.assertEqual(summary.first_missing_pair, (1, 3))
        self.assertEqual(summary.first_extra_pair, (1, 4))

    def test_empty_rows_are_equal(self) -> None:
        summary = summarize_fixed_radius_mismatch((), (), strict_parity_ok=True)
        self.assertTrue(summary.strict_parity_ok)
        self.assertEqual(summary.reference_row_count, 0)
        self.assertEqual(summary.candidate_row_count, 0)
        self.assertEqual(summary.missing_pair_count, 0)
        self.assertEqual(summary.extra_pair_count, 0)

    def test_first_mismatch_row_captured_on_positional_difference(self) -> None:
        ref_row = self._row(1, 2, distance=0.5)
        cand_row = self._row(1, 2, distance=0.9)
        summary = summarize_fixed_radius_mismatch((ref_row,), (cand_row,), strict_parity_ok=False)
        # Pairs are the same (query_id, neighbor_id), so missing/extra are empty
        self.assertEqual(summary.missing_pair_count, 0)
        self.assertEqual(summary.extra_pair_count, 0)
        # But positional rows differ
        self.assertIsNotNone(summary.first_reference_row)
        self.assertIsNotNone(summary.first_candidate_row)


# ---------------------------------------------------------------------------
# 3. rtnn_kitti — validation and config paths not covered by goal270/271
# ---------------------------------------------------------------------------

class RtnnKittiValidationTest(unittest.TestCase):

    def test_select_bounded_frames_rejects_nonpositive_max_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "seq" / "velodyne").mkdir(parents=True)
            (root / "seq" / "velodyne" / "000000.bin").write_bytes(b"\x00" * 16)
            with self.assertRaisesRegex(ValueError, "max_frames must be positive"):
                rt.select_kitti_bounded_frames(source_root=root, max_frames=0)

    def test_select_bounded_frames_rejects_nonpositive_stride(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "seq" / "velodyne").mkdir(parents=True)
            (root / "seq" / "velodyne" / "000000.bin").write_bytes(b"\x00" * 16)
            with self.assertRaisesRegex(ValueError, "stride must be positive"):
                rt.select_kitti_bounded_frames(source_root=root, max_frames=1, stride=0)

    def test_select_bounded_frames_rejects_negative_start_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "seq" / "velodyne").mkdir(parents=True)
            (root / "seq" / "velodyne" / "000000.bin").write_bytes(b"\x00" * 16)
            with self.assertRaisesRegex(ValueError, "start_index must be non-negative"):
                rt.select_kitti_bounded_frames(source_root=root, max_frames=1, start_index=-1)

    def test_write_manifest_rejects_nonpositive_max_points_per_frame(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "seq" / "velodyne").mkdir(parents=True)
            (root / "seq" / "velodyne" / "000000.bin").write_bytes(b"\x00" * 16)
            with self.assertRaisesRegex(ValueError, "max_points_per_frame must be positive"):
                rt.write_kitti_bounded_package_manifest(
                    Path(tmpdir) / "out.json",
                    source_root=root,
                    max_frames=1,
                    max_points_per_frame=0,
                )

    def test_write_manifest_rejects_nonpositive_max_total_points(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "seq" / "velodyne").mkdir(parents=True)
            (root / "seq" / "velodyne" / "000000.bin").write_bytes(b"\x00" * 16)
            with self.assertRaisesRegex(ValueError, "max_total_points must be positive"):
                rt.write_kitti_bounded_package_manifest(
                    Path(tmpdir) / "out.json",
                    source_root=root,
                    max_frames=1,
                    max_total_points=0,
                )

    def test_kitti_source_config_returns_resolved_status_for_valid_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = rt.kitti_source_config(tmpdir)
            self.assertEqual(config.current_status, "source_root_resolved")
            self.assertIn("configured", config.notes)

    def test_load_kitti_bounded_point_package_rejects_wrong_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package_path = Path(tmpdir) / "package.json"
            package_path.write_text('{"package_kind":"bad_kind"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported KITTI bounded point package kind"):
                rt.load_kitti_bounded_point_package(package_path)

    def test_load_kitti_bounded_point_package_round_trips_points(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            bin_path = root / "seq" / "velodyne" / "000000.bin"
            bin_path.parent.mkdir(parents=True)
            bin_path.write_bytes(struct.pack("<ffff", 1.0, 2.0, 3.0, 0.5))
            manifest = rt.write_kitti_bounded_package_manifest(
                Path(tmpdir) / "manifest.json",
                source_root=root,
                max_frames=1,
            )
            package_path = rt.write_kitti_bounded_point_package(
                Path(tmpdir) / "package.json",
                manifest,
            )
            loaded = rt.load_kitti_bounded_point_package(package_path)
            self.assertEqual(loaded.selected_point_count, 1)
            self.assertAlmostEqual(loaded.points[0].x, 1.0)
            self.assertAlmostEqual(loaded.points[0].z, 3.0)

    def test_point_id_start_must_be_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            bin_path = root / "seq" / "velodyne" / "000000.bin"
            bin_path.parent.mkdir(parents=True)
            bin_path.write_bytes(b"\x00" * 16)
            manifest = rt.write_kitti_bounded_package_manifest(
                Path(tmpdir) / "manifest.json",
                source_root=root,
                max_frames=1,
            )
            with self.assertRaisesRegex(ValueError, "point_id_start must be positive"):
                rt.load_kitti_bounded_points_from_manifest(manifest, point_id_start=0)


# ---------------------------------------------------------------------------
# 4. rtnn_cunsearch_live — precision compile flags and driver source details
# ---------------------------------------------------------------------------

class CuNSearchLivePrecisionTest(unittest.TestCase):

    def test_precision_compile_flags_double_returns_define_flag(self) -> None:
        flags = _precision_compile_flags("double")
        self.assertIn("-DCUNSEARCH_USE_DOUBLE_PRECISION", flags)
        self.assertEqual(len(flags), 1)

    def test_precision_compile_flags_float_returns_empty_tuple(self) -> None:
        flags = _precision_compile_flags("float")
        self.assertEqual(flags, ())

    def test_driver_source_embeds_radius_in_neighbourhood_search_call(self) -> None:
        payload = {
            "adapter": "cunsearch",
            "workload": "fixed_radius_neighbors",
            "radius": 1.5,
            "k_max": 8,
            "query_points": [{"id": 1, "x": 0.0, "y": 0.0, "z": 0.0}],
            "search_points": [{"id": 2, "x": 0.0, "y": 0.0, "z": 1.0}],
        }
        source = _render_cunsearch_driver_source(payload, Path("/tmp/r.json"), precision_mode="double")
        self.assertIn("static_cast<Real>(1.5)", source)
        self.assertIn("static_cast<std::size_t>(8)", source)

    def test_driver_source_float_uses_f_suffix_on_point_literals(self) -> None:
        payload = {
            "adapter": "cunsearch",
            "workload": "fixed_radius_neighbors",
            "radius": 2.0,
            "k_max": 2,
            "query_points": [{"id": 1, "x": 1.0, "y": 0.0, "z": 0.0}],
            "search_points": [{"id": 2, "x": 0.0, "y": 1.0, "z": 0.0}],
        }
        source = _render_cunsearch_driver_source(payload, Path("/tmp/r.json"), precision_mode="float")
        self.assertIn("1.0f", source)
        self.assertIn("static_cast<Real>(2.0f)", source)

    def test_driver_source_distance_always_computed_in_double(self) -> None:
        payload = {
            "adapter": "cunsearch",
            "workload": "fixed_radius_neighbors",
            "radius": 1.0,
            "k_max": 1,
            "query_points": [{"id": 1, "x": 0.0, "y": 0.0, "z": 0.0}],
            "search_points": [{"id": 2, "x": 0.0, "y": 0.0, "z": 0.5}],
        }
        for mode in ("float", "double"):
            source = _render_cunsearch_driver_source(payload, Path("/tmp/r.json"), precision_mode=mode)
            # Distance computation always casts to double regardless of precision mode
            self.assertIn("static_cast<double>(q[0])", source)


# ---------------------------------------------------------------------------
# 5. rtnn_comparison — notes and blocked path shape
# ---------------------------------------------------------------------------

class RtnnComparisonNotesTest(unittest.TestCase):

    def test_offline_comparison_result_notes_contain_bounded_offline_claim(self) -> None:
        import json
        import struct
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            root = Path(tmpdir) / "source"
            bin_path = root / "seq" / "velodyne" / "000000.bin"
            bin_path.parent.mkdir(parents=True)
            bin_path.write_bytes(struct.pack("<ffff", 0.0, 0.0, 0.0, 0.0))
            manifest = rt.write_kitti_bounded_package_manifest(
                tmpdir / "manifest.json", source_root=root, max_frames=1,
            )
            pkg = rt.write_kitti_bounded_point_package(tmpdir / "pkg.json", manifest)
            response = tmpdir / "response.json"
            response.write_text(json.dumps({
                "adapter": "cunsearch",
                "response_format": "json_rows_v1",
                "workload": "fixed_radius_neighbors",
                "rows": [],
            }), encoding="utf-8")
            result = rt.compare_bounded_fixed_radius_from_packages(
                query_package_path=pkg,
                search_package_path=pkg,
                external_response_path=response,
                radius=0.5,
                k_max=4,
            )
            self.assertIn("bounded offline comparison", result.notes)

    def test_live_comparison_blocked_by_duplicate_guard_has_non_parity(self) -> None:
        import json
        import struct
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            root = Path(tmpdir) / "source"
            bin_path = root / "seq" / "velodyne" / "000000.bin"
            bin_path.parent.mkdir(parents=True)
            # Two identical points — cross-package duplicate
            bin_path.write_bytes(struct.pack("<ffff", 1.0, 2.0, 3.0, 0.0) * 1)
            manifest = rt.write_kitti_bounded_package_manifest(
                tmpdir / "manifest.json", source_root=root, max_frames=1,
            )
            pkg = rt.write_kitti_bounded_point_package(tmpdir / "pkg.json", manifest)
            # Use same package for both query and search → 1 duplicate point
            result = rt.compare_bounded_fixed_radius_live_cunsearch(
                query_package_path=pkg,
                search_package_path=pkg,
                request_path=tmpdir / "req.json",
                response_path=tmpdir / "resp.json",
                radius=1.0,
                k_max=4,
                cunsearch_source_root=tmpdir / "src",
                cunsearch_build_root=tmpdir / "build",
            )
            self.assertFalse(result.parity_ok)
            self.assertIn("duplicate", result.notes)


# ---------------------------------------------------------------------------
# 6. rtnn_kitti_ready — sample truncation contract
# ---------------------------------------------------------------------------

class KittiReadySampleTruncationTest(unittest.TestCase):

    def test_sample_velodyne_dirs_capped_at_five(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for i in range(8):
                velodyne = root / f"seq{i:02d}" / "velodyne"
                velodyne.mkdir(parents=True)
                (velodyne / "000000.bin").write_bytes(b"\x00" * 16)
            report = rt.inspect_kitti_linux_source_root(root)
            self.assertLessEqual(len(report.sample_velodyne_dirs), 5)
            self.assertLessEqual(len(report.sample_bin_files), 5)
            # But full counts are correct
            self.assertEqual(report.velodyne_dir_count, 8)
            self.assertEqual(report.velodyne_bin_count, 8)

    def test_report_status_ready_when_bin_files_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            velodyne = root / "seq" / "velodyne"
            velodyne.mkdir(parents=True)
            (velodyne / "000000.bin").write_bytes(b"\x00" * 16)
            report = rt.inspect_kitti_linux_source_root(root)
            self.assertEqual(report.current_status, "ready")
            self.assertTrue(report.exists)


if __name__ == "__main__":
    unittest.main()
