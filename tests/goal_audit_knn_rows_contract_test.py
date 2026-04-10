"""
knn_rows contract audit tests.

Covers semantics not exercised by goal204/goal205:
- empty search -> no rows, no crash
- k > len(search) -> emit only available rows, no padding
- neighbor_rank is 1-based and contiguous within each query group
- tie-breaking by neighbor_id ascending at equal distance
- out-of-order query_id input -> output sorted by query_id
- API validation: k=0 and k<0 raise ValueError
- distance field accuracy
- Python / oracle parity on tie and overflow cases
- baseline_contracts validation error paths
"""
from __future__ import annotations

import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from rtdsl.baseline_contracts import validate_compiled_kernel_against_baseline
from rtdsl.reference import Point
from rtdsl.reference import knn_rows_cpu


def _python_rows(query_points, search_points, *, k):
    return knn_rows_cpu(
        tuple(query_points),
        tuple(search_points),
        k=k,
    )


def _oracle_rows(query_points, search_points, *, k):
    @rt.kernel(backend="rtdl", precision="float_approx")
    def _kernel():
        qp = rt.input("query_points", rt.Points, role="probe")
        sp = rt.input("search_points", rt.Points, role="build")
        candidates = rt.traverse(qp, sp, accel="bvh")
        hits = rt.refine(candidates, predicate=rt.knn_rows(k=k))
        return rt.emit(
            hits,
            fields=["query_id", "neighbor_id", "distance", "neighbor_rank"],
        )

    return rt.run_cpu(
        _kernel,
        query_points=tuple(query_points),
        search_points=tuple(search_points),
    )


class KnnEmptyInputTest(unittest.TestCase):
    """k-NN with empty search produces no rows; no crash."""

    def test_empty_search_produces_no_rows(self) -> None:
        rows = _python_rows(
            [Point(id=1, x=0.0, y=0.0)],
            [],
            k=3,
        )
        self.assertEqual(rows, ())

    def test_empty_query_produces_no_rows(self) -> None:
        rows = _python_rows(
            [],
            [Point(id=1, x=0.0, y=0.0)],
            k=3,
        )
        self.assertEqual(rows, ())

    def test_both_empty_produces_no_rows(self) -> None:
        rows = _python_rows([], [], k=1)
        self.assertEqual(rows, ())

    def test_oracle_empty_search_matches_python(self) -> None:
        python = _python_rows([Point(id=1, x=0.0, y=0.0)], [], k=3)
        native = _oracle_rows([Point(id=1, x=0.0, y=0.0)], [], k=3)
        self.assertEqual(python, ())
        self.assertEqual(len(native), 0)

    def test_oracle_empty_query_matches_python(self) -> None:
        python = _python_rows([], [Point(id=1, x=0.0, y=0.0)], k=3)
        native = _oracle_rows([], [Point(id=1, x=0.0, y=0.0)], k=3)
        self.assertEqual(python, ())
        self.assertEqual(len(native), 0)


class KnnShortSearchTest(unittest.TestCase):
    """k > len(search): emit only available rows, no padding."""

    def test_k_larger_than_search_returns_all_available(self) -> None:
        rows = _python_rows(
            [Point(id=1, x=0.0, y=0.0)],
            [Point(id=10, x=1.0, y=0.0)],
            k=5,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["neighbor_id"], 10)
        self.assertEqual(rows[0]["neighbor_rank"], 1)

    def test_no_padding_row_when_k_exceeds_search(self) -> None:
        rows = _python_rows(
            [Point(id=1, x=0.0, y=0.0)],
            [Point(id=10, x=1.0, y=0.0), Point(id=20, x=2.0, y=0.0)],
            k=10,
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["neighbor_rank"], 1)
        self.assertEqual(rows[1]["neighbor_rank"], 2)

    def test_oracle_short_search_matches_python(self) -> None:
        python = _python_rows(
            [Point(id=1, x=0.0, y=0.0)],
            [Point(id=10, x=1.0, y=0.0)],
            k=5,
        )
        native = _oracle_rows(
            [Point(id=1, x=0.0, y=0.0)],
            [Point(id=10, x=1.0, y=0.0)],
            k=5,
        )
        self.assertEqual(len(python), 1)
        self.assertEqual(len(native), len(python))
        self.assertEqual(native[0]["neighbor_rank"], 1)


