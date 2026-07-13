from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "run_goal5504_librts_range_intersects_semantics_fixtures.py"
SPEC = importlib.util.spec_from_file_location("goal5504_fixtures", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5504RangeIntersectsSemanticsFixtureTest(unittest.TestCase):
    def test_fixture_matrix_is_deterministic_and_source_consistent(self) -> None:
        cases = MODULE.build_cases()
        self.assertEqual(len(cases), 5)
        self.assertEqual(sum(bool(case["discriminates"]) for case in cases), 1)
        by_id = {case["case_id"]: case for case in cases}
        self.assertEqual(
            (by_id["interior_overlap"]["cpu_inclusive_intersects"], by_id["interior_overlap"]["author_gpu_style_intersects"]),
            (True, True),
        )
        self.assertEqual(
            (by_id["edge_touch"]["cpu_inclusive_intersects"], by_id["edge_touch"]["author_gpu_style_intersects"]),
            (True, True),
        )
        self.assertEqual(
            (by_id["corner_touch"]["cpu_inclusive_intersects"], by_id["corner_touch"]["author_gpu_style_intersects"]),
            (True, True),
        )
        self.assertEqual(
            (by_id["one_ulp_gap_after_box_max"]["cpu_inclusive_intersects"], by_id["one_ulp_gap_after_box_max"]["author_gpu_style_intersects"]),
            (False, True),
        )

    def test_fixture_is_not_an_author_runtime_claim(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("author_gpu_style_intersects", text)
        self.assertIn('"author_gpu_runtime_executed": False', text)
        self.assertIn('"cpu_oracle_is_author_truth": False', text)
        self.assertIn('"rtdl_core_change_authorized": False', text)


if __name__ == "__main__":
    unittest.main()
