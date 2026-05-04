from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1245ExamplesTutorialEntryTest(unittest.TestCase):
    def test_examples_index_has_short_path_before_full_inventory(self) -> None:
        text = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "## Short Path",
            "prove the checkout imports and runs",
            "choose one app by job instead of scanning the directory",
            "check what RTDL accelerates and what remains outside",
            "public speedup wording comes only from the support matrix and reviewed evidence",
            "## Directory Contents",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertLess(text.index("## Short Path"), text.index("## Start Here"))

    def test_tutorial_ladder_points_to_quickstart_and_full_examples_index(self) -> None:
        text = (ROOT / "docs" / "tutorials" / "README.md").read_text(encoding="utf-8")

        self.assertIn("[App And Example Quickstart](../app_example_quickstart.md)", text)
        self.assertIn("[Examples Index](../../examples/README.md)", text)
        self.assertIn("more complete and more boundary-heavy than this tutorial page", text)


if __name__ == "__main__":
    unittest.main()
