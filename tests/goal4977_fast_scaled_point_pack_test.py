from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points
from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points_fast_host


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4977FastScaledPointPackTest(unittest.TestCase):
    def test_fast_host_pack_matches_legacy_ctypes_pack(self) -> None:
        ids = np.array([1, 2, 3, 2**32 - 1], dtype=np.uint64)
        x = np.array([1.25, -2.5, 3.75, 0.0], dtype=np.float64)
        y = np.array([-1.0, 2.0, -3.0, 4.0], dtype=np.float64)
        sx = np.array([10, -11, 12, -13], dtype=np.int64)
        sy = np.array([-20, 21, -22, 23], dtype=np.int64)

        legacy = pack_rayjoin_cdb_scaled_points(ids=ids, x=x, y=y, sx=sx, sy=sy)
        fast = pack_rayjoin_cdb_scaled_points_fast_host(ids=ids, x=x, y=y, sx=sx, sy=sy)

        self.assertEqual(legacy.count, fast.count)
        self.assertIsNotNone(fast.owner)
        for index in range(fast.count):
            self.assertEqual(legacy.records[index].id, fast.records[index].id)
            self.assertEqual(legacy.records[index].x, fast.records[index].x)
            self.assertEqual(legacy.records[index].y, fast.records[index].y)
            self.assertEqual(legacy.records[index].sx, fast.records[index].sx)
            self.assertEqual(legacy.records[index].sy, fast.records[index].sy)

    def test_fast_host_pack_rejects_bad_ids(self) -> None:
        with self.assertRaises(ValueError):
            pack_rayjoin_cdb_scaled_points_fast_host(
                ids=np.array([2**32], dtype=np.uint64),
                x=np.array([0.0]),
                y=np.array([0.0]),
                sx=np.array([0], dtype=np.int64),
                sy=np.array([0], dtype=np.int64),
            )

    def test_app_route_is_explicitly_host_pack_not_device_resident_claim(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn("--fast-scaled-point-pack", app)
        self.assertIn("pack_rayjoin_cdb_scaled_points_fast_host", app)
        self.assertIn("fast_scaled_point_pack_requested", app)
        self.assertIn("fast_scaled_point_pack_device_resident_claim_authorized", app)
        self.assertIn("not a device-resident prepared-points claim", app)


if __name__ == "__main__":
    unittest.main()
