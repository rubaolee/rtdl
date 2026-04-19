from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
V08_DIR = REPO_ROOT / "docs" / "release_reports" / "v0_8"


class Goal532V08ReleaseAuthorizationTest(unittest.TestCase):
    def test_public_docs_identify_v094_as_current_release_and_v08_as_released_layer(self) -> None:
        front_page = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        self.assertIn("current released version: `v0.9.4`", front_page)
        self.assertIn("current released version is `v0.9.4`", docs_index)
        self.assertIn("released `v0.8.0` app-building", front_page)
        self.assertIn("released `v0.8.0` app-building", docs_index)
        self.assertIn("RTDL v0.8 Release Package", front_page)
        self.assertIn("v0.8 Release Package", docs_index)

    def test_v08_release_package_no_longer_claims_candidate_status(self) -> None:
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                V08_DIR / "README.md",
                V08_DIR / "release_statement.md",
                V08_DIR / "support_matrix.md",
                V08_DIR / "audit_report.md",
                V08_DIR / "tag_preparation.md",
            )
        )

        self.assertIn("Status: released as `v0.8.0`", public_text)
        self.assertIn("Tag `v0.8.0` is authorized for the Goal532 release commit", public_text)
        for stale_phrase in (
            "release candidate / not yet tagged",
            "current released version remains `v0.7.0`",
            "not authorized for tag yet",
            "Do not tag `v0.8.0` yet",
            "Release-Candidate",
        ):
            with self.subTest(stale_phrase=stale_phrase):
                self.assertNotIn(stale_phrase, public_text)

    def test_release_boundary_stays_bounded(self) -> None:
        statement = (V08_DIR / "release_statement.md").read_text(encoding="utf-8")
        support = (V08_DIR / "support_matrix.md").read_text(encoding="utf-8")

        self.assertIn("not widen the v0.7 DB/language/backend contract", statement)
        self.assertIn("not a full ANN index", support)
        self.assertIn("not a DB release", support)
        self.assertIn("Vulkan is intentionally not exposed", support)


if __name__ == "__main__":
    unittest.main()
