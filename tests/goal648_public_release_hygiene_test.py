from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal648PublicReleaseHygieneTest(unittest.TestCase):
    def test_history_public_indexes_include_current_v096_and_v095_release_rows(self) -> None:
        history_readme = (REPO_ROOT / "history" / "README.md").read_text(encoding="utf-8")
        complete_history = (REPO_ROOT / "history" / "COMPLETE_HISTORY.md").read_text(encoding="utf-8")
        revision_dashboard = (
            REPO_ROOT / "history" / "revision_dashboard.md"
        ).read_text(encoding="utf-8")

        self.assertIn("through the `v0.9.6` release", history_readme)
        self.assertIn("Goal1023", history_readme)
        self.assertIn("fresh-checkout verification", history_readme)
        self.assertIn("- `v0.9.6`", complete_history)
        self.assertIn("Goal1023 v0.9.6 history catch-up", complete_history)
        self.assertIn("- `v0.9.5`", complete_history)
        self.assertIn("Goal647 fresh checkout post-release verification", complete_history)
        self.assertIn("Goal646 public front-page doc refresh", complete_history)
        self.assertIn("Goal645 v0.9.5 release action and package", complete_history)
        self.assertIn("| v0.9.6 | 2026-04-26 | accepted |", revision_dashboard)
        self.assertIn("Goal648 public release hygiene check", revision_dashboard)
        self.assertIn("| v0.9.5 | 2026-04-20 | accepted |", revision_dashboard)

    def test_internal_v092_package_is_not_mistaken_for_public_release(self) -> None:
        v092_files = [
            REPO_ROOT / "docs" / "release_reports" / "v0_9_2" / "README.md",
            REPO_ROOT / "docs" / "release_reports" / "v0_9_2" / "release_statement.md",
            REPO_ROOT / "docs" / "release_reports" / "v0_9_2" / "tag_preparation.md",
        ]
        for path in v092_files:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("not tagged as a public release", text)
                self.assertIn("absorbed", text)
                self.assertIn("released `v0.9.4`", text)

    def test_historical_v09_matrix_points_to_current_release_boundary(self) -> None:
        matrix = (
            REPO_ROOT / "docs" / "release_reports" / "v0_9" / "support_matrix.md"
        ).read_text(encoding="utf-8")

        self.assertIn("historical `v0.9.0`/`v0.9.1` support", matrix)
        self.assertIn("For the current public release boundary", matrix)
        self.assertIn("../v0_9_6/support_matrix.md", matrix)


if __name__ == "__main__":
    unittest.main()
