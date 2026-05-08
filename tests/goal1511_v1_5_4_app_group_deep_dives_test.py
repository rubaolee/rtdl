from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "technical_app_notes" / "app_group_deep_dives.md"
INDEX = ROOT / "docs" / "technical_app_notes" / "README.md"


class Goal1511AppGroupDeepDivesTest(unittest.TestCase):
    def test_deep_dive_doc_exists(self):
        self.assertTrue(DOC.exists())

    def test_group_headings_exist(self):
        text = DOC.read_text(encoding="utf-8")
        for heading in [
            "## Group 1: Reduction-First Apps",
            "## Group 2: Split-Contract Apps",
            "## Group 3: Candidate-Refinement Apps",
            "## Group 4: Bounded-Collection Blocked Apps",
            "## Cross-Group Design Rules",
        ]:
            self.assertIn(heading, text)

    def test_each_group_has_implementation_copy_and_testing_focus(self):
        text = DOC.read_text(encoding="utf-8")
        groups = text.split("## Group ")[1:5]
        self.assertEqual(4, len(groups))
        for group in groups:
            self.assertIn("### Implementation Shape", group)
            self.assertIn("### Copy Behavior", group)
            self.assertIn("### Testing Focus", group)

    def test_boundaries_and_claim_controls_are_explicit(self):
        text = DOC.read_text(encoding="utf-8")
        for phrase in [
            "does not authorize public speedup",
            "true zero-copy claims",
            "Unsafe wording without new evidence",
            "No silent truncation",
            "Pod evidence uses the expected native path",
            "Do not use whole-app speedup wording",
        ]:
            self.assertIn(phrase, text)

    def test_index_links_deep_dive(self):
        text = INDEX.read_text(encoding="utf-8")
        self.assertIn("app_group_deep_dives.md", text)


if __name__ == "__main__":
    unittest.main()
