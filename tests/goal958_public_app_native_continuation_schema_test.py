from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal958PublicAppNativeContinuationSchemaTest(unittest.TestCase):
    def test_rt_core_app_payloads_expose_native_continuation_schema(self) -> None:
        missing: list[str] = []
        for path in sorted((ROOT / "examples").glob("rtdl_*.py")):
            text = path.read_text()
            if "rt_core_accelerated" not in text:
                continue
            if "native_continuation_active" not in text or "native_continuation_backend" not in text:
                missing.append(str(path.relative_to(ROOT)))

        self.assertEqual(missing, [])

    def test_public_docs_explain_native_continuation_boundary(self) -> None:
        docs = {
            "examples/README.md": (ROOT / "examples" / "README.md").read_text(),
            "docs/application_catalog.md": (ROOT / "docs" / "application_catalog.md").read_text(),
            "docs/app_engine_support_matrix.md": (ROOT / "docs" / "app_engine_support_matrix.md").read_text(),
        }

        for label, text in docs.items():
            with self.subTest(label=label):
                self.assertIn("native", text.lower())
                self.assertIn("continuation", text.lower())

    def test_no_public_doc_uses_known_overclaim_phrases(self) -> None:
        public_docs = (
            ROOT / "examples" / "README.md",
            ROOT / "docs" / "application_catalog.md",
            ROOT / "docs" / "app_engine_support_matrix.md",
            ROOT / "docs" / "features" / "segment_polygon_anyhit_rows" / "README.md",
            ROOT / "docs" / "features" / "segment_polygon_hitcount" / "README.md",
        )
        forbidden = (
            "unbounded pair-row acceleration is ready",
            "broad segment/polygon app speedup is authorized",
            "full gis/routing acceleration is supported",
        )
        for path in public_docs:
            text = path.read_text().lower()
            for phrase in forbidden:
                with self.subTest(path=path.relative_to(ROOT), phrase=phrase):
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
