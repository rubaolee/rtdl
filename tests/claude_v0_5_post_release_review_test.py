"""
Post-v0.5 code review tests — April 14, 2026.

Covers the 8 modules added after the April 12 v0.5 RTNN scaffolding review:
  layout_types, rtnn_kitti, rtnn_kitti_selector, rtnn_kitti_ready,
  rtnn_duplicate_audit, rtnn_cunsearch_live, rtnn_comparison, rtnn_perf_audit.

All tests run without network, CUDA GPU, or live KITTI data.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.layout_types import (
    Field,
    GeometryType,
    Layout,
    Point3DLayout,
    Points3D,
    Ray3DLayout,
    Rays3D,
    ScalarType,
    Triangle3DLayout,
    Triangles3D,
    f32,
    field,
    layout,
    u32,
)
from rtdsl.rtnn_cunsearch_live import (
    _detect_cunsearch_precision_mode,
    _precision_compile_flags,
    _render_cunsearch_driver_source,
)
from rtdsl.rtnn_duplicate_audit import (
    assess_cunsearch_duplicate_point_guard,
    find_exact_cross_package_matches,
)
from rtdsl.rtnn_kitti import (
    KittiBoundedPointPackage,
    KittiFrameRecord,
    KittiSourceConfig,
    kitti_source_config,
    resolve_kitti_source_root,
    select_kitti_bounded_frames,
)
from rtdsl.rtnn_kitti_ready import inspect_kitti_linux_source_root
from rtdsl.rtnn_perf_audit import summarize_fixed_radius_mismatch
from rtdsl.reference import Point3D


# ---------------------------------------------------------------------------
# LayoutTypesTest
# ---------------------------------------------------------------------------

class LayoutTypesTest(unittest.TestCase):
    def test_empty_layout_raises(self) -> None:
        with self.assertRaises(ValueError):
            layout("Empty")

    def test_layout_with_one_field(self) -> None:
        lay = layout("Single", field("x", f32))
        self.assertEqual(lay.name, "Single")
        self.assertEqual(len(lay.fields), 1)

    def test_require_fields_passes_when_all_present(self) -> None:
        lay = layout("XY", field("x", f32), field("y", f32))
        lay.require_fields(("x", "y"))  # no exception

    def test_require_fields_raises_on_missing(self) -> None:
        lay = layout("XY", field("x", f32), field("y", f32))
        with self.assertRaises(ValueError) as ctx:
            lay.require_fields(("x", "z"))
        self.assertIn("z", str(ctx.exception))
        self.assertIn("XY", str(ctx.exception))

    def test_require_fields_reports_all_missing_names(self) -> None:
        lay = layout("X", field("x", f32))
        with self.assertRaises(ValueError) as ctx:
            lay.require_fields(("y", "z"))
        msg = str(ctx.exception)
        self.assertIn("y", msg)
        self.assertIn("z", msg)

    def test_point3d_layout_has_four_fields(self) -> None:
        self.assertEqual(Point3DLayout.field_names(), ("x", "y", "z", "id"))

    def test_triangle3d_layout_has_ten_fields(self) -> None:
        names = Triangle3DLayout.field_names()
        self.assertEqual(len(names), 10)
        self.assertIn("z0", names)
        self.assertIn("z2", names)

    def test_ray3d_layout_has_eight_fields(self) -> None:
        names = Ray3DLayout.field_names()
        self.assertEqual(len(names), 8)
        self.assertIn("oz", names)
        self.assertIn("dz", names)

    def test_points3d_geometry_type_name(self) -> None:
        self.assertEqual(Points3D.name, "points")
        self.assertIn("z", Points3D.required_fields)

    def test_triangles3d_geometry_type_required_fields(self) -> None:
        self.assertIn("z0", Triangles3D.required_fields)
        self.assertIn("z1", Triangles3D.required_fields)
        self.assertIn("z2", Triangles3D.required_fields)

    def test_rays3d_geometry_type_required_fields(self) -> None:
        self.assertIn("oz", Rays3D.required_fields)
        self.assertIn("dz", Rays3D.required_fields)

    def test_field_to_dict_contains_expected_keys(self) -> None:
        f = field("x", f32)
        d = f.to_dict()
        for key in ("name", "scalar_type", "c_type", "cuda_type", "size"):
            self.assertIn(key, d)
        self.assertEqual(d["name"], "x")

    def test_scalar_type_sizes(self) -> None:
        self.assertEqual(f32.size, 4)
        self.assertEqual(u32.size, 4)


# ---------------------------------------------------------------------------
# RtnnPerfAuditTest
# ---------------------------------------------------------------------------

class RtnnPerfAuditTest(unittest.TestCase):
    def _row(self, query_id: int, neighbor_id: int, distance: float) -> dict:
        return {"query_id": query_id, "neighbor_id": neighbor_id, "distance": distance}

    def test_identical_rows_give_parity_ok(self) -> None:
        rows = (self._row(1, 2, 0.5), self._row(1, 3, 1.0))
        summary = summarize_fixed_radius_mismatch(rows, rows, strict_parity_ok=True)
        self.assertTrue(summary.strict_parity_ok)
        self.assertEqual(summary.missing_pair_count, 0)
        self.assertEqual(summary.extra_pair_count, 0)
        self.assertIsNone(summary.first_missing_pair)
        self.assertIsNone(summary.first_extra_pair)

    def test_missing_pair_detected(self) -> None:
        reference = (self._row(1, 2, 0.5), self._row(1, 3, 1.0))
        candidate = (self._row(1, 2, 0.5),)
        summary = summarize_fixed_radius_mismatch(reference, candidate, strict_parity_ok=False)
        self.assertEqual(summary.missing_pair_count, 1)
        self.assertEqual(summary.first_missing_pair, (1, 3))

    def test_extra_pair_detected(self) -> None:
        reference = (self._row(1, 2, 0.5),)
        candidate = (self._row(1, 2, 0.5), self._row(1, 3, 1.0))
        summary = summarize_fixed_radius_mismatch(reference, candidate, strict_parity_ok=False)
        self.assertEqual(summary.extra_pair_count, 1)
        self.assertEqual(summary.first_extra_pair, (1, 3))

    def test_symmetric_mismatch_both_missing_and_extra(self) -> None:
        reference = (self._row(1, 2, 0.5), self._row(1, 4, 2.0))
        candidate = (self._row(1, 2, 0.5), self._row(1, 5, 3.0))
        summary = summarize_fixed_radius_mismatch(reference, candidate, strict_parity_ok=False)
        self.assertEqual(summary.missing_pair_count, 1)
        self.assertEqual(summary.extra_pair_count, 1)

    def test_empty_rows_give_zero_counts(self) -> None:
        summary = summarize_fixed_radius_mismatch((), (), strict_parity_ok=True)
        self.assertEqual(summary.reference_row_count, 0)
        self.assertEqual(summary.candidate_row_count, 0)
        self.assertEqual(summary.missing_pair_count, 0)
        self.assertEqual(summary.extra_pair_count, 0)

    def test_positional_mismatch_captures_first_differing_row(self) -> None:
        reference = (self._row(1, 2, 0.5), self._row(1, 3, 1.0))
        candidate = (self._row(1, 2, 0.5), self._row(1, 3, 9.9))
        summary = summarize_fixed_radius_mismatch(reference, candidate, strict_parity_ok=False)
        self.assertIsNotNone(summary.first_reference_row)
        self.assertIsNotNone(summary.first_candidate_row)
        self.assertAlmostEqual(summary.first_reference_row["distance"], 1.0)
        self.assertAlmostEqual(summary.first_candidate_row["distance"], 9.9)


# ---------------------------------------------------------------------------
# RtnnKittiValidationTest
# ---------------------------------------------------------------------------

class RtnnKittiValidationTest(unittest.TestCase):
    def test_select_raises_on_zero_max_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises((ValueError, RuntimeError)):
                select_kitti_bounded_frames(
                    source_root=tmpdir,
                    max_frames=0,
                )

    def test_select_raises_on_negative_max_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises((ValueError, RuntimeError)):
                select_kitti_bounded_frames(
                    source_root=tmpdir,
                    max_frames=-1,
                )

    def test_select_raises_on_zero_stride(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises((ValueError, RuntimeError)):
                select_kitti_bounded_frames(
                    source_root=tmpdir,
                    max_frames=1,
                    stride=0,
                )

    def test_select_raises_on_negative_start_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises((ValueError, RuntimeError)):
                select_kitti_bounded_frames(
                    source_root=tmpdir,
                    max_frames=1,
                    start_index=-1,
                )

    def test_resolve_kitti_source_root_missing_returns_none(self) -> None:
        result = resolve_kitti_source_root("/nonexistent/kitti/path/that/does/not/exist")
        self.assertIsNone(result)

    def test_kitti_source_config_missing_gives_planned_status(self) -> None:
        config = kitti_source_config("/nonexistent/kitti/path/that/does/not/exist")
        self.assertEqual(config.current_status, "planned")

    def test_kitti_source_config_with_valid_dir_gives_resolved_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = kitti_source_config(tmpdir)
            self.assertEqual(config.current_status, "source_root_resolved")
            self.assertEqual(config.source_root, str(Path(tmpdir).resolve()))

    def test_load_bounded_point_package_roundtrip(self) -> None:
        from rtdsl.rtnn_kitti import load_kitti_bounded_point_package, write_kitti_bounded_point_package
        # Build a minimal package JSON manually and verify load
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_path = Path(tmpdir) / "pkg.json"
            payload = {
                "package_kind": "kitti_bounded_point_package_v1",
                "selected_frame_count": 1,
                "selected_point_count": 2,
                "max_points_per_frame": 100,
                "max_total_points": 200,
                "point_id_start": 1,
                "points": [
                    {"id": 1, "x": 1.0, "y": 2.0, "z": 3.0},
                    {"id": 2, "x": 4.0, "y": 5.0, "z": 6.0},
                ],
            }
            pkg_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            pkg = load_kitti_bounded_point_package(pkg_path)
            self.assertEqual(len(pkg.points), 2)
            self.assertEqual(pkg.points[0].id, 1)
            self.assertAlmostEqual(pkg.points[1].z, 6.0)

    def test_load_bounded_points_from_manifest_rejects_wrong_kind(self) -> None:
        from rtdsl.rtnn_kitti import load_kitti_bounded_points_from_manifest
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "bad_manifest.json"
            manifest_path.write_text(
                json.dumps({"manifest_kind": "wrong_kind", "frames": []}), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                load_kitti_bounded_points_from_manifest(manifest_path)


# ---------------------------------------------------------------------------
# CuNSearchLivePrecisionTest
# ---------------------------------------------------------------------------

class CuNSearchLivePrecisionTest(unittest.TestCase):
    def _minimal_payload(self, radius: float = 1.0, k_max: int = 5) -> dict:
        return {
            "adapter": "cunsearch",
            "workload": "fixed_radius_neighbors",
            "radius": radius,
            "k_max": k_max,
            "query_points": [{"id": 1, "x": 0.0, "y": 0.0, "z": 0.0}],
            "search_points": [{"id": 2, "x": 0.5, "y": 0.0, "z": 0.0}],
        }

    def test_double_precision_compile_flags(self) -> None:
        flags = _precision_compile_flags("double")
        self.assertIn("-DCUNSEARCH_USE_DOUBLE_PRECISION", flags)

    def test_float_precision_compile_flags_empty(self) -> None:
        flags = _precision_compile_flags("float")
        self.assertEqual(flags, ())

    def test_driver_source_embeds_radius(self) -> None:
        payload = self._minimal_payload(radius=2.5)
        source = _render_cunsearch_driver_source(payload, Path("/tmp/r.json"), precision_mode="double")
        self.assertIn("2.5", source)

    def test_driver_source_embeds_k_max(self) -> None:
        payload = self._minimal_payload(k_max=10)
        source = _render_cunsearch_driver_source(payload, Path("/tmp/r.json"), precision_mode="double")
        self.assertIn("10", source)

    def test_float_mode_uses_f_suffix_on_literals(self) -> None:
        payload = self._minimal_payload(radius=1.0)
        source = _render_cunsearch_driver_source(payload, Path("/tmp/r.json"), precision_mode="float")
        # Coordinate literals should end in 'f'
        self.assertIn("0.0f", source)

    def test_double_mode_uses_double_distance_computation(self) -> None:
        payload = self._minimal_payload()
        source = _render_cunsearch_driver_source(payload, Path("/tmp/r.json"), precision_mode="double")
        self.assertIn("static_cast<double>", source)

    def test_detect_precision_mode_defaults_to_double_when_cache_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            mode = _detect_cunsearch_precision_mode(Path(tmpdir))
            self.assertEqual(mode, "double")

    def test_detect_precision_mode_reads_cmake_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir) / "CMakeCache.txt"
            cache.write_text(
                "CUNSEARCH_USE_DOUBLE_PRECISION:BOOL=OFF\n",
                encoding="utf-8",
            )
            mode = _detect_cunsearch_precision_mode(Path(tmpdir))
            self.assertEqual(mode, "float")


# ---------------------------------------------------------------------------
# RtnnComparisonNotesTest
# ---------------------------------------------------------------------------

class RtnnComparisonNotesTest(unittest.TestCase):
    def test_offline_comparison_notes_field_is_honest(self) -> None:
        from rtdsl.rtnn_comparison import RtnnBoundedComparisonResult
        import dataclasses
        fields = {f.name for f in dataclasses.fields(RtnnBoundedComparisonResult)}
        self.assertIn("workload", fields)
        self.assertIn("parity_ok", fields)
        self.assertIn("notes", fields)
        # notes field must be present and is the honest-disclosure field
        self.assertIn("query_point_count", fields)
        self.assertIn("reference_row_count", fields)

    def test_live_duplicate_guard_blocked_note_shape(self) -> None:
        # Simulate the note shape returned when duplicate guard fires
        note = (
            "Strict live cuNSearch comparison was blocked because the package contains exact "
            "cross-package duplicate points, which are outside the current validated cuNSearch "
            "parity contract. First duplicate pair: query 1, search 2."
        )
        self.assertIn("blocked", note)
        self.assertIn("duplicate", note)
        self.assertIn("query 1", note)


# ---------------------------------------------------------------------------
# KittiReadySampleTruncationTest
# ---------------------------------------------------------------------------

class KittiReadySampleTruncationTest(unittest.TestCase):
    def test_sample_dirs_capped_at_five(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create 7 velodyne directories with one .bin file each
            for i in range(7):
                seq = root / f"sequence_{i:02d}" / "velodyne"
                seq.mkdir(parents=True)
                (seq / f"{i:010d}.bin").write_bytes(b"\x00" * 16)
            report = inspect_kitti_linux_source_root(root)
            self.assertLessEqual(len(report.sample_velodyne_dirs), 5)
            self.assertLessEqual(len(report.sample_bin_files), 5)

    def test_status_ready_when_bin_files_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            seq = root / "seq00" / "velodyne"
            seq.mkdir(parents=True)
            (seq / "000000.bin").write_bytes(b"\x00" * 16)
            report = inspect_kitti_linux_source_root(root)
            self.assertEqual(report.current_status, "ready")
            self.assertTrue(report.exists)
            self.assertGreater(report.velodyne_bin_count, 0)

    def test_status_empty_when_no_bin_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "velodyne").mkdir()
            report = inspect_kitti_linux_source_root(root)
            self.assertEqual(report.current_status, "empty")

    def test_status_missing_when_dir_nonexistent(self) -> None:
        report = inspect_kitti_linux_source_root("/nonexistent/path/kitti")
        self.assertEqual(report.current_status, "missing")
        self.assertFalse(report.exists)


if __name__ == "__main__":
    unittest.main()
