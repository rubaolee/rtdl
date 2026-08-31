from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class Goal3099V27SemanticSearchPreviewTest(unittest.TestCase):
    def test_semantic_search_requires_explicit_preview_flag(self) -> None:
        with self.assertRaisesRegex(ValueError, "preview-only"):
            rt.find_primitive_semantic("page huge witness rows")

    def test_semantic_search_preview_finds_synonym_intents(self) -> None:
        cases = (
            ("page huge witness rows", "continuation.segmented_chunked_rows"),
            ("density core flags", "traversal.fixed_radius_count_threshold"),
            ("prepared scene reuse", "execution.prepared_rt_state"),
        )

        for query, expected_id in cases:
            with self.subTest(query=query):
                matches = rt.find_primitive_semantic(query, enable_preview=True, limit=5)
                self.assertTrue(matches, query)
                self.assertEqual(matches[0].node_id, expected_id)
                self.assertGreater(matches[0].score, 0)

    def test_semantic_search_preview_is_metadata_only(self) -> None:
        validation = rt.validate_primitive_semantic_search()

        self.assertTrue(validation["valid"], validation)
        self.assertFalse(validation["executes"])
        self.assertFalse(validation["uses_embeddings"])
        self.assertFalse(validation["automatic_partner_selection_allowed"])
        self.assertTrue(validation["preview_requires_explicit_enable"])
        self.assertIn("does not execute", validation["claim_boundary"])
        self.assertIn("does not execute", rt.PRIMITIVE_SEMANTIC_SEARCH_CLAIM_BOUNDARY)

    def test_public_exports_include_semantic_preview_surface(self) -> None:
        expected = (
            "find_primitive_semantic",
            "validate_primitive_semantic_search",
            "PRIMITIVE_SEMANTIC_SEARCH_PREVIEW_VERSION",
            "PRIMITIVE_SEMANTIC_SEARCH_EXECUTES",
            "PRIMITIVE_SEMANTIC_SEARCH_USES_EMBEDDINGS",
            "PRIMITIVE_SEMANTIC_SEARCH_AUTO_PARTNER_SELECTION_ALLOWED",
            "PRIMITIVE_SEMANTIC_SEARCH_CLAIM_BOUNDARY",
        )

        for name in expected:
            with self.subTest(name=name):
                self.assertIn(name, rt.__all__)
                self.assertTrue(hasattr(rt, name))

    def test_catalog_records_semantic_preview_boundaries(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn("Semantic search preview validation valid: `True`", catalog)
        self.assertIn("Semantic search preview executes: `False`", catalog)
        self.assertIn("Semantic search preview uses embeddings: `False`", catalog)
        self.assertIn("Semantic search preview auto partner selection: `False`", catalog)


if __name__ == "__main__":
    unittest.main()
