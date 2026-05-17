from __future__ import annotations

import pathlib
import unittest

from rtdsl.reference import Polygon
from rtdsl.reference import overlay_compose_cpu


ROOT = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "src" / "rtdsl" / "reference.py"


class Goal2175OverlayReferencePairSetMaterializationTest(unittest.TestCase):
    def test_overlay_reference_preserves_lsi_and_pip_flags(self) -> None:
        left = (
            Polygon(id=1, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
            Polygon(id=2, vertices=((10.0, 10.0), (12.0, 10.0), (12.0, 12.0), (10.0, 12.0))),
        )
        right = (
            Polygon(id=10, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),
            Polygon(id=11, vertices=((0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75))),
        )

        rows = {
            (int(row["left_polygon_id"]), int(row["right_polygon_id"])): (
                int(row["requires_lsi"]),
                int(row["requires_pip"]),
            )
            for row in overlay_compose_cpu(left, right)
        }

        self.assertEqual(rows[(1, 10)], (1, 0))
        self.assertEqual(rows[(1, 11)], (0, 1))
        self.assertEqual(rows[(2, 10)], (0, 0))
        self.assertEqual(rows[(2, 11)], (0, 0))

    def test_overlay_reference_uses_pair_sets_not_repeated_hit_scans(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")

        self.assertIn("lsi_pairs = {", text)
        self.assertIn("pip_pairs = {", text)
        self.assertIn("pair = (int(left_polygon.id), int(right_polygon.id))", text)
        self.assertNotIn("for hit in (*left_in_right, *right_in_left)", text)


if __name__ == "__main__":
    unittest.main()
