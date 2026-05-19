from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"


class Goal2397RtDbscanCupyGridUnionRepairTest(unittest.TestCase):
    def test_device_grid_components_use_monotonic_union(self) -> None:
        text = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("int find_root_readonly(const int* parent, int item)", text)
        self.assertIn("const int old = atomicMin(parent + high, low);", text)
        self.assertIn("if (other <= point || core_flags[other] == 0u) continue;", text)
        self.assertIn('"component_union_policy": "monotonic_atomic_min_core_edge_union"', text)
        self.assertNotIn("const int old = atomicCAS(parent + high, high, low);", text)


if __name__ == "__main__":
    unittest.main()
