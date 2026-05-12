from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1802PartnerAnyHitDocsExampleTest(unittest.TestCase):
    def test_tutorial_and_indexes_link_partner_anyhit_example(self) -> None:
        tutorial = (ROOT / "docs" / "tutorials" / "partner_anyhit.md").read_text(encoding="utf-8")
        tutorials_index = (ROOT / "docs" / "tutorials" / "README.md").read_text(encoding="utf-8")
        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        examples_index = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")
        app_quickstart = (ROOT / "docs" / "app_example_quickstart.md").read_text(encoding="utf-8")

        self.assertIn("rt.run_partner_ray_triangle_any_hit_2d", tutorial)
        self.assertIn("transfer_mode = \"host_stage\"", tutorial)
        self.assertIn("true_zero_copy_authorized", tutorial)
        self.assertIn("Python Partner Any-Hit", tutorials_index)
        self.assertIn("tutorials/partner_anyhit.md", docs_index)
        self.assertIn("rtdl_partner_anyhit.py", examples_index)
        self.assertIn("rtdl_partner_anyhit.py --partner numpy --backend embree", app_quickstart)

    def test_partner_anyhit_example_runs_on_embree_when_available(self) -> None:
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("NumPy is required for the partner any-hit example")

        import sys

        sys.path.insert(0, str(ROOT / "examples"))
        import rtdl_partner_anyhit as example

        try:
            result = example.run_demo(partner="numpy", backend="embree")
        except (OSError, RuntimeError, ValueError) as exc:
            self.skipTest(f"Embree backend is not available in this environment: {exc}")

        self.assertEqual(result["example"], "rtdl_partner_anyhit")
        self.assertEqual(result["backend"], "embree")
        self.assertEqual(result["partner_input"], "numpy")
        self.assertEqual(result["hit_count"], 1)
        self.assertEqual(result["transfer_mode"], "host_stage")
        self.assertFalse(result["true_zero_copy_authorized"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
