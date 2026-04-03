from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "goal50_postgis_ground_truth.py"
SPEC = importlib.util.spec_from_file_location("goal50_postgis_ground_truth", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal50PostgisGroundTruthTest(unittest.TestCase):
    def test_polygon_wkt_closes_ring(self) -> None:
        wkt = MODULE.polygon_wkt(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)))
        self.assertEqual(wkt, "POLYGON((0.0 0.0,1.0 0.0,1.0 1.0,0.0 0.0))")

    def test_hash_tuples_is_order_insensitive(self) -> None:
        left = MODULE.hash_tuples([(2, 3), (1, 4), (1, 3)])
        right = MODULE.hash_tuples([(1, 3), (2, 3), (1, 4)])
        self.assertEqual(left, right)

    def test_hashing_sink_counts_rows(self) -> None:
        sink = MODULE.HashingSink()
        sink.write("1\t2\n3\t4\n")
        self.assertEqual(sink.row_count, 2)
        self.assertEqual(len(sink.hexdigest), 64)


if __name__ == "__main__":
    unittest.main()
