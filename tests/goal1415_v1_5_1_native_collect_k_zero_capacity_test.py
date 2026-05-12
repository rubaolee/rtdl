from __future__ import annotations

import ctypes
import unittest
from types import SimpleNamespace
from unittest import mock

from rtdsl import embree_runtime
from rtdsl import optix_runtime


class _PackedPolygons:
    refs = None
    polygon_count = 0
    vertices_xy = None
    vertex_xy_count = 0


def _make_zero_result_symbol(captured):
    def _symbol(
        _left_refs,
        _left_count,
        _left_vertices,
        _left_vertex_count,
        _right_refs,
        _right_count,
        _right_vertices,
        _right_vertex_count,
        candidates_out,
        candidate_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        captured["candidates_out"] = candidates_out
        captured["candidate_capacity"] = candidate_capacity
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = 0
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        return 0

    return _symbol


def _make_duplicate_result_symbol():
    def _symbol(
        _left_refs,
        _left_count,
        _left_vertices,
        _left_vertex_count,
        _right_refs,
        _right_count,
        _right_vertices,
        _right_vertex_count,
        candidates_out,
        _candidate_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        candidates_out[0].left_polygon_id = 1
        candidates_out[0].right_polygon_id = 10
        candidates_out[1].left_polygon_id = 1
        candidates_out[1].right_polygon_id = 10
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = 2
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        return 0

    return _symbol


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


class Goal1415V151NativeCollectKZeroCapacityTest(unittest.TestCase):
    def test_embree_wrapper_allows_zero_capacity_empty_collection(self) -> None:
        captured = {}
        library = SimpleNamespace(
            rtdl_embree_collect_shape_pair_candidates_bounded=_make_zero_result_symbol(captured),
            rtdl_embree_collect_k_bounded_i64=_make_generic_collect_k_symbol(),
        )

        with mock.patch.object(embree_runtime, "pack_polygons", return_value=_PackedPolygons()), \
             mock.patch.object(embree_runtime, "_load_embree_library", return_value=library):
            result = embree_runtime.collect_polygon_pair_candidates_bounded_embree(
                (),
                (),
                candidate_capacity=0,
            )

        self.assertIsNone(captured["candidates_out"])
        self.assertEqual(captured["candidate_capacity"], 0)
        self.assertEqual(result["capacity"], 0)
        self.assertEqual(result["valid_count"], 0)
        self.assertEqual(result["candidate_id_rows"], ())
        self.assertEqual(result["candidate_pairs"], ())

    def test_optix_wrapper_allows_zero_capacity_empty_collection(self) -> None:
        captured = {}
        library = SimpleNamespace(
            rtdl_optix_collect_shape_pair_candidates_bounded=_make_zero_result_symbol(captured),
            rtdl_optix_collect_k_bounded_i64=_make_generic_collect_k_symbol(),
        )

        with mock.patch.object(optix_runtime, "pack_polygons", return_value=_PackedPolygons()), \
             mock.patch.object(optix_runtime, "_load_optix_library", return_value=library):
            result = optix_runtime.collect_polygon_pair_candidates_bounded_optix(
                (),
                (),
                candidate_capacity=0,
            )

        self.assertIsNone(captured["candidates_out"])
        self.assertEqual(captured["candidate_capacity"], 0)
        self.assertEqual(result["capacity"], 0)
        self.assertEqual(result["valid_count"], 0)
        self.assertEqual(result["candidate_id_rows"], ())
        self.assertEqual(result["candidate_pairs"], ())

    def test_negative_capacity_remains_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_capacity must be non-negative"):
            embree_runtime.collect_polygon_pair_candidates_bounded_embree((), (), candidate_capacity=-1)

        with self.assertRaisesRegex(ValueError, "candidate_capacity must be non-negative"):
            optix_runtime.collect_polygon_pair_candidates_bounded_optix((), (), candidate_capacity=-1)

    def test_embree_wrapper_canonicalizes_duplicate_native_rows_through_generic_symbol(self) -> None:
        library = SimpleNamespace(
            rtdl_embree_collect_shape_pair_candidates_bounded=_make_duplicate_result_symbol(),
            rtdl_embree_collect_k_bounded_i64=_make_generic_collect_k_symbol(),
        )

        with mock.patch.object(embree_runtime, "pack_polygons", return_value=_PackedPolygons()), \
             mock.patch.object(embree_runtime, "_load_embree_library", return_value=library):
            result = embree_runtime.collect_polygon_pair_candidates_bounded_embree(
                (),
                (),
                candidate_capacity=2,
            )

        self.assertEqual(result["candidate_id_rows"], ((1, 10),))
        self.assertEqual(result["emitted_count"], 1)
        self.assertEqual(result["native_emitted_count"], 2)
        self.assertEqual(result["native_generic_symbol"], "rtdl_embree_collect_k_bounded_i64")

    def test_optix_wrapper_canonicalizes_duplicate_native_rows_through_generic_symbol(self) -> None:
        library = SimpleNamespace(
            rtdl_optix_collect_shape_pair_candidates_bounded=_make_duplicate_result_symbol(),
            rtdl_optix_collect_k_bounded_i64=_make_generic_collect_k_symbol(),
        )

        with mock.patch.object(optix_runtime, "pack_polygons", return_value=_PackedPolygons()), \
             mock.patch.object(optix_runtime, "_load_optix_library", return_value=library):
            result = optix_runtime.collect_polygon_pair_candidates_bounded_optix(
                (),
                (),
                candidate_capacity=2,
            )

        self.assertEqual(result["candidate_id_rows"], ((1, 10),))
        self.assertEqual(result["emitted_count"], 1)
        self.assertEqual(result["native_emitted_count"], 2)
        self.assertEqual(result["native_generic_symbol"], "rtdl_optix_collect_k_bounded_i64")


if __name__ == "__main__":
    unittest.main()
