"""Application-level admission tests for the RayDB V4 front door."""

from __future__ import annotations

import ast
from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "Paper-reproduction-apps/raydb-paper/v4_whole_app.py"


class RayDBApplicationFrontdoorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = runpy.run_path(str(APP_PATH))

    def test_bounded_q21_starts_from_rows_and_matches_reference(self) -> None:
        prepared = self.module["build_v4_input"]()
        self.assertEqual(len(prepared.triangles), 10)
        self.assertEqual(len(prepared.queries), 7)
        self.assertEqual(
            prepared.expected_keyed_rows,
            (((0,), 47), ((2,), 5), ((3,), 13)),
        )
        self.assertEqual(
            prepared.expected_paper_rows,
            (
                {"group": [1992, 12], "value": 47},
                {"group": [1993, 12], "value": 5},
                {"group": [1994, 12], "value": 13},
            ),
        )

    def test_frontdoor_uses_app_rows_not_expected_output_expansion(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        attributes = {
            node.func.attr for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("bounded_q21_rows", attributes)
        self.assertIn("events_from_rows", attributes)
        self.assertIn("run_reference_rows", attributes)
        self.assertNotIn("repeat", attributes)
        self.assertNotIn("tile", attributes)

    def test_complete_timer_wraps_lowering_compile_and_execute(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertLess(source.index("started = time.perf_counter()"),
                        source.index("prepared_input = build_v4_input()"))
        self.assertLess(source.index("prepared_input = build_v4_input()"),
                        source.index("callback = compile_keyed_callback()"))
        self.assertLess(source.index("callback = compile_keyed_callback()"),
                        source.index("executed = run_builtin_triangle_reduction_callback"))
        self.assertLess(source.index("executed = run_builtin_triangle_reduction_callback"),
                        source.index("complete_seconds = time.perf_counter() - started"))

    def test_no_app_identity_dispatch_in_product_standard_library(self) -> None:
        product = (ROOT / "src/rtdsl/v4_triangle_standard_library.py").read_text()
        for forbidden in ("raydb", "q21", "triangle_counting", "paper_app"):
            self.assertNotIn(forbidden, product.lower())


if __name__ == "__main__":
    unittest.main()
