from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.aabb_index import EmbreeAabbIndex2D


ROOT = Path(__file__).resolve().parents[1]


class _FakeNativePreparedAabb:
    native_aabb_index = True

    def __init__(self) -> None:
        self.query_records = None

    def collect_range_intersection_rows(self, query_records):
        self.query_records = tuple(query_records)
        return {
            "candidate_id_rows": ((20, 10), (20, 11)),
            "row_schema": ("query_id", "indexed_id"),
            "complete_candidate_coverage": True,
            "native_generic_symbol": "rtdl_embree_collect_prepared_aabb_index_2d_range_intersection_rows",
        }


class Goal4348EmbreeAabbRowsTest(unittest.TestCase):
    def test_embree_aabb_index_uses_native_prepared_row_collector(self) -> None:
        prepared = _FakeNativePreparedAabb()
        index = EmbreeAabbIndex2D(
            boxes=((0.0, 0.0, 1.0, 1.0), (2.0, 2.0, 3.0, 3.0)),
            prepared=prepared,
            row_ids=(10, 11),
        )

        rows = index.intersection_rows(
            ((0.5, 0.5, 0.75, 0.75),),
            (20,),
        )

        self.assertEqual(((20, 10), (20, 11)), rows)
        self.assertIsNotNone(prepared.query_records)
        self.assertEqual(20, prepared.query_records[0].id)

    def test_embree_native_abi_declares_prepared_aabb_pair_rows(self) -> None:
        prelude = (ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h").read_text(
            encoding="utf-8"
        )
        api = (ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp").read_text(
            encoding="utf-8"
        )
        runtime = (ROOT / "src" / "rtdsl" / "embree_runtime.py").read_text(encoding="utf-8")

        self.assertIn("struct RtdlAabbPairRow", prelude)
        self.assertIn("rtdl_embree_collect_prepared_aabb_index_2d_range_intersection_rows", prelude)
        self.assertIn("aabb_rows_collision_callback", api)
        self.assertIn("_RtdlAabbPairRow", runtime)
        self.assertIn("collect_range_intersection_rows", runtime)


if __name__ == "__main__":
    unittest.main()
