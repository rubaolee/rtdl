from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal2150OptixShapePairRelationKernelCompileTest(unittest.TestCase):
    def test_shape_pair_relation_intersection_uses_declared_flag(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        self.assertIn("bool segment_pair_intersection_hit = false;", text)
        self.assertNotIn("bool segment_intersection_hit = false;", text)
        self.assertIn("if (segment_pair_intersection_hit) {", text)


if __name__ == "__main__":
    unittest.main()
