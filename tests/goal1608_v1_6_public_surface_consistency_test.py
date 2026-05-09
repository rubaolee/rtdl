from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_SURFACE_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "quick_tutorial.md",
    ROOT / "docs" / "tutorials" / "README.md",
    ROOT / "docs" / "app_example_quickstart.md",
    ROOT / "docs" / "release_facing_examples.md",
    ROOT / "docs" / "rtdl_feature_guide.md",
    ROOT / "docs" / "performance_model.md",
    ROOT / "docs" / "application_catalog.md",
    ROOT / "docs" / "app_engine_support_matrix.md",
    ROOT / "docs" / "backend_maturity.md",
    ROOT / "docs" / "capability_boundaries.md",
    ROOT / "examples" / "README.md",
)
REVIEW_FILES = (
    ROOT / "docs" / "reviews" / "goal1608_v1_6_public_surface_polish_claude_review_2026-05-09.md",
    ROOT / "docs" / "reviews" / "goal1608_v1_6_public_surface_polish_gemini_review_2026-05-09.md",
    ROOT / "docs" / "reviews" / "goal1608_v1_6_public_surface_polish_3ai_consensus_2026-05-09.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Goal1608V16PublicSurfaceConsistencyTest(unittest.TestCase):
    def test_front_page_tutorial_docs_and_examples_name_v1_6(self):
        for path in PUBLIC_SURFACE_DOCS:
            with self.subTest(path=path):
                self.assertIn("v1.6", _text(path))

    def test_start_here_docs_keep_source_tree_commands(self):
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "quick_tutorial.md",
            ROOT / "docs" / "app_example_quickstart.md",
            ROOT / "docs" / "release_facing_examples.md",
            ROOT / "examples" / "README.md",
        ]:
            with self.subTest(path=path):
                text = _text(path)
                self.assertIn("PYTHONPATH=src:.", text)
                self.assertNotIn("pip install -e .", text)

    def test_public_surface_does_not_present_v1_0_or_v1_5_as_current(self):
        joined = "\n".join(_text(path) for path in PUBLIC_SURFACE_DOCS)
        for forbidden in [
            "Recommended v1.0 Demo Path",
            "v1.5 is the current public release",
            "v1.5 is the current release line",
            "current released state is `v1.5`",
            "current released version is `v1.5`",
            "Status: public app-level support map for current `main` after Goal970",
            "Status: v1.0 direction contract",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, joined)

    def test_boundary_phrases_remain_visible(self):
        joined = "\n".join(_text(path) for path in PUBLIC_SURFACE_DOCS)
        for phrase in [
            "first Python+RTDL architecture milestone",
            "`--backend optix` is not",
            "whole-app speedup",
            "`COLLECT_K_BOUNDED` remains experimental",
            "source tree",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, joined)

    def test_external_review_consensus_exists(self):
        for path in REVIEW_FILES:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)
        consensus = _text(REVIEW_FILES[-1])
        for phrase in [
            "Codex Verdict",
            "Claude Verdict",
            "Gemini Verdict",
            "ACCEPT",
            "does not authorize a new release tag",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
