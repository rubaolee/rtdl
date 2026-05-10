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
ENTRY_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "quick_tutorial.md",
    ROOT / "docs" / "tutorials" / "README.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Goal1608PublicSurfaceConsistencyTest(unittest.TestCase):
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

    def test_entry_docs_do_not_present_history_as_user_path(self):
        joined = "\n".join(_text(path) for path in ENTRY_DOCS)
        for forbidden in [
            "v1.0 remains the foundation proof line",
            "v1.5 remains the standalone",
            "v1.7-v2.0 are",
            "Goal748",
            "Goal1177",
            "Recommended v1.0 Demo Path",
            "Status: v1.0 direction contract",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, joined)

    def test_boundary_phrases_remain_visible(self):
        joined = "\n".join(_text(path) for path in PUBLIC_SURFACE_DOCS)
        normalized = " ".join(joined.split())
        for phrase in [
            "`--backend optix` is not",
            "whole-app",
            "source tree",
            "Performance Model",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_history_index_is_the_only_entry_history_route(self):
        for path in ENTRY_DOCS:
            with self.subTest(path=path):
                text = _text(path)
                if "History" in text:
                    self.assertIn("history/README.md", text)


if __name__ == "__main__":
    unittest.main()
