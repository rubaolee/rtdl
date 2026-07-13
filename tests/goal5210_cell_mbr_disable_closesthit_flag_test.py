from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal5210CellMbrDisableClosestHitFlagTest(unittest.TestCase):
    def test_cell_mbr_frontier_raygen_disables_closest_hit(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        start = source.index('extern "C" __global__ void __raygen__cell_mbr_frontier3d')
        end = source.index('extern "C" __global__ void __miss__cell_mbr_frontier3d')
        raygen = source[start:end]
        self.assertIn("OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT", raygen)
        self.assertNotIn("OPTIX_RAY_FLAG_NONE", raygen)
        self.assertIn("__anyhit__cell_mbr_frontier3d_emit", source)
        self.assertIn("__intersection__cell_mbr_frontier3d_exact", source)

    def test_disable_closesthit_change_is_scoped_to_cell_mbr_frontier(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        self.assertEqual(source.count("OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT"), 1)
        flag_index = source.index("OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT")
        raygen_start = source.rfind('extern "C" __global__ void ', 0, flag_index)
        raygen_header = source[raygen_start : source.index("{", raygen_start)]
        self.assertIn("__raygen__cell_mbr_frontier3d", raygen_header)


if __name__ == "__main__":
    unittest.main()
