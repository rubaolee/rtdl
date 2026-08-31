from __future__ import annotations

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py"


class BarnesHutV4FrontdoorTest(unittest.TestCase):
    def test_author_contract_builds_real_hierarchy_and_rows(self):
        module = runpy.run_path(str(APP))
        data = module["build_v4_input"](body_count=32)
        hierarchy = data["spec"].prepared_hierarchy.hierarchy
        self.assertEqual(hierarchy.point_count, 32)
        self.assertEqual(len(data["expected_rows"]), 32)
        self.assertGreater(hierarchy.node_count, 0)

    def test_timer_contains_tree_build_and_optix_execution(self):
        source = APP.read_text()
        self.assertIn("registered_complete_seconds", source)
        self.assertIn("author_bucket_tree_build", source)
        self.assertIn("optix_frontier_execute", source)
        self.assertNotIn("select_default", source)


if __name__ == "__main__":
    unittest.main()