class KnnNeighborRankTest(unittest.TestCase):
    """neighbor_rank is 1-based, contiguous, and per-query-group."""

    def test_ranks_start_at_one(self) -> None:
        rows = _python_rows(
            [Point(id=1, x=0.0, y=0.0)],
            [
                Point(id=10, x=0.1, y=0.0),
                Point(id=20, x=0.3, y=0.0),
                Point(id=30, x=0.5, y=0.0),
            ],
            k=3,
        )
        self.assertEqual(tuple(r["neighbor_rank"] for r in rows), (1, 2, 3))

    def test_ranks_reset_per_query_group(self) -> None:
        rows = _python_rows(
            [Point(id=1, x=0.0, y=0.0), Point(id=2, x=10.0, y=0.0)],
            [Point(id=10, x=0.1, y=0.0), Point(id=20, x=10.1, y=0.0)],
            k=2,
        )
        query1_rows = [r for r in rows if r["query_id"] == 1]
        query2_rows = [r for r in rows if r["query_id"] == 2]
        self.assertEqual(query1_rows[0]["neighbor_rank"], 1)
        self.assertEqual(query2_rows[0]["neighbor_rank"], 1)

    def test_oracle_ranks_match_python(self) -> None:
        query = [Point(id=1, x=0.0, y=0.0)]
        search = [
            Point(id=10, x=0.1, y=0.0),
            Point(id=20, x=0.3, y=0.0),
            Point(id=30, x=0.5, y=0.0),
        ]
        python = _python_rows(query, search, k=3)
        native = _oracle_rows(query, search, k=3)
        self.assertEqual(len(python), 3)
        self.assertEqual(len(native), 3)
        for p, n in zip(python, native):
            self.assertEqual(p["neighbor_rank"], n["neighbor_rank"])


class KnnTieBreakingTest(unittest.TestCase):
    """Equal distances are broken by neighbor_id ascending."""

    def test_equal_distance_broken_by_neighbor_id_asc(self) -> None:
        query = [Point(id=1, x=0.0, y=0.0)]
        search = [
            Point(id=30, x=0.5, y=0.0),
            Point(id=10, x=-0.5, y=0.0),
        ]
        rows = _python_rows(query, search, k=2)
        self.assertEqual(rows[0]["neighbor_id"], 10)
        self.assertEqual(rows[1]["neighbor_id"], 30)
        self.assertEqual(rows[0]["neighbor_rank"], 1)
        self.assertEqual(rows[1]["neighbor_rank"], 2)

    def test_tie_at_k_boundary_lower_id_wins(self) -> None:
        query = [Point(id=1, x=0.0, y=0.0)]
        search = [
            Point(id=10, x=0.1, y=0.0),
            Point(id=20, x=0.5, y=0.0),
            Point(id=30, x=-0.5, y=0.0),
        ]
        rows = _python_rows(query, search, k=2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["neighbor_id"], 10)
        self.assertEqual(rows[1]["neighbor_id"], 20)

    def test_oracle_tie_breaking_matches_python(self) -> None:
        query = [Point(id=1, x=0.0, y=0.0)]
        search = [
            Point(id=30, x=0.5, y=0.0),
            Point(id=10, x=-0.5, y=0.0),
        ]
        python = _python_rows(query, search, k=2)
        native = _oracle_rows(query, search, k=2)
        self.assertEqual(len(python), 2)
        self.assertEqual(len(native), 2)
        self.assertEqual(python[0]["neighbor_id"], native[0]["neighbor_id"])
        self.assertEqual(python[1]["neighbor_id"], native[1]["neighbor_id"])


