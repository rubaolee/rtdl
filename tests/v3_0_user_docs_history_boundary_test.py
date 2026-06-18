from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


CURRENT_DOC_PATHS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "learn" / "README.md",
    ROOT / "docs" / "learn" / "benchmark_evidence_index.md",
    ROOT / "docs" / "learn" / "current_claim_boundaries.md",
    ROOT / "docs" / "release_reports" / "README.md",
    ROOT / "examples" / "README.md",
    ROOT / "examples" / "current" / "README.md",
    ROOT / "tutorials" / "README.md",
    ROOT / "tutorials" / "current" / "README.md",
)


class V30UserDocsHistoryBoundaryTest(unittest.TestCase):
    def test_release_reports_directory_is_current_only(self) -> None:
        names = {path.name for path in (ROOT / "docs" / "release_reports").iterdir()}
        self.assertEqual({"README.md", "v3_0"}, names)
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v2_14").is_dir())
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v1_0").is_dir())
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v0_9_8").is_dir())

    def test_learn_and_current_examples_are_v3_only(self) -> None:
        self.assertFalse((ROOT / "docs" / "learn" / "v2_14_app_author_implementation_strategy.md").exists())
        self.assertFalse((ROOT / "docs" / "learn" / "v3_0_c_abi_draft.md").exists())
        self.assertFalse((ROOT / "examples" / "current" / "embedding").exists())
        self.assertTrue((ROOT / "docs" / "history" / "learn" / "v2_14_app_author_implementation_strategy.md").exists())
        self.assertTrue((ROOT / "docs" / "history" / "v4_preparatory_embedding" / "v3_0_c_abi_draft.md").exists())
        self.assertTrue((ROOT / "docs" / "history" / "v4_preparatory_embedding" / "examples" / "embedding").is_dir())

    def test_current_entry_points_do_not_link_old_release_packets(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in CURRENT_DOC_PATHS)
        forbidden = (
            "release_reports/v0_",
            "release_reports/v1_",
            "release_reports/v2_",
            "v2_14_app_author_implementation_strategy.md",
            "examples/current/embedding",
            "V4 Preparatory Embedding Docs",
            "RTDL v2.10 is the current",
            "current v2.10",
            "current v2.14",
            "v2.x release position",
            "fast v2.x",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, combined)

    def test_history_indexes_explain_old_material_boundary(self) -> None:
        history = (ROOT / "docs" / "history" / "README.md").read_text(encoding="utf-8")
        release_history = (ROOT / "docs" / "history" / "release_reports" / "README.md").read_text(
            encoding="utf-8"
        )
        v4_archive = (ROOT / "docs" / "history" / "v4_preparatory_embedding" / "README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Historical Release Reports", history)
        self.assertIn("V4 preparatory embedding/C ABI archive", history)
        self.assertIn("authoritative only for its own tag", release_history)
        self.assertIn("V3.0 excludes embedding/SDK/zero-copy work", v4_archive)


if __name__ == "__main__":
    unittest.main()
