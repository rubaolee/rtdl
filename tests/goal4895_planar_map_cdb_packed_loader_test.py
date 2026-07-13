import json
import os
import tempfile
import unittest
from pathlib import Path

import rtdsl as rt


class Goal4895PlanarMapCdbPackedLoaderTest(unittest.TestCase):
    def test_public_packed_cdb_loader_builds_native_buffers_and_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cdb = root / "tiny.cdb"
            cdb.write_text(
                "\n".join(
                    [
                        "1 3 0 2 11 0",
                        "0.0 0.0",
                        "1.0 0.0",
                        "1.0 1.0",
                        "2 2 3 4 13 0",
                        "2.0 0.0",
                        "2.0 1.0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cache = root / "cache"
            old = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
            os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(cache)
            try:
                first = rt.load_planar_map_cdb_packed_inputs(cdb)
                second = rt.load_planar_map_cdb_packed_inputs(cdb)
            finally:
                if old is None:
                    os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
                else:
                    os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old

            self.assertIsInstance(first, rt.PlanarMapCdbPackedInputs)
            self.assertEqual(2, first.chain_count)
            self.assertEqual(5, first.point_count)
            self.assertEqual(3, first.edge_count)
            self.assertEqual(3, first.lsi_segments.count)
            self.assertEqual(3, first.cdb_segments.count)
            self.assertEqual(5, first.points.count)
            self.assertEqual([0, 3], list(first.chain_offsets))
            self.assertEqual([3, 2], list(first.chain_point_counts))
            self.assertEqual([11, 13], list(first.chain_left_faces))
            self.assertEqual([0, 0], list(first.chain_right_faces))
            self.assertEqual([1, 2, 3], list(first.seg_ids))
            self.assertEqual(2, second.chain_count)
            meta_paths = list(cache.glob("*/meta.json"))
            self.assertTrue(meta_paths)
            meta_path = meta_paths[0]
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(0.0, meta["min_x"])
            self.assertEqual(2.0, meta["max_x"])
            self.assertEqual(0.0, meta["min_y"])
            self.assertEqual(1.0, meta["max_y"])

            for key in ("min_x", "max_x", "min_y", "max_y"):
                meta.pop(key)
            meta_path.write_text(json.dumps(meta, sort_keys=True) + "\n", encoding="utf-8")
            old = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
            os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(cache)
            try:
                third = rt.load_planar_map_cdb_packed_inputs(cdb)
            finally:
                if old is None:
                    os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
                else:
                    os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old
            self.assertEqual(0.0, third.min_x)
            self.assertEqual(2.0, third.max_x)
            backfilled = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(0.0, backfilled["min_x"])
            self.assertEqual(2.0, backfilled["max_x"])
            del first
            del second
            del third


if __name__ == "__main__":
    unittest.main()