class KnnRowOrderingTest(unittest.TestCase):
    """Output rows are sorted by query_id asc, then distance asc."""

    def test_out_of_order_query_ids_sorted_in_output(self) -> None:
        query = [Point(id=5, x=10.0, y=0.0), Point(id=2, x=0.0, y=0.0)]
        search = [Point(id=1, x=0.2, y=0.0), Point(id=2, x=10.1, y=0.0)]
        rows = _python_rows(query, search, k=1)
        self.assertGreaterEqual(len(rows), 2)
        query_ids = [r["query_id"] for r in rows]
        self.assertEqual(query_ids, sorted(query_ids))

    def test_oracle_ordering_matches_python(self) -> None:
        query = [Point(id=5, x=10.0, y=0.0), Point(id=2, x=0.0, y=0.0)]
        search = [Point(id=1, x=0.2, y=0.0), Point(id=2, x=10.1, y=0.0)]
        python = _python_rows(query, search, k=1)
        native = _oracle_rows(query, search, k=1)
        self.assertEqual(len(python), len(native))
        for p, n in zip(python, native):
            self.assertEqual(p["query_id"], n["query_id"])
            self.assertEqual(p["neighbor_id"], n["neighbor_id"])


class KnnApiValidationTest(unittest.TestCase):
    """DSL API rejects invalid k values."""

    def test_k_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            rt.knn_rows(k=0)

    def test_k_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            rt.knn_rows(k=-1)

    def test_k_one_does_not_raise(self) -> None:
        predicate = rt.knn_rows(k=1)
        self.assertEqual(predicate.options["k"], 1)

    def test_k_large_does_not_raise(self) -> None:
        predicate = rt.knn_rows(k=1000)
        self.assertEqual(predicate.options["k"], 1000)


class KnnDistanceFieldTest(unittest.TestCase):
    """Emitted distance is an accurate Euclidean distance."""

    def test_distance_3_4_5_triangle(self) -> None:
        rows = _python_rows(
            [Point(id=1, x=0.0, y=0.0)],
            [Point(id=10, x=3.0, y=4.0)],
            k=1,
        )
        self.assertEqual(len(rows), 1)
        self.assertTrue(math.isclose(rows[0]["distance"], 5.0, rel_tol=1e-12))

    def test_distance_zero_for_coincident(self) -> None:
        rows = _python_rows(
            [Point(id=1, x=1.5, y=2.5)],
            [Point(id=10, x=1.5, y=2.5)],
            k=1,
        )
        self.assertEqual(rows[0]["distance"], 0.0)

    def test_oracle_distance_matches_python(self) -> None:
        query = [Point(id=1, x=0.0, y=0.0)]
        search = [Point(id=10, x=3.0, y=4.0), Point(id=20, x=1.0, y=0.0)]
        python = _python_rows(query, search, k=2)
        native = _oracle_rows(query, search, k=2)
        self.assertEqual(len(python), 2)
        self.assertEqual(len(native), 2)
        for p, n in zip(python, native):
            self.assertTrue(
                math.isclose(
                    p["distance"],
                    n["distance"],
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ),
                f"distance mismatch: python={p['distance']} oracle={n['distance']}",
            )


