from __future__ import annotations

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py"


class XHDV4FrontdoorTest(unittest.TestCase):
    def test_real_wkt_input_and_exact_witness(self):
        module = runpy.run_path(str(APP))
        data = module["build_v4_input"]()
        self.assertEqual(data["sources"].shape, (2, 3))
        self.assertEqual(data["targets"].shape, (2, 3))
        self.assertEqual(data["expected"]["source_id"], 0)
        self.assertEqual(data["expected"]["item_id"], 0)
        self.assertIn("registered_complete_seconds", APP.read_text())

    def test_no_home_cc_or_plan_selection(self):
        source = APP.read_text()
        self.assertIn("compute_capability=compute_capability", source)
        self.assertNotIn("compute_capability=(6, 1)", source)
        self.assertNotIn("select_default", source)


if __name__ == "__main__":
    unittest.main()
