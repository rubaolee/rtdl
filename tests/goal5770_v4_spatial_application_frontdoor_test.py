from __future__ import annotations

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SpatialV4FrontdoorTest(unittest.TestCase):
    def test_rtnn_uses_real_xyz_and_exact_app_oracle(self):
        path = ROOT / "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py"
        module = runpy.run_path(str(path))
        data = module["build_v4_input"]()
        self.assertGreater(len(data["search"]), 0)
        self.assertGreater(len(data["queries"]), 0)
        self.assertGreater(len(data["expected"]), 0)
        self.assertLessEqual(len(data["expected"]), len(data["queries"]) * 4)
        self.assertIn("registered_complete_seconds", path.read_text())

    def test_rt_dbscan_uses_real_csv_and_exact_app_oracle(self):
        path = ROOT / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py"
        module = runpy.run_path(str(path))
        data = module["build_v4_input"]()
        self.assertGreater(len(data["points"]), 0)
        self.assertEqual(
            len(data["expected"]["canonical_component_labels"]),
            len(data["points"]),
        )
        self.assertIn("registered_complete_seconds", path.read_text())

    def test_target_compute_capability_is_not_home_hardcoded(self):
        for app in ("rtnn-paper", "rt-dbscan-paper"):
            source = (ROOT / f"Paper-reproduction-apps/{app}/v4_whole_app.py").read_text()
            self.assertIn("compute_capability=compute_capability", source)
            self.assertNotIn("compute_capability=(6, 1)", source)


if __name__ == "__main__":
    unittest.main()
