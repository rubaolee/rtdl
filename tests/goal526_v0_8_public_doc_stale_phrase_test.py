from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal526V08PublicDocStalePhraseTest(unittest.TestCase):
    def test_public_v08_docs_do_not_imply_only_three_current_apps(self) -> None:
        release_examples = (
            REPO_ROOT / "docs" / "release_facing_examples.md"
        ).read_text(encoding="utf-8")
        feature_guide = (REPO_ROOT / "docs" / "rtdl_feature_guide.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("the other two v0.8 apps", release_examples)
        self.assertIn("Goal509 covers the robot collision screening and Barnes-Hut apps", release_examples)

        for app_name in (
            "Hausdorff distance",
            "ANN\n  candidate search",
            "outlier detection",
            "DBSCAN clustering",
            "robot collision",
            "Barnes-Hut force approximation",
        ):
            with self.subTest(app_name=app_name):
                self.assertIn(app_name, feature_guide)

        self.assertIn("Goal507, Goal509, and Goal524 reports", feature_guide)


if __name__ == "__main__":
    unittest.main()
