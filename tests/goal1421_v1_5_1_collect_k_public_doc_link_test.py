from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


class Goal1421V151CollectKPublicDocLinkTest(unittest.TestCase):
    def test_front_page_links_candidate_docs_with_boundary(self) -> None:
        readme = _read("README.md")

        self.assertIn("docs/release_reports/v1_5_1/README.md", readme)
        self.assertIn("documented experimental public-candidate", readme)
        self.assertIn("not stable primitive promotion", readme)
        self.assertIn("no public speedup wording", readme)
        self.assertIn("no zero-copy wording", readme)
        self.assertIn("no whole-app claims", readme)
        self.assertIn("no release tag action", readme)

    def test_docs_index_links_candidate_docs_with_boundary(self) -> None:
        docs_index = _compact(_read("docs/README.md"))

        self.assertIn("release_reports/v1_5_1/README.md", docs_index)
        self.assertIn("documented experimental public-candidate", docs_index)
        self.assertIn("not stable primitive promotion", docs_index)
        self.assertIn("no public speedup wording", docs_index)
        self.assertIn("no zero-copy wording", docs_index)
        self.assertIn("no whole-app claims", docs_index)
        self.assertIn("no release tag action", docs_index)

    def test_public_map_links_candidate_docs_without_overclaiming(self) -> None:
        public_map = _compact(_read("docs/public_documentation_map.md"))

        self.assertIn("release_reports/v1_5_1/README.md", public_map)
        self.assertIn("documented experimental public-candidate", public_map)
        self.assertIn("not stable primitive promotion", public_map)
        self.assertIn("no public speedup wording", public_map)
        self.assertIn("no zero-copy wording", public_map)
        self.assertIn("no whole-app claims", public_map)
        self.assertIn("no release tag action", public_map)

    def test_public_docs_do_not_authorize_forbidden_claims(self) -> None:
        combined = "\n".join(
            _read(path)
            for path in (
                "README.md",
                "docs/README.md",
                "docs/public_documentation_map.md",
            )
        )

        for forbidden in (
            "COLLECT_K_BOUNDED is stable",
            "public speedup is authorized",
            "zero-copy is authorized",
            "release tag action is authorized",
            "whole-app speedup is authorized",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
