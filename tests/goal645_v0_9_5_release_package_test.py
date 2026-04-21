from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
V095_DIR = REPO_ROOT / "docs" / "release_reports" / "v0_9_5"


class Goal645V095ReleasePackageTest(unittest.TestCase):
    def test_v095_release_package_files_exist(self) -> None:
        for filename in (
            "README.md",
            "release_statement.md",
            "support_matrix.md",
            "audit_report.md",
            "tag_preparation.md",
        ):
            with self.subTest(filename=filename):
                self.assertTrue((V095_DIR / filename).is_file())

    def test_public_docs_keep_v095_as_previous_release_after_v096(self) -> None:
        front_page = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        self.assertIn("current released version: `v0.9.6`", front_page)
        self.assertIn("current released version is `v0.9.6`", docs_index)
        self.assertIn("`v0.9.5`: previous public release", front_page)
        self.assertIn("RTDL v0.9.5 Release Package", front_page)
        self.assertIn("v0.9.5 Release Package", docs_index)

    def test_v095_release_surface_and_boundaries_are_documented(self) -> None:
        public_text = "\n".join(
            (V095_DIR / filename).read_text(encoding="utf-8")
            for filename in (
                "README.md",
                "release_statement.md",
                "support_matrix.md",
                "audit_report.md",
                "tag_preparation.md",
            )
        )

        for phrase in (
            "ray_triangle_any_hit",
            "visibility_rows",
            "reduce_rows",
            "OptiX, Embree, and HIPRT have native early-exit any-hit",
            "Vulkan and Apple RT support the any-hit row contract",
            "`reduce_rows` is not a backend primitive",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, public_text)

    def test_no_stale_v095_candidate_wording_in_public_docs(self) -> None:
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                REPO_ROOT / "README.md",
                REPO_ROOT / "docs" / "README.md",
                REPO_ROOT / "docs" / "rtdl_feature_guide.md",
                REPO_ROOT / "docs" / "release_facing_examples.md",
                REPO_ROOT / "docs" / "features" / "README.md",
            )
        )

        for stale_phrase in (
            "active v0.9.5 candidate",
            "`v0.9.5` candidate",
            "v0.9.5 candidate surface",
        ):
            with self.subTest(stale_phrase=stale_phrase):
                self.assertNotIn(stale_phrase, public_text)


if __name__ == "__main__":
    unittest.main()
