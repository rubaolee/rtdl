from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.primitive_catalog import PRIMITIVE_CATALOG_GENERATOR_VERSION
from rtdsl.primitive_catalog import render_primitive_catalog_markdown
from scripts.generate_rtdl_primitive_catalog import main as catalog_generator_main


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"


class Goal3073V27GeneratedPrimitiveCatalogTest(unittest.TestCase):
    def test_checked_in_catalog_matches_renderer(self) -> None:
        rendered = render_primitive_catalog_markdown()
        checked_in = CATALOG.read_text(encoding="utf-8")

        self.assertEqual(checked_in, rendered)

    def test_generator_check_mode_detects_no_drift(self) -> None:
        self.assertEqual(catalog_generator_main(["--check"]), 0)

    def test_catalog_records_generator_and_source_of_truth(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn(PRIMITIVE_CATALOG_GENERATOR_VERSION, catalog)
        self.assertIn("Generated from `src/rtdsl/primitive_hierarchy.py`", catalog)
        self.assertIn("Do not hand-edit this", catalog)
        self.assertIn("rtdsl.find_primitive", catalog)
        self.assertIn("rtdsl.lint_new_primitive", catalog)

    def test_every_hierarchy_node_id_appears_in_catalog(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        for node in rt.iter_primitive_hierarchy_nodes():
            with self.subTest(node=node.id):
                self.assertIn(node.id, catalog)

    def test_catalog_uses_current_partner_language(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn("Explicit Partner Continuation", catalog)
        self.assertIn("Partner-selected post-traversal continuation", catalog)
        self.assertNotIn("Triton-first Partner Continuation", catalog)
        self.assertNotIn("Triton-first post-traversal", catalog)

    def test_catalog_preserves_claim_boundary(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")

        self.assertIn("does not authorize release readiness", catalog)
        self.assertIn("public speedup wording", catalog)
        self.assertIn("zero-copy claims", catalog)
        self.assertIn("app-specific native engine logic", catalog)


if __name__ == "__main__":
    unittest.main()