class BaselineContractsValidationErrorsTest(unittest.TestCase):
    """validate_compiled_kernel_against_baseline rejects mismatched kernels."""

    def test_wrong_predicate_raises(self) -> None:
        from examples.reference.rtdl_fixed_radius_neighbors_reference import (
            fixed_radius_neighbors_reference,
        )

        with self.assertRaises(ValueError):
            validate_compiled_kernel_against_baseline(
                rt.compile_kernel(fixed_radius_neighbors_reference),
                "knn_rows",
            )

    def test_wrong_emit_fields_raises(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def _bad_knn():
            qp = rt.input("query_points", rt.Points, role="probe")
            sp = rt.input("search_points", rt.Points, role="build")
            candidates = rt.traverse(qp, sp, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.knn_rows(k=3))
            return rt.emit(hits, fields=["query_id", "neighbor_id"])

        with self.assertRaises(ValueError):
            validate_compiled_kernel_against_baseline(rt.compile_kernel(_bad_knn), "knn_rows")

    def test_wrong_role_raises(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def _wrong_role():
            qp = rt.input("query_points", rt.Points, role="build")
            sp = rt.input("search_points", rt.Points, role="probe")
            candidates = rt.traverse(sp, qp, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.knn_rows(k=3))
            return rt.emit(
                hits,
                fields=["query_id", "neighbor_id", "distance", "neighbor_rank"],
            )

        with self.assertRaises(ValueError):
            validate_compiled_kernel_against_baseline(rt.compile_kernel(_wrong_role), "knn_rows")

    def test_compare_baseline_rows_different_lengths(self) -> None:
        from rtdsl.baseline_contracts import compare_baseline_rows

        self.assertFalse(
            compare_baseline_rows(
                "knn_rows",
                ({"query_id": 1, "neighbor_id": 2, "distance": 0.5, "neighbor_rank": 1},),
                (),
            )
        )

    def test_compare_baseline_rows_different_neighbor_id(self) -> None:
        from rtdsl.baseline_contracts import compare_baseline_rows

        self.assertFalse(
            compare_baseline_rows(
                "knn_rows",
                ({"query_id": 1, "neighbor_id": 2, "distance": 0.5, "neighbor_rank": 1},),
                ({"query_id": 1, "neighbor_id": 3, "distance": 0.5, "neighbor_rank": 1},),
            )
        )

    def test_compare_baseline_rows_distance_within_tolerance(self) -> None:
        from rtdsl.baseline_contracts import compare_baseline_rows

        self.assertTrue(
            compare_baseline_rows(
                "knn_rows",
                ({"query_id": 1, "neighbor_id": 2, "distance": 1.0, "neighbor_rank": 1},),
                (
                    {
                        "query_id": 1,
                        "neighbor_id": 2,
                        "distance": 1.0 + 5e-7,
                        "neighbor_rank": 1,
                    },
                ),
            )
        )

    def test_compare_baseline_rows_distance_exceeds_tolerance(self) -> None:
        from rtdsl.baseline_contracts import compare_baseline_rows

        self.assertFalse(
            compare_baseline_rows(
                "knn_rows",
                ({"query_id": 1, "neighbor_id": 2, "distance": 1.0, "neighbor_rank": 1},),
                ({"query_id": 1, "neighbor_id": 2, "distance": 1.1, "neighbor_rank": 1},),
            )
        )


class ExternalBaselineEdgeCasesTest(unittest.TestCase):
    """Edge cases for SciPy and PostGIS baselines."""

    def test_scipy_knn_empty_search_returns_empty(self) -> None:
        rows = rt.run_scipy_knn_rows(
            (rt.Point(id=1, x=0.0, y=0.0),),
            (),
            k=3,
            tree_factory=list,
        )
        self.assertEqual(rows, ())

    def test_scipy_frn_zero_radius_no_match(self) -> None:
        class _NoMatchTree:
            def __init__(self, coords):
                pass

            def query_ball_point(self, point, r):
                return []

        rows = rt.run_scipy_fixed_radius_neighbors(
            (rt.Point(id=1, x=0.0, y=0.0),),
            (rt.Point(id=10, x=1.0, y=0.0),),
            radius=0.0,
            k_max=5,
            tree_factory=_NoMatchTree,
        )
        self.assertEqual(rows, ())

    def test_connect_postgis_raises_without_dsn(self) -> None:
        import os

        env_backup = os.environ.pop("RTDL_POSTGIS_DSN", None)
        try:
            with self.assertRaises(RuntimeError):
                rt.connect_postgis()
        finally:
            if env_backup is not None:
                os.environ["RTDL_POSTGIS_DSN"] = env_backup

    def test_scipy_available_does_not_raise(self) -> None:
        result = rt.scipy_available()
        self.assertIsInstance(result, bool)

    def test_postgis_available_does_not_raise(self) -> None:
        result = rt.postgis_available()
        self.assertIsInstance(result, bool)

    def test_frn_scipy_secondary_distance_check_filters_candidates(self) -> None:
        class _AllReturningTree:
            def __init__(self, coords):
                self._n = len(list(coords))

            def query_ball_point(self, point, r):
                return list(range(self._n))

        search = (
            rt.Point(id=1, x=0.4, y=0.0),
            rt.Point(id=2, x=0.9, y=0.0),
        )
        rows = rt.run_scipy_fixed_radius_neighbors(
            (rt.Point(id=10, x=0.0, y=0.0),),
            search,
            radius=0.5,
            k_max=5,
            tree_factory=_AllReturningTree,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["neighbor_id"], 1)


if __name__ == "__main__":
    unittest.main()
