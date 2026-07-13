from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "run_goal5501_range_intersects_mismatch_diagnostic.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("goal5501_diagnostic", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5501RangeIntersectsMismatchDiagnosticTest(unittest.TestCase):
    def test_cpu_oracle_distinguishes_overlap_from_padding(self) -> None:
        import numpy as np

        boxes = MODULE.rt.Aabb2DColumns(
            ids=np.array([0, 1], dtype=np.uint32),
            min_x=np.array([0.0, 2.0]),
            min_y=np.array([0.0, 2.0]),
            max_x=np.array([1.0, 3.0]),
            max_y=np.array([1.0, 3.0]),
        )
        queries = MODULE.rt.Aabb2DColumns(
            ids=np.array([0, 1], dtype=np.uint32),
            min_x=np.array([1.0, 3.0000005]),
            min_y=np.array([0.0, 2.0]),
            max_x=np.array([1.0, 4.0]),
            max_y=np.array([1.0, 3.0]),
        )
        self.assertEqual(MODULE.cpu_overlap_count(boxes, queries, cast_float32=False), 1)
        self.assertEqual(MODULE.cpu_overlap_count(boxes, queries, cast_float32=True), 1)
        self.assertEqual(
            MODULE.cpu_overlap_count(boxes, queries, cast_float32=True, pad=1.0e-6),
            2,
        )

    def test_diagnostic_contract_is_not_a_claim_upgrade(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("float64_exact_overlap_count", text)
        self.assertIn("float32_overlap_count", text)
        self.assertIn("root_cause_declared", text)
        self.assertIn("complete_range_intersects_matrix_claimed", text)
        self.assertIn("parks_bz2_oom_resolved", text)


if __name__ == "__main__":
    unittest.main()
