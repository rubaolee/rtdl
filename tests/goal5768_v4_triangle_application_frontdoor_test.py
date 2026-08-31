"""Application-level admission tests for the Triangle Counting V4 front door."""

from __future__ import annotations

import ast
import runpy
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py"


class TriangleApplicationFrontdoorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = runpy.run_path(str(APP_PATH))

    def test_both_paper_algorithms_lower_real_graph_edges(self) -> None:
        build = self.module["build_v4_input"]
        one = build("RT-1A2")
        two = build("RT-2A1")
        self.assertEqual(one.expected_triangle_count, 2)
        self.assertEqual(two.expected_triangle_count, 2)
        self.assertGreater(len(one.triangles), 0)
        self.assertGreater(len(one.queries), 0)
        self.assertGreater(len(two.triangles), 0)
        self.assertGreater(len(two.queries), 0)
        self.assertNotEqual(one.input_sha256, two.input_sha256)
        self.assertEqual(two.metadata["query.weight"], (1, 1))

    def test_rejects_nonpaper_algorithm(self) -> None:
        with self.assertRaisesRegex(ValueError, "RT-1A2 or RT-2A1"):
            self.module["build_v4_input"]("AUTO")

    def test_frontdoor_does_not_expand_expected_count_into_events(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertIn("_build_rt_graph_1a2_geometry", calls)
        self.assertIn("_build_rt_graph_2a1_geometry", calls)
        self.assertNotIn("repeat", calls)
        self.assertNotIn("tile", calls)

    def test_complete_timer_wraps_input_lowering_compile_and_execution(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertLess(source.index("started = time.perf_counter()"),
                        source.index("prepared_input = build_v4_input"))
        self.assertLess(source.index("prepared_input = build_v4_input"),
                        source.index("callback = compile_count_callback()"))
        self.assertLess(source.index("callback = compile_count_callback()"),
                        source.index("executed = run_builtin_triangle_reduction_callback"))
        self.assertLess(source.index("executed = run_builtin_triangle_reduction_callback"),
                        source.index("complete_seconds = time.perf_counter() - started"))

    def test_application_chooses_algorithm_not_default(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertIn('"default_selected_between_paper_algorithms": False', source)
        self.assertNotIn("select_default", source)
        self.assertNotIn("candidate_override", source)


if __name__ == "__main__":
    unittest.main()
