from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5773_home_multiround_lifecycle_validation.py"


class Goal5776RtDbscanFixedRadiusLifecycleTest(unittest.TestCase):
    def test_cross_call_reuse_varies_threshold_not_prepared_radius(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn("((0.35, 5), (0.35, 4))", source)
        self.assertNotIn("((0.35, 5), (0.28, 4))", source)
        self.assertIn("changing epsilon requires a", source)
        self.assertIn("separately prepared owner", source)


if __name__ == "__main__":
    unittest.main()
