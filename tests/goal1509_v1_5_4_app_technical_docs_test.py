from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "technical_app_notes"
INDEX = DOC_DIR / "README.md"
MATRIX = DOC_DIR / "app_implementation_matrix.md"
DOC_INDEX = ROOT / "docs" / "README.md"


class Goal1509AppTechnicalDocsTest(unittest.TestCase):
    def test_docs_exist(self):
        self.assertTrue(INDEX.exists())
        self.assertTrue(MATRIX.exists())

    def test_index_declares_non_claim_scope(self):
        text = INDEX.read_text(encoding="utf-8")
        for phrase in [
            "not tutorials",
            "does not authorize public",
            "true zero-copy",
            "reduced-copy",
            "COLLECT_K_BOUNDED",
        ]:
            self.assertIn(phrase, text)

    def test_public_docs_index_links_technical_notes(self):
        text = DOC_INDEX.read_text(encoding="utf-8")
        self.assertIn("Technical App Notes", text)
        self.assertIn("technical_app_notes/README.md", text)

    def test_matrix_covers_public_app_set(self):
        text = MATRIX.read_text(encoding="utf-8")
        for app in [
            "Database Analytics",
            "Graph Analytics",
            "Service Coverage Gaps",
            "Event Hotspot Screening",
            "Facility KNN Assignment",
            "Road Hazard Screening",
            "Segment/Polygon Hitcount",
            "Segment/Polygon Any-Hit Rows",
            "Polygon-Pair Overlap Area Rows",
            "Polygon-Set Jaccard",
            "Hausdorff Distance",
            "ANN Candidate Search",
            "Outlier Detection",
            "DBSCAN Clustering",
            "Robot Collision Screening",
            "Barnes-Hut Force App",
        ]:
            self.assertIn(f"### {app}", text)

    def test_matrix_keeps_claim_boundaries_visible(self):
        text = MATRIX.read_text(encoding="utf-8")
        for phrase in [
            "This is not a public speedup claim",
            "not true zero-copy",
            "whole-app acceleration",
            "COLLECT_K_BOUNDED",
            "exact 512-copy",
            "outside RTDL",
        ]:
            self.assertIn(phrase, text)

    def test_matrix_explains_v1_0_current_and_copy_for_every_app(self):
        text = MATRIX.read_text(encoding="utf-8")
        sections = [part for part in text.split("\n### ") if part.startswith((
            "Database Analytics",
            "Graph Analytics",
            "Service Coverage Gaps",
            "Event Hotspot Screening",
            "Facility KNN Assignment",
            "Road Hazard Screening",
            "Segment/Polygon Hitcount",
            "Segment/Polygon Any-Hit Rows",
            "Polygon-Pair Overlap Area Rows",
            "Polygon-Set Jaccard",
            "Hausdorff Distance",
            "ANN Candidate Search",
            "Outlier Detection",
            "DBSCAN Clustering",
            "Robot Collision Screening",
            "Barnes-Hut Force App",
        ))]
        self.assertEqual(16, len(sections))
        for section in sections:
            self.assertIn("v1.0 implementation", section)
            self.assertIn("Current implementation direction", section)
            self.assertIn("Copy/reduction behavior", section)
            self.assertIn("Performance evidence", section)
            self.assertIn("Pros:", section)
            self.assertIn("Cons:", section)


if __name__ == "__main__":
    unittest.main()
