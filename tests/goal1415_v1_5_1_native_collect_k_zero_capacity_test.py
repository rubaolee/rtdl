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


class Goal1415V151NativeCollectKZeroCapacityTest(unittest.TestCase):
    def test_embree_wrapper_allows_zero_capacity_empty_collection(self) -> None:
        captured = {}
        library = SimpleNamespace(
            rtdl_embree_collect_polygon_pair_candidates_bounded=_make_zero_result_symbol(captured)
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
            rtdl_optix_collect_polygon_pair_candidates_bounded=_make_zero_result_symbol(captured)
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

    def test_embree_wrapper_validates_native_result_metadata(self) -> None:
        library = SimpleNamespace(
            rtdl_embree_collect_polygon_pair_candidates_bounded=_make_duplicate_result_symbol()
        )

        with mock.patch.object(embree_runtime, "pack_polygons", return_value=_PackedPolygons()), \
             mock.patch.object(embree_runtime, "_load_embree_library", return_value=library):
            with self.assertRaisesRegex(ValueError, "emitted_count metadata mismatch"):
                embree_runtime.collect_polygon_pair_candidates_bounded_embree(
                    (),
                    (),
                    candidate_capacity=2,
                )

    def test_optix_wrapper_validates_native_result_metadata(self) -> None:
        library = SimpleNamespace(
            rtdl_optix_collect_polygon_pair_candidates_bounded=_make_duplicate_result_symbol()
        )

        with mock.patch.object(optix_runtime, "pack_polygons", return_value=_PackedPolygons()), \
             mock.patch.object(optix_runtime, "_load_optix_library", return_value=library):
            with self.assertRaisesRegex(ValueError, "emitted_count metadata mismatch"):
                optix_runtime.collect_polygon_pair_candidates_bounded_optix(
                    (),
                    (),
                    candidate_capacity=2,
                )


if __name__ == "__main__":
    unittest.main()
