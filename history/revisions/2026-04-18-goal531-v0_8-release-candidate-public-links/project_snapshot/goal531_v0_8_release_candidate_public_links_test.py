from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal531V08ReleaseCandidatePublicLinksTest(unittest.TestCase):
    def test_front_page_links_v08_release_candidate_package(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("RTDL v0.8 Release-Candidate Statement", text)
        self.assertIn("RTDL v0.8 Release-Candidate Support Matrix", text)
        self.assertIn("RTDL v0.8 Release-Candidate Package", text)
        self.assertIn("docs/release_reports/v0_8/README.md", text)

    def test_docs_index_includes_v08_before_v07_release_links(self) -> None:
        text = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        v08 = text.index("[v0.8 Release-Candidate Package](release_reports/v0_8/README.md)")
        v07 = text.index("[v0.7 Release Package](release_reports/v0_7/README.md)")
        self.assertLess(v08, v07)
        self.assertIn(
            "[v0.8 Release-Candidate Support Matrix](release_reports/v0_8/support_matrix.md)",
            text,
        )

    def test_architecture_links_current_app_release_candidate_boundary(self) -> None:
        text = (REPO_ROOT / "docs" / "current_architecture.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("v0.8 Release-Candidate Statement", text)
        self.assertIn("v0.8 Release-Candidate Support Matrix", text)


if __name__ == "__main__":
    unittest.main()
