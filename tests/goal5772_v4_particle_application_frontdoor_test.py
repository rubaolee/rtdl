from __future__ import annotations

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / (
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/"
    "v4_whole_app.py"
)
STANDARD_LIBRARY = ROOT / "src/rtdsl/v4_builtin_triangle_standard_library.py"


class ParticleV4FrontdoorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = runpy.run_path(str(APP))

    def test_two_tetra_input_projects_unique_faces_and_exact_cells(self):
        data = self.module["build_v4_input"]()
        self.assertEqual(len(data["vertices"]), 5)
        self.assertEqual(len(data["triangles"]), 7)
        self.assertEqual(tuple(row[0] for row in data["expected"]), (0, 1))
        self.assertEqual(data["expected"][0][1], 1)
        self.assertEqual(data["expected"][1][1], 0xFFFFFFFF)

    def test_complete_timer_covers_input_compile_and_optix_execution(self):
        source = APP.read_text(encoding="utf-8")
        body = source[source.index("def run_v4_complete("):]
        self.assertLess(body.index("started = time.perf_counter()"),
                        body.index("data = build_v4_input()"))
        self.assertLess(body.index("data = build_v4_input()"),
                        body.index("compile_standard_builtin_triangle_program"))
        self.assertLess(body.index("compile_standard_builtin_triangle_program"),
                        body.index("run_builtin_triangle_callback"))
        self.assertLess(body.index("run_builtin_triangle_callback"),
                        body.index("elapsed = time.perf_counter() - started"))

    def test_product_frontdoor_does_not_import_tests_or_goal_fixture_scripts(self):
        product = STANDARD_LIBRARY.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        self.assertNotIn("from tests", product)
        self.assertNotIn("from scripts", product)
        self.assertNotIn("from tests", app)
        self.assertNotIn("from scripts", app)

    def test_no_default_or_expected_event_expansion(self):
        source = APP.read_text(encoding="utf-8")
        self.assertNotIn("select_default", source)
        self.assertNotIn("candidate_override", source)
        self.assertNotIn("repeat(", source)
        self.assertNotIn("tile(", source)


if __name__ == "__main__":
    unittest.main()
