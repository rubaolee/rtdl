from __future__ import annotations

import ctypes
import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt
from rtdsl.optix_runtime import _RtdlAabb2D
from rtdsl.optix_runtime import pack_aabbs_2d_columns


ROOT = Path(__file__).resolve().parents[1]


class Goal5487GenericAabbColumnarFrontdoorTest(unittest.TestCase):
    def _columns(self) -> rt.Aabb2DColumns:
        return rt.Aabb2DColumns.from_mapping(
            {
                "id": np.asarray([10, 20], dtype=np.uint32),
                "min_x": np.asarray([0.0, 5.0]),
                "min_y": np.asarray([0.0, 5.0]),
                "max_x": np.asarray([2.0, 7.0]),
                "max_y": np.asarray([2.0, 7.0]),
            }
        )

    def test_cpu_reference_consumes_generic_columns_without_app_identity(self):
        index = rt.prepare_aabb_index_2d_columns(
            self._columns(),
            point_queries=((1.0, 1.0), (6.0, 6.0), (3.0, 3.0)),
            backend="cpu",
        )
        result = index.count(
            point_queries=((1.0, 1.0), (6.0, 6.0), (3.0, 3.0)),
            operation="point_contains",
        )
        self.assertEqual(result["counts"]["point_contains"], 2)
        self.assertEqual(len(index.boxes), 2)

    def test_column_pack_matches_native_abi_and_retains_owner(self):
        columns = self._columns()
        packed = pack_aabbs_2d_columns(columns)
        self.assertEqual(packed.count, 2)
        self.assertIsNotNone(packed.owner)
        self.assertEqual(ctypes.sizeof(_RtdlAabb2D), 40)
        self.assertEqual(len(packed.records), 2)
        self.assertEqual(packed.records[0].id, 10)
        self.assertEqual(packed.records[1].min_x, 5.0)
        self.assertEqual(packed.records[1].max_y, 7.0)

    def test_columns_fail_closed_on_length_mismatch(self):
        with self.assertRaises(ValueError):
            rt.Aabb2DColumns.from_mapping(
                {
                    "min_x": [0.0, 1.0],
                    "min_y": [0.0],
                    "max_x": [1.0, 2.0],
                    "max_y": [1.0, 2.0],
                }
            )

    def test_columns_fail_closed_on_out_of_range_ids(self):
        with self.assertRaises(ValueError):
            rt.Aabb2DColumns.from_mapping(
                {
                    "id": [-1],
                    "min_x": [0.0],
                    "min_y": [0.0],
                    "max_x": [1.0],
                    "max_y": [1.0],
                }
            )

    def test_new_core_surface_is_app_neutral(self):
        source = (ROOT / "src" / "rtdsl" / "aabb_columns.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("librts", source)
        self.assertNotIn("figure 6", source)
        self.assertNotIn("paper", source)


if __name__ == "__main__":
    unittest.main()
