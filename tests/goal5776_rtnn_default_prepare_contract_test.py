from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py"


class Goal5776RtnnDefaultPrepareContractTest(unittest.TestCase):
    def test_optional_real_scale_keys_have_paper_fixture_defaults(self):
        source = SOURCE.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn('data.get("k", 4)', source)
        self.assertIn('data.get("maximum_distance", 3.0)', source)
        self.assertNotIn('int(data["k"]) if data is not None', source)
        self.assertNotIn('float(data["maximum_distance"]) if data is not None', source)


if __name__ == "__main__":
    unittest.main()
