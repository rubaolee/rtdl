from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal3258ClosedShapeSquaredBoundaryPredicateTest(unittest.TestCase):
    def test_boundary_check_avoids_per_edge_sqrt(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index("static __forceinline__ __device__ bool point_in_polygon(")
        end = text.index("extern \"C\" __global__ void __raygen__pip_probe()", start)
        body = text[start:end]

        self.assertIn("cross * cross <= point_eps * point_eps * len2", body)
        self.assertNotIn("sqrtf(len2)", body)
        self.assertIn("dot >= -point_eps && dot <= len2 + point_eps", body)


if __name__ == "__main__":
    unittest.main()
