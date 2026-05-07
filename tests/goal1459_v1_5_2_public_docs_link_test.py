from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOCS = (ROOT / "README.md", ROOT / "docs" / "README.md")
LINK_LABEL = "v1.5.2 Prepared Host-Output Candidate Docs"
STATUS_WORDING = (
    "v1.5.2 candidate docs record reviewed prepared host-output evidence for "
    "COLLECT_K_BOUNDED; still no prepared-buffer reuse claim, no public speedup "
    "wording, no zero-copy wording, no whole-app claims, no stable primitive "
    "promotion, and no release tag action"
)


def normalized(text: str) -> str:
    return " ".join(text.split())


class Goal1459V152PublicDocsLinkTest(unittest.TestCase):
    def test_public_docs_link_to_reviewed_candidate_package(self) -> None:
        for path in PUBLIC_DOCS:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(LINK_LABEL, text)
                self.assertIn("release_reports/v1_5_2/README.md", text)

    def test_public_docs_keep_exact_bounded_status_wording(self) -> None:
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")

        self.assertIn(STATUS_WORDING, normalized(root_readme))
        self.assertIn(STATUS_WORDING, normalized(docs_readme))

    def test_public_docs_do_not_claim_v1_5_2_release_or_speedup(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_DOCS)

        forbidden_phrases = (
            "v1.5.2 is released",
            "v1.5.2 released",
            "prepared-buffer reuse proven",
            "true zero-copy is authorized",
            "public speedup authorized",
            "stable primitive promotion is authorized",
            "release tag action authorized",
        )
        for phrase in forbidden_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
