from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal3257ClosedShapeSinglePassPredicateTest(unittest.TestCase):
    def _point_in_polygon_body(self) -> str:
        text = CORE.read_text(encoding="utf-8")
        start = text.index("static __forceinline__ __device__ bool point_in_polygon(")
        end = text.index("extern \"C\" __global__ void __raygen__pip_probe()", start)
        return text[start:end]

    def test_device_predicate_keeps_inclusive_boundary_logic(self) -> None:
        body = self._point_in_polygon_body()

        self.assertIn("const float point_eps = 1.0e-4f;", body)
        self.assertIn("fabsf(px - ax) <= point_eps", body)
        self.assertIn("fabsf(cross) <= point_eps * sqrtf(len2)", body)
        self.assertIn("dot >= -point_eps && dot <= len2 + point_eps", body)

    def test_device_predicate_uses_one_edge_loop_for_boundary_and_crossing(self) -> None:
        body = self._point_in_polygon_body()

        self.assertEqual(body.count("for (uint32_t i = 0, j = n - 1; i < n; j = i++)"), 1)
        self.assertIn("bool inside = false;", body)
        self.assertIn("inside = !inside;", body)
        self.assertLess(body.index("fabsf(cross)"), body.index("inside = !inside;"))


if __name__ == "__main__":
    unittest.main()
