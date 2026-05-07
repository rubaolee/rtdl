from __future__ import annotations

import unittest
import ctypes
from unittest import mock

import rtdsl as rt
from rtdsl import embree_runtime


def _polygons():
    return (
        rt.Polygon(1, ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))),
        rt.Polygon(2, ((2.0, 0.0), (3.0, 0.0), (3.0, 1.0), (2.0, 1.0))),
    )


def _make_generic_collect_k_symbol():
    def _symbol(
        candidate_rows,
        candidate_count,
        row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        rows = []
        for row_index in range(int(candidate_count)):
            start = row_index * int(row_width)
            rows.append(
                tuple(int(candidate_rows[start + column]) for column in range(int(row_width)))
            )
        normalized = tuple(sorted(set(rows)))
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = len(normalized)
        overflowed = len(normalized) > int(row_capacity)
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1 if overflowed else 0
        if overflowed:
            return 0
        for row_index, row in enumerate(normalized):
            for column, value in enumerate(row):
                rows_out[row_index * int(row_width) + column] = value
        return 0

    return _symbol


class Goal1316V15EmbreeCandidateCollectionSurfaceTest(unittest.TestCase):
    def test_embree_collection_requires_current_native_export(self) -> None:
        with mock.patch.object(embree_runtime, "_load_embree_library", return_value=object()):
            with self.assertRaisesRegex(ValueError, "rtdl_embree_collect_polygon_pair_candidates_bounded"):
                rt.collect_polygon_pair_candidates_bounded_embree(
                    _polygons(),
                    _polygons(),
                    candidate_capacity=8,
                )

    def test_embree_collection_returns_same_contract_metadata_as_optix(self) -> None:
        class FakeLibrary:
            pass

        def fake_symbol(
            _left_refs,
            _left_count,
            _left_vertices_xy,
            _left_vertex_xy_count,
            _right_refs,
            _right_count,
            _right_vertices_xy,
            _right_vertex_xy_count,
            candidates_out,
            _candidate_capacity,
            emitted_count_out,
            overflowed_out,
            _error_out,
            _error_size,
        ):
            candidates_out[0].left_polygon_id = 2
            candidates_out[0].right_polygon_id = 11
            candidates_out[1].left_polygon_id = 1
            candidates_out[1].right_polygon_id = 10
            emitted_count_out._obj.value = 2
            overflowed_out._obj.value = 0
            return 0

        library = FakeLibrary()
        library.rtdl_embree_collect_polygon_pair_candidates_bounded = fake_symbol
        library.rtdl_embree_collect_k_bounded_i64 = _make_generic_collect_k_symbol()
        with mock.patch.object(embree_runtime, "_load_embree_library", return_value=library):
            result = rt.collect_polygon_pair_candidates_bounded_embree(
                _polygons(),
                _polygons(),
                candidate_capacity=8,
            )

        self.assertEqual(result["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(result["backend"], "embree")
        self.assertEqual(result["candidate_pairs"], ((1, 10), (2, 11)))
        self.assertEqual(result["capacity"], 8)
        self.assertEqual(result["emitted_count"], 2)
        self.assertFalse(result["overflowed"])
        self.assertTrue(result["complete_candidate_coverage"])
        self.assertEqual(result["failure_mode"], "fail_closed_overflow")
        self.assertEqual(result["overflow_policy"], "fail_closed_before_result_materialization")

    def test_embree_collection_overflow_fails_closed(self) -> None:
        class FakeLibrary:
            pass

        def fake_overflow_symbol(
            _left_refs,
            _left_count,
            _left_vertices_xy,
            _left_vertex_xy_count,
            _right_refs,
            _right_count,
            _right_vertices_xy,
            _right_vertex_xy_count,
            _candidates_out,
            _candidate_capacity,
            emitted_count_out,
            overflowed_out,
            _error_out,
            _error_size,
        ):
            emitted_count_out._obj.value = 9
            overflowed_out._obj.value = 1
            return 0

        library = FakeLibrary()
        library.rtdl_embree_collect_polygon_pair_candidates_bounded = fake_overflow_symbol
        library.rtdl_embree_collect_k_bounded_i64 = _make_generic_collect_k_symbol()
        with mock.patch.object(embree_runtime, "_load_embree_library", return_value=library):
            with self.assertRaisesRegex(RuntimeError, "fail_closed_overflow"):
                rt.collect_polygon_pair_candidates_bounded_embree(
                    _polygons(),
                    _polygons(),
                    candidate_capacity=4,
                )

    def test_embree_collection_rejects_negative_capacity(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_capacity must be non-negative"):
            rt.collect_polygon_pair_candidates_bounded_embree(
                _polygons(),
                _polygons(),
                candidate_capacity=-1,
            )


if __name__ == "__main__":
    unittest.main()
