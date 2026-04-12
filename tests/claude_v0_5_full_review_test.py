"""
Comprehensive review test suite for v0.5 work introduced in commits
17a775e..917bcdc (2026-04-12).

Covers:
  1. Point3D geometry type and layout
  2. _point_distance_sq helper (2D/3D generalisation)
  3. bounded_knn_rows API factory (validation, options)
  4. bounded_knn_rows_cpu reference implementation (edge cases, ordering)
  5. bounded_knn_rows via run_cpu_python_reference (kernel path)
  6. bounded_knn_rows vs fixed_radius_neighbors output-shape distinction
  7. bounded_knn_rows oracle path (run_cpu)
  8. rtnn_reproduction module (datasets, targets, local profiles, filters)
  9. rtnn_baselines module (libraries, decisions, filters)
  10. rtnn_matrix module (cross-product logic, status classification)
  11. rtnn_manifests module (lookup, write, roundtrip JSON)
  12. rtnn_cunsearch adapter skeleton (resolution, config, plan, write)
  13. goal187 video-link regression check
  14. __init__ exports for all new public symbols
  15. run_cpu rejection of Point3D with honest error message
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
import rtdsl.reference as _ref

_point_distance_sq = _ref._point_distance_sq
Point = rt.Point
Point3D = rt.Point3D


# ---------------------------------------------------------------------------
# Kernel fixtures used across multiple test classes
# ---------------------------------------------------------------------------

@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_2d_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def frn_2d_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


# ---------------------------------------------------------------------------
# 1. Point3D geometry type and layout
# ---------------------------------------------------------------------------

class Point3DTypeTest(unittest.TestCase):

    def test_point3d_layout_field_names(self) -> None:
        self.assertEqual(rt.Point3DLayout.field_names(), ("x", "y", "z", "id"))

    def test_point3d_layout_name(self) -> None:
        self.assertEqual(rt.Point3DLayout.name, "Point3D")

    def test_points3d_required_fields(self) -> None:
        self.assertEqual(rt.Points3D.required_fields, ("x", "y", "z", "id"))

    def test_points3d_geometry_name(self) -> None:
        self.assertEqual(rt.Points3D.name, "points")

    def test_point3d_dataclass_is_frozen(self) -> None:
        p = rt.Point3D(id=1, x=1.0, y=2.0, z=3.0)
        with self.assertRaises(AttributeError):
            p.x = 9.0  # type: ignore[misc]

    def test_point3d_equality(self) -> None:
        p1 = rt.Point3D(id=1, x=1.0, y=2.0, z=3.0)
        p2 = rt.Point3D(id=1, x=1.0, y=2.0, z=3.0)
        p3 = rt.Point3D(id=2, x=1.0, y=2.0, z=3.0)
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)

    def test_point3d_z_field_distinguishes_from_point2d(self) -> None:
        p2d = Point(id=1, x=1.0, y=2.0)
        p3d = rt.Point3D(id=1, x=1.0, y=2.0, z=0.0)
        self.assertNotEqual(type(p2d), type(p3d))
        self.assertFalse(hasattr(p2d, "z"))
        self.assertEqual(p3d.z, 0.0)

    def test_point3d_exported_from_rtdsl(self) -> None:
        self.assertIs(rt.Point3D, _ref.Point3D)


# ---------------------------------------------------------------------------
# 2. _point_distance_sq helper
# ---------------------------------------------------------------------------

class PointDistanceSqTest(unittest.TestCase):

    def test_zero_distance_2d(self) -> None:
        p = Point(id=1, x=3.0, y=4.0)
        self.assertEqual(_point_distance_sq(p, p), 0.0)

    def test_unit_vector_2d(self) -> None:
        a = Point(id=1, x=0.0, y=0.0)
        b = Point(id=2, x=1.0, y=0.0)
        self.assertAlmostEqual(_point_distance_sq(a, b), 1.0)

    def test_pythagorean_triple_2d(self) -> None:
        a = Point(id=1, x=0.0, y=0.0)
        b = Point(id=2, x=3.0, y=4.0)
        self.assertAlmostEqual(_point_distance_sq(a, b), 25.0)

    def test_unit_vector_3d_z_axis(self) -> None:
        a = Point3D(id=1, x=0.0, y=0.0, z=0.0)
        b = Point3D(id=2, x=0.0, y=0.0, z=1.0)
        self.assertAlmostEqual(_point_distance_sq(a, b), 1.0)

    def test_3d_diagonal_distance(self) -> None:
        a = Point3D(id=1, x=0.0, y=0.0, z=0.0)
        b = Point3D(id=2, x=1.0, y=1.0, z=1.0)
        self.assertAlmostEqual(_point_distance_sq(a, b), 3.0)

    def test_2d_point_z_defaults_to_zero(self) -> None:
        # When a 2D Point is paired with a 3D Point the z component of the 2D
        # point is treated as 0.0 via getattr fallback.
        a = Point(id=1, x=0.0, y=0.0)
        b = Point3D(id=2, x=0.0, y=0.0, z=1.0)
        self.assertAlmostEqual(_point_distance_sq(a, b), 1.0)

    def test_symmetry(self) -> None:
        a = Point3D(id=1, x=1.0, y=2.0, z=3.0)
        b = Point3D(id=2, x=4.0, y=6.0, z=3.0)
        self.assertAlmostEqual(_point_distance_sq(a, b), _point_distance_sq(b, a))


# ---------------------------------------------------------------------------
# 3. bounded_knn_rows API factory
# ---------------------------------------------------------------------------

class BoundedKnnRowsApiTest(unittest.TestCase):

    def test_valid_predicate_has_correct_name(self) -> None:
        p = rt.bounded_knn_rows(radius=1.0, k_max=3)
        self.assertEqual(p.name, "bounded_knn_rows")

    def test_valid_predicate_stores_options(self) -> None:
        p = rt.bounded_knn_rows(radius=0.5, k_max=2)
        self.assertEqual(p.options["radius"], 0.5)
        self.assertEqual(p.options["k_max"], 2)

    def test_radius_zero_is_valid(self) -> None:
        p = rt.bounded_knn_rows(radius=0.0, k_max=1)
        self.assertEqual(p.options["radius"], 0.0)

    def test_negative_radius_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded_knn_rows radius must be non-negative"):
            rt.bounded_knn_rows(radius=-0.001, k_max=1)

    def test_zero_k_max_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded_knn_rows k_max must be positive"):
            rt.bounded_knn_rows(radius=1.0, k_max=0)

    def test_negative_k_max_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded_knn_rows k_max must be positive"):
            rt.bounded_knn_rows(radius=1.0, k_max=-1)

    def test_radius_coerced_to_float(self) -> None:
        p = rt.bounded_knn_rows(radius=1, k_max=1)  # type: ignore[arg-type]
        self.assertIsInstance(p.options["radius"], float)

    def test_k_max_coerced_to_int(self) -> None:
        p = rt.bounded_knn_rows(radius=1.0, k_max=3)
        self.assertIsInstance(p.options["k_max"], int)

    def test_exported_from_rtdsl(self) -> None:
        self.assertTrue(callable(rt.bounded_knn_rows))


# ---------------------------------------------------------------------------
# 4. bounded_knn_rows_cpu reference implementation
# ---------------------------------------------------------------------------

_Q2D = (Point(id=100, x=0.0, y=0.0), Point(id=101, x=3.0, y=0.0))
_S2D = (
    Point(id=1, x=0.0, y=0.0),
    Point(id=2, x=0.3, y=0.0),
    Point(id=3, x=-0.3, y=0.0),
    Point(id=4, x=3.2, y=0.0),
    Point(id=5, x=4.0, y=0.0),   # too far from both queries at radius=0.5
)


class BoundedKnnRowsCpuTest(unittest.TestCase):

    def test_basic_2d_radius_filter(self) -> None:
        rows = rt.bounded_knn_rows_cpu(_Q2D, _S2D, radius=0.5, k_max=10)
        neighbor_ids = {r["neighbor_id"] for r in rows if r["query_id"] == 100}
        # id=5 is 4.0 away from q=100 → excluded; id=4 is 3.0 away → excluded
        self.assertEqual(neighbor_ids, {1, 2, 3})

    def test_k_max_truncation(self) -> None:
        rows = rt.bounded_knn_rows_cpu(_Q2D, _S2D, radius=10.0, k_max=2)
        q100_rows = [r for r in rows if r["query_id"] == 100]
        self.assertLessEqual(len(q100_rows), 2)

    def test_neighbor_rank_is_1_based(self) -> None:
        rows = rt.bounded_knn_rows_cpu(_Q2D, _S2D, radius=0.5, k_max=10)
        q100_rows = sorted([r for r in rows if r["query_id"] == 100], key=lambda r: r["neighbor_rank"])
        self.assertEqual(q100_rows[0]["neighbor_rank"], 1)

    def test_ordering_by_distance_within_query(self) -> None:
        rows = rt.bounded_knn_rows_cpu(_Q2D, _S2D, radius=0.5, k_max=10)
        q100_rows = [r for r in rows if r["query_id"] == 100]
        distances = [r["distance"] for r in q100_rows]
        self.assertEqual(distances, sorted(distances))

    def test_tie_breaking_by_neighbor_id(self) -> None:
        # id=2 and id=3 both have distance=0.3 from q=100
        rows = rt.bounded_knn_rows_cpu(_Q2D, _S2D, radius=0.5, k_max=10)
        q100_rows = [r for r in rows if r["query_id"] == 100]
        d03_rows = [r for r in q100_rows if math.isclose(r["distance"], 0.3)]
        self.assertEqual(len(d03_rows), 2)
        self.assertLess(d03_rows[0]["neighbor_id"], d03_rows[1]["neighbor_id"])

    def test_output_sorted_by_query_id(self) -> None:
        rows = rt.bounded_knn_rows_cpu(_Q2D, _S2D, radius=10.0, k_max=5)
        query_ids = [r["query_id"] for r in rows]
        self.assertEqual(query_ids, sorted(query_ids))

    def test_empty_result_when_no_neighbors_in_radius(self) -> None:
        q = (Point(id=1, x=100.0, y=100.0),)
        s = (Point(id=2, x=0.0, y=0.0),)
        rows = rt.bounded_knn_rows_cpu(q, s, radius=0.1, k_max=5)
        self.assertEqual(rows, ())

    def test_neighbor_rank_matches_distance_order(self) -> None:
        rows = rt.bounded_knn_rows_cpu(_Q2D, _S2D, radius=0.5, k_max=10)
        q100 = [r for r in rows if r["query_id"] == 100]
        for i, row in enumerate(q100, start=1):
            self.assertEqual(row["neighbor_rank"], i)

    def test_3d_basic(self) -> None:
        q = (Point3D(id=10, x=0.0, y=0.0, z=0.0),)
        s = (
            Point3D(id=1, x=0.0, y=0.0, z=0.3),
            Point3D(id=2, x=0.0, y=0.0, z=0.8),
            Point3D(id=3, x=0.0, y=0.0, z=1.5),  # outside radius=1.0
        )
        rows = rt.bounded_knn_rows_cpu(q, s, radius=1.0, k_max=5)
        self.assertEqual(tuple(r["neighbor_id"] for r in rows), (1, 2))
        self.assertEqual(tuple(r["neighbor_rank"] for r in rows), (1, 2))

    def test_query_with_no_search_points(self) -> None:
        q = (Point(id=1, x=0.0, y=0.0),)
        rows = rt.bounded_knn_rows_cpu(q, (), radius=1.0, k_max=5)
        self.assertEqual(rows, ())

    def test_exported_from_rtdsl(self) -> None:
        self.assertTrue(callable(rt.bounded_knn_rows_cpu))


# ---------------------------------------------------------------------------
# 5. bounded_knn_rows via run_cpu_python_reference (full kernel path)
# ---------------------------------------------------------------------------

class BoundedKnnRunCpuPythonReferenceTest(unittest.TestCase):

    def test_2d_kernel_basic(self) -> None:
        rows = rt.run_cpu_python_reference(
            bounded_knn_2d_kernel,
            query_points=_Q2D,
            search_points=_S2D,
        )
        # radius=1.0, k_max=3 → q100 gets ids 1,2,3; q101 gets id 4
        q100_ids = tuple(r["neighbor_id"] for r in rows if r["query_id"] == 100)
        self.assertEqual(set(q100_ids), {1, 2, 3})

    def test_3d_kernel_basic(self) -> None:
        rows = rt.run_cpu_python_reference(
            bounded_knn_3d_kernel,
            query_points=(rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),),
            search_points=(
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),
                rt.Point3D(id=3, x=0.0, y=0.0, z=2.0),
            ),
        )
        self.assertEqual(tuple(r["neighbor_id"] for r in rows), (1, 2))

    def test_neighbor_rank_field_is_emitted(self) -> None:
        rows = rt.run_cpu_python_reference(
            bounded_knn_2d_kernel,
            query_points=(Point(id=1, x=0.0, y=0.0),),
            search_points=(Point(id=2, x=0.2, y=0.0),),
        )
        self.assertIn("neighbor_rank", rows[0])

    def test_result_is_tuple_of_dicts(self) -> None:
        rows = rt.run_cpu_python_reference(
            bounded_knn_2d_kernel,
            query_points=(Point(id=1, x=0.0, y=0.0),),
            search_points=(Point(id=2, x=0.2, y=0.0),),
        )
        self.assertIsInstance(rows, tuple)
        self.assertIsInstance(rows[0], dict)


# ---------------------------------------------------------------------------
# 6. bounded_knn_rows vs fixed_radius_neighbors output-shape distinction
# ---------------------------------------------------------------------------

class BoundedKnnVsFrnShapeTest(unittest.TestCase):
    """
    bounded_knn_rows adds neighbor_rank; fixed_radius_neighbors does not.
    Both share the radius filter.
    """

    _QUERY = (Point(id=1, x=0.0, y=0.0),)
    _SEARCH = (
        Point(id=10, x=0.2, y=0.0),
        Point(id=11, x=0.5, y=0.0),
        Point(id=12, x=2.0, y=0.0),  # outside radius=1.0
    )

    def test_bounded_knn_has_neighbor_rank_frn_does_not(self) -> None:
        bknn = rt.run_cpu_python_reference(
            bounded_knn_2d_kernel,
            query_points=self._QUERY,
            search_points=self._SEARCH,
        )
        frn = rt.run_cpu_python_reference(
            frn_2d_kernel,
            query_points=self._QUERY,
            search_points=self._SEARCH,
        )
        self.assertIn("neighbor_rank", bknn[0])
        self.assertNotIn("neighbor_rank", frn[0])

    def test_both_respect_radius_filter(self) -> None:
        bknn = rt.run_cpu_python_reference(
            bounded_knn_2d_kernel,
            query_points=self._QUERY,
            search_points=self._SEARCH,
        )
        frn = rt.run_cpu_python_reference(
            frn_2d_kernel,
            query_points=self._QUERY,
            search_points=self._SEARCH,
        )
        bknn_ids = {r["neighbor_id"] for r in bknn}
        frn_ids = {r["neighbor_id"] for r in frn}
        # id=12 is outside radius=1.0; both should exclude it
        self.assertNotIn(12, bknn_ids)
        self.assertNotIn(12, frn_ids)
        self.assertEqual(bknn_ids, frn_ids)

    def test_predicate_names_are_distinct(self) -> None:
        bknn_pred = rt.bounded_knn_rows(radius=1.0, k_max=3)
        frn_pred = rt.fixed_radius_neighbors(radius=1.0, k_max=3)
        self.assertNotEqual(bknn_pred.name, frn_pred.name)
        self.assertEqual(bknn_pred.name, "bounded_knn_rows")
        self.assertEqual(frn_pred.name, "fixed_radius_neighbors")


# ---------------------------------------------------------------------------
# 7. bounded_knn_rows oracle path (run_cpu)
# ---------------------------------------------------------------------------

class BoundedKnnOracleTest(unittest.TestCase):

    def test_run_cpu_matches_reference_for_bounded_knn_rows(self) -> None:
        case = {
            "query_points": _Q2D,
            "search_points": _S2D,
        }
        # kernel uses radius=1.0, k_max=3
        expected = rt.run_cpu_python_reference(bounded_knn_2d_kernel, **case)
        actual = rt.run_cpu(bounded_knn_2d_kernel, **case)
        self.assertEqual(actual, expected)

    def test_run_cpu_rejects_point3d_with_clear_message(self) -> None:
        with self.assertRaisesRegex(ValueError, "run_cpu currently supports only 2D"):
            rt.run_cpu(
                bounded_knn_3d_kernel,
                query_points=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
                search_points=(rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),),
            )


# ---------------------------------------------------------------------------
# 8. rtnn_reproduction module
# ---------------------------------------------------------------------------

class RtnnReproductionTest(unittest.TestCase):

    def test_three_dataset_families_exist(self) -> None:
        families = rt.rtnn_dataset_families()
        self.assertEqual(len(families), 3)

    def test_dataset_handles_are_unique(self) -> None:
        handles = [f.handle for f in rt.rtnn_dataset_families()]
        self.assertEqual(len(handles), len(set(handles)))

    def test_all_families_are_3d(self) -> None:
        for family in rt.rtnn_dataset_families():
            self.assertEqual(family.dimensionality, "3d")

    def test_handle_filter_returns_one(self) -> None:
        result = rt.rtnn_dataset_families(handle="kitti_velodyne_point_sets")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].handle, "kitti_velodyne_point_sets")

    def test_unknown_handle_returns_empty(self) -> None:
        result = rt.rtnn_dataset_families(handle="nonexistent_handle")
        self.assertEqual(result, ())

    def test_experiment_targets_cover_three_artifacts(self) -> None:
        artifacts = {t.artifact for t in rt.rtnn_experiment_targets()}
        self.assertIn("dataset_packaging", artifacts)
        self.assertIn("paper_matrix", artifacts)
        self.assertIn("comparison_matrix", artifacts)

    def test_bounded_knn_rows_referenced_in_targets(self) -> None:
        targets = rt.rtnn_experiment_targets()
        all_workloads = "|".join(t.workload for t in targets)
        self.assertIn("bounded_knn_rows", all_workloads)

    def test_local_profiles_exist_for_each_family(self) -> None:
        # Each dataset family must have a corresponding local profile,
        # linked via the manifest's bounded_profile_id.
        families = rt.rtnn_dataset_families()
        manifests = rt.rtnn_bounded_dataset_manifests()
        profiles_by_id = {p.profile_id: p for p in rt.rtnn_local_profiles()}
        for family in families:
            manifest = next((m for m in manifests if m.dataset_handle == family.handle), None)
            self.assertIsNotNone(manifest, msg=f"No manifest for {family.handle}")
            self.assertIn(manifest.bounded_profile_id, profiles_by_id,
                          msg=f"profile_id {manifest.bounded_profile_id!r} not found for {family.handle}")

    def test_artifact_filter_on_experiment_targets(self) -> None:
        packaging = rt.rtnn_experiment_targets(artifact="dataset_packaging")
        for t in packaging:
            self.assertEqual(t.artifact, "dataset_packaging")

    def test_reproduction_tier_filter(self) -> None:
        bounded = rt.rtnn_experiment_targets(reproduction_tier="bounded_reproduction")
        for t in bounded:
            self.assertEqual(t.reproduction_tier, "bounded_reproduction")

    def test_local_profile_workload_filter(self) -> None:
        profiles = rt.rtnn_local_profiles(workload="bounded_knn_rows")
        self.assertGreater(len(profiles), 0)
        for p in profiles:
            self.assertIn("bounded_knn_rows", p.workload)

    def test_rtnn_dataset_family_is_frozen(self) -> None:
        fam = rt.rtnn_dataset_families(handle="kitti_velodyne_point_sets")[0]
        with self.assertRaises(AttributeError):
            fam.dimensionality = "2d"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 9. rtnn_baselines module
# ---------------------------------------------------------------------------

class RtnnBaselinesTest(unittest.TestCase):

    def test_six_baseline_libraries_exist(self) -> None:
        libs = rt.rtnn_baseline_libraries()
        self.assertEqual(len(libs), 6)

    def test_library_handles_are_unique(self) -> None:
        handles = [lib.handle for lib in rt.rtnn_baseline_libraries()]
        self.assertEqual(len(handles), len(set(handles)))

    def test_cunsearch_is_first_prioritized_adapter(self) -> None:
        decisions = rt.rtnn_baseline_decisions(verdict="prioritize_first_adapter")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].library_handle, "cunsearch")

    def test_existing_baselines_are_online_or_bounded(self) -> None:
        # postgis and scipy are the two already-online baselines
        online = rt.rtnn_baseline_libraries(current_status="online_2d_only")
        handles = {lib.handle for lib in online}
        self.assertEqual(handles, {"postgis", "scipy_ckdtree"})

    def test_pcl_octree_is_deferred(self) -> None:
        decisions = rt.rtnn_baseline_decisions(library_handle="pcl_octree")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].verdict, "defer_until_packaging_plan")

    def test_handle_filter(self) -> None:
        result = rt.rtnn_baseline_libraries(handle="frnn")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].handle, "frnn")

    def test_decisions_cover_all_libraries(self) -> None:
        lib_handles = {lib.handle for lib in rt.rtnn_baseline_libraries()}
        decision_handles = {d.library_handle for d in rt.rtnn_baseline_decisions()}
        self.assertTrue(decision_handles.issubset(lib_handles))

    def test_library_is_frozen_dataclass(self) -> None:
        lib = rt.rtnn_baseline_libraries(handle="cunsearch")[0]
        with self.assertRaises(AttributeError):
            lib.current_status = "online"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 10. rtnn_matrix module
# ---------------------------------------------------------------------------

class RtnnReproductionMatrixTest(unittest.TestCase):

    def test_matrix_is_non_empty(self) -> None:
        entries = rt.rtnn_reproduction_matrix()
        self.assertGreater(len(entries), 0)

    def test_entries_have_expected_fields(self) -> None:
        entry = rt.rtnn_reproduction_matrix()[0]
        for field in ("artifact", "dataset_handle", "dataset_label", "workload",
                      "reproduction_tier", "baseline_handle", "baseline_label",
                      "matrix_status", "notes"):
            self.assertTrue(hasattr(entry, field), msg=f"missing field: {field}")

    def test_dataset_packaging_excludes_nonpaper_baselines(self) -> None:
        packaging = rt.rtnn_reproduction_matrix(artifact="dataset_packaging")
        for entry in packaging:
            self.assertNotIn(entry.baseline_handle, {"postgis", "scipy_ckdtree"},
                             msg="non-paper baselines must not appear in dataset_packaging matrix")

    def test_comparison_matrix_exposes_nonpaper_rows(self) -> None:
        comparison = rt.rtnn_reproduction_matrix(artifact="comparison_matrix")
        handles = {e.baseline_handle for e in comparison}
        # comparison matrix should include non-paper baselines
        self.assertTrue(handles & {"postgis", "scipy_ckdtree"},
                        msg="comparison_matrix must include non-paper baselines")

    def test_exact_reproduction_candidates_are_blocked(self) -> None:
        paper = rt.rtnn_reproduction_matrix(artifact="paper_matrix")
        for entry in paper:
            if entry.reproduction_tier == "exact_reproduction_candidate":
                self.assertEqual(entry.matrix_status, "blocked_on_exact_dataset_and_adapter")

    def test_bounded_reproduction_entries_are_planned(self) -> None:
        entries = rt.rtnn_reproduction_matrix()
        bounded = [e for e in entries if e.reproduction_tier == "bounded_reproduction"
                   and e.baseline_handle not in {"postgis", "scipy_ckdtree"}]
        for entry in bounded:
            self.assertEqual(entry.matrix_status, "planned_bounded_matrix")

    def test_artifact_filter_works(self) -> None:
        packaging = rt.rtnn_reproduction_matrix(artifact="dataset_packaging")
        for entry in packaging:
            self.assertEqual(entry.artifact, "dataset_packaging")

    def test_workload_entries_match_library_support(self) -> None:
        # Every matrix entry's workload must be in the baseline library's workload_shape
        libs_by_handle = {lib.handle: lib for lib in rt.rtnn_baseline_libraries()}
        for entry in rt.rtnn_reproduction_matrix():
            lib = libs_by_handle[entry.baseline_handle]
            supported = set(lib.workload_shape.split("|"))
            self.assertIn(entry.workload, supported,
                          msg=f"{entry.baseline_handle} does not support {entry.workload}")


# ---------------------------------------------------------------------------
# 11. rtnn_manifests module
# ---------------------------------------------------------------------------

class RtnnManifestsTest(unittest.TestCase):

    def test_three_manifests_exist(self) -> None:
        manifests = rt.rtnn_bounded_dataset_manifests()
        self.assertEqual(len(manifests), 3)

    def test_manifest_handles_match_dataset_families(self) -> None:
        family_handles = {f.handle for f in rt.rtnn_dataset_families()}
        manifest_handles = {m.dataset_handle for m in rt.rtnn_bounded_dataset_manifests()}
        self.assertEqual(manifest_handles, family_handles)

    def test_all_manifests_have_10min_runtime_budget(self) -> None:
        for manifest in rt.rtnn_bounded_dataset_manifests():
            self.assertIn("10 minutes", manifest.runtime_target)

    def test_handle_filter(self) -> None:
        result = rt.rtnn_bounded_dataset_manifests(dataset_handle="kitti_velodyne_point_sets")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].dataset_handle, "kitti_velodyne_point_sets")

    def test_unknown_handle_returns_empty(self) -> None:
        result = rt.rtnn_bounded_dataset_manifests(dataset_handle="nonexistent")
        self.assertEqual(result, ())

    def test_write_manifest_raises_for_unknown_handle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = Path(tmpdir) / "manifest.json"
            with self.assertRaisesRegex(ValueError, "unknown RTNN bounded dataset manifest handle"):
                rt.write_rtnn_bounded_dataset_manifest("nonexistent_handle", dest)

    def test_write_manifest_produces_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = Path(tmpdir) / "manifest.json"
            returned = rt.write_rtnn_bounded_dataset_manifest(
                "kitti_velodyne_point_sets", dest
            )
            self.assertEqual(returned, dest)
            payload = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(payload["manifest_kind"], "rtnn_bounded_dataset_manifest_v1")
            self.assertIn("dataset", payload)
            self.assertIn("bounded_manifest", payload)
            self.assertIn("local_profile", payload)

    def test_written_manifest_contains_correct_handle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = Path(tmpdir) / "manifest.json"
            rt.write_rtnn_bounded_dataset_manifest("stanford_3d_scan_point_sets", dest)
            payload = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(payload["dataset"]["handle"], "stanford_3d_scan_point_sets")

    def test_parent_directory_is_created_by_writer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = Path(tmpdir) / "nested" / "dir" / "manifest.json"
            rt.write_rtnn_bounded_dataset_manifest("kitti_velodyne_point_sets", dest)
            self.assertTrue(dest.exists())


# ---------------------------------------------------------------------------
# 12. rtnn_cunsearch adapter skeleton
# ---------------------------------------------------------------------------

class RtnnCuNSearchAdapterTest(unittest.TestCase):

    def test_resolve_binary_returns_none_when_unconfigured(self) -> None:
        result = rt.resolve_cunsearch_binary(None)
        self.assertIsNone(result)

    def test_available_returns_false_when_unconfigured(self) -> None:
        self.assertFalse(rt.cunsearch_available(None))

    def test_adapter_config_status_when_unconfigured(self) -> None:
        config = rt.cunsearch_adapter_config(None)
        self.assertIsInstance(config, rt.CuNSearchAdapterConfig)
        self.assertEqual(config.current_status, "planned")

    def test_adapter_config_includes_set_env_instructions(self) -> None:
        config = rt.cunsearch_adapter_config(None)
        self.assertIn("RTDL_CUNSEARCH_BIN", config.notes)

    def test_plan_raises_when_no_binary(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "cuNSearch adapter is not online yet"):
            rt.plan_cunsearch_fixed_radius_neighbors(radius=0.5, k_max=3)

    def test_write_request_raises_when_no_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = Path(tmpdir) / "request.json"
            with self.assertRaises(RuntimeError):
                rt.write_cunsearch_fixed_radius_request(
                    dest,
                    [rt.Point3D(id=1, x=0.0, y=0.0, z=0.0)],
                    [rt.Point3D(id=2, x=0.0, y=0.0, z=0.5)],
                    radius=1.0,
                    k_max=3,
                )

    def test_resolve_binary_returns_none_for_nonexistent_path(self) -> None:
        result = rt.resolve_cunsearch_binary("/nonexistent/path/cunsearch_binary")
        self.assertIsNone(result)

    def test_config_binary_resolved_status_when_binary_exists(self) -> None:
        # Use sys.executable which is guaranteed to exist as a stand-in binary.
        # binary_path is stored as the resolved (symlink-free) path.
        import sys
        from pathlib import Path
        config = rt.cunsearch_adapter_config(sys.executable)
        self.assertEqual(config.current_status, "binary_resolved")
        self.assertEqual(config.binary_path, str(Path(sys.executable).resolve()))

    def test_invocation_plan_fields(self) -> None:
        import sys
        from pathlib import Path
        plan = rt.plan_cunsearch_fixed_radius_neighbors(
            radius=0.5, k_max=3, binary_path=sys.executable
        )
        self.assertIsInstance(plan, rt.CuNSearchInvocationPlan)
        self.assertEqual(plan.workload, "fixed_radius_neighbors")
        self.assertEqual(plan.target_dimension, "3d")
        self.assertEqual(plan.radius, 0.5)
        self.assertEqual(plan.k_max, 3)
        self.assertEqual(plan.request_format, "json_request_v1")

    def test_write_request_produces_valid_json_when_binary_exists(self) -> None:
        import sys
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = Path(tmpdir) / "request.json"
            returned = rt.write_cunsearch_fixed_radius_request(
                dest,
                [rt.Point3D(id=1, x=0.0, y=0.0, z=0.0)],
                [rt.Point3D(id=2, x=0.1, y=0.0, z=0.0)],
                radius=1.0,
                k_max=3,
                binary_path=sys.executable,
            )
            self.assertEqual(returned, dest)
            payload = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(payload["adapter"], "cunsearch")
            self.assertEqual(payload["workload"], "fixed_radius_neighbors")
            self.assertEqual(payload["radius"], 1.0)
            self.assertEqual(payload["k_max"], 3)
            self.assertEqual(len(payload["query_points"]), 1)
            self.assertEqual(len(payload["search_points"]), 1)
            q = payload["query_points"][0]
            self.assertIn("id", q)
            self.assertIn("x", q)
            self.assertIn("y", q)
            self.assertIn("z", q)


# ---------------------------------------------------------------------------
# 13. goal187 video-link regression check
# ---------------------------------------------------------------------------

class StaleGoal187Test(unittest.TestCase):
    """Keep the goal187 video-link assertion aligned with the live 4K front page."""

    REPO_ROOT = Path(__file__).resolve().parents[1]
    OLD_SHORTS_URL = "https://youtube.com/shorts/VnzVWAPln3k?si=O1iet-3uFm2gpPes"
    NEW_4K_URL = "https://youtu.be/d3yJB7AmCLM"

    def test_readme_contains_4k_url_not_shorts_url(self) -> None:
        text = (self.REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(self.NEW_4K_URL, text,
                      msg="README.md must contain the 4K demo URL")
        self.assertNotIn(self.OLD_SHORTS_URL, text,
                         msg="README.md must NOT contain the old Shorts URL — "
                             "goal187_v0_3_audit_test.py line 24 is stale and must be updated")

    def test_goal187_file_references_4k_url(self) -> None:
        goal187_file = self.REPO_ROOT / "tests/goal187_v0_3_audit_test.py"
        text = goal187_file.read_text(encoding="utf-8")
        self.assertIn(self.NEW_4K_URL, text,
                      msg="goal187_v0_3_audit_test.py must check for the 4K URL")
        self.assertNotIn(self.OLD_SHORTS_URL, text,
                         msg="goal187_v0_3_audit_test.py must not keep the old Shorts URL")


# ---------------------------------------------------------------------------
# 14. __init__ exports for all new public symbols
# ---------------------------------------------------------------------------

class NewPublicExportsTest(unittest.TestCase):

    def test_bounded_knn_rows_exported(self) -> None:
        self.assertIn("bounded_knn_rows", dir(rt))

    def test_bounded_knn_rows_cpu_exported(self) -> None:
        self.assertIn("bounded_knn_rows_cpu", dir(rt))

    def test_point3d_exported(self) -> None:
        self.assertIn("Point3D", dir(rt))

    def test_point3d_layout_exported(self) -> None:
        self.assertIn("Point3DLayout", dir(rt))

    def test_points3d_exported(self) -> None:
        self.assertIn("Points3D", dir(rt))

    def test_rtnn_dataset_families_exported(self) -> None:
        self.assertIn("rtnn_dataset_families", dir(rt))

    def test_rtnn_experiment_targets_exported(self) -> None:
        self.assertIn("rtnn_experiment_targets", dir(rt))

    def test_rtnn_local_profiles_exported(self) -> None:
        self.assertIn("rtnn_local_profiles", dir(rt))

    def test_rtnn_baseline_libraries_exported(self) -> None:
        self.assertIn("rtnn_baseline_libraries", dir(rt))

    def test_rtnn_baseline_decisions_exported(self) -> None:
        self.assertIn("rtnn_baseline_decisions", dir(rt))

    def test_rtnn_reproduction_matrix_exported(self) -> None:
        self.assertIn("rtnn_reproduction_matrix", dir(rt))

    def test_rtnn_bounded_dataset_manifests_exported(self) -> None:
        self.assertIn("rtnn_bounded_dataset_manifests", dir(rt))

    def test_write_rtnn_bounded_dataset_manifest_exported(self) -> None:
        self.assertIn("write_rtnn_bounded_dataset_manifest", dir(rt))

    def test_cunsearch_available_exported(self) -> None:
        self.assertIn("cunsearch_available", dir(rt))

    def test_write_cunsearch_fixed_radius_request_exported(self) -> None:
        self.assertIn("write_cunsearch_fixed_radius_request", dir(rt))

    def test_rtnn_dataclass_types_exported(self) -> None:
        for name in ("RtnnDatasetFamily", "RtnnExperimentTarget", "RtnnLocalProfile",
                     "RtnnBaselineLibrary", "RtnnBaselineDecision",
                     "RtnnBoundedDatasetManifest", "RtnnMatrixEntry",
                     "CuNSearchAdapterConfig", "CuNSearchInvocationPlan"):
            self.assertIn(name, dir(rt), msg=f"{name} not exported from rtdsl")


# ---------------------------------------------------------------------------
# 15. run_cpu rejection of Point3D with honest error message
# ---------------------------------------------------------------------------

class Point3DOracleRejectionTest(unittest.TestCase):

    def test_run_cpu_fixed_radius_rejects_point3d(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def frn_3d_k():
            qp = rt.input("query_points", rt.Points3D, role="probe")
            sp = rt.input("search_points", rt.Points3D, role="build")
            c = rt.traverse(qp, sp, accel="bvh")
            hits = rt.refine(c, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=3))
            return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])

        with self.assertRaisesRegex(ValueError, "2D"):
            rt.run_cpu(
                frn_3d_k,
                query_points=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
                search_points=(rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),),
            )

    def test_run_cpu_knn_rows_rejects_point3d(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def knn_3d_k():
            qp = rt.input("query_points", rt.Points3D, role="probe")
            sp = rt.input("search_points", rt.Points3D, role="build")
            c = rt.traverse(qp, sp, accel="bvh")
            hits = rt.refine(c, predicate=rt.knn_rows(k=2))
            return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])

        with self.assertRaisesRegex(ValueError, "2D"):
            rt.run_cpu(
                knn_3d_k,
                query_points=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
                search_points=(rt.Point3D(id=2, x=0.0, y=0.0, z=0.5),),
            )


if __name__ == "__main__":
    unittest.main()
