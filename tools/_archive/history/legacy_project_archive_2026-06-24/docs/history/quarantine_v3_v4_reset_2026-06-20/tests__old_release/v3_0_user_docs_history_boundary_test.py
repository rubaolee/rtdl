from __future__ import annotations

from pathlib import Path
import re
import unittest

from scripts import run_test_matrix


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
    def assert_no_files_under(self, path: Path) -> None:
        if not path.exists():
            return
        user_files = [
            item.relative_to(ROOT).as_posix()
            for item in path.rglob("*")
            if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc"
        ]
        self.assertEqual([], user_files)

    def test_release_reports_directory_is_current_only(self) -> None:
        names = {path.name for path in (ROOT / "docs" / "release_reports").iterdir()}
        self.assertEqual({"README.md", "v3_0_2"}, names)
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v3_0_1").is_dir())
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v3_0").is_dir())
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v2_14").is_dir())
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v1_0").is_dir())
        self.assertTrue((ROOT / "docs" / "history" / "release_reports" / "v0_9_8").is_dir())

    def test_learn_and_current_examples_are_v3_only(self) -> None:
        self.assertFalse((ROOT / "docs" / "learn" / "v2_14_app_author_implementation_strategy.md").exists())
        self.assertFalse((ROOT / "docs" / "learn" / "v3_0_c_abi_draft.md").exists())
        self.assert_no_files_under(ROOT / "examples" / "current" / "embedding")
        self.assertTrue((ROOT / "docs" / "history" / "learn" / "v2_14_app_author_implementation_strategy.md").exists())
        self.assertTrue((ROOT / "docs" / "history" / "v4_preparatory_embedding" / "v3_0_c_abi_draft.md").exists())
        self.assertTrue((ROOT / "docs" / "history" / "v4_preparatory_embedding" / "examples" / "embedding").is_dir())

    def test_v4_preparatory_artifacts_are_not_repo_front_door(self) -> None:
        self.assertFalse((ROOT / "include" / "rtdl" / "rtdl.h").exists())
        self.assertFalse((ROOT / "packaging" / "rtdl-c-api.pc").exists())
        self.assertFalse((ROOT / "packaging" / "rtdl-c-api-config.cmake").exists())
        staging = ROOT / "docs" / "history" / "v4_preparatory_embedding" / "staging"
        self.assertTrue((staging / "README.md").exists())
        self.assertTrue((staging / "include" / "rtdl" / "rtdl.h").exists())
        self.assertTrue((staging / "packaging" / "rtdl-c-api.pc").exists())
        self.assertTrue((staging / "packaging" / "rtdl-c-api-config.cmake").exists())

    def test_makefile_public_targets_do_not_advertise_c_api(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        default_help = makefile.split("help:", 1)[1].split("help-v4-prep:", 1)[0]
        for phrase in ("c-api", "C ABI", "V4 preparatory", "stage-c-api", "package-c-api-stage"):
            self.assertNotIn(phrase, default_help)
        reviewer_help = makefile.split("help-v4-prep:", 1)[1].split("build-apple-rt:", 1)[0]
        self.assertIn("Reviewer-only V4 preparatory targets", reviewer_help)
        self.assertIn("stage-c-api", reviewer_help)
        self.assertIn("scripts/run_test_matrix.py --group v3_current", makefile)
        self.assertIn("test-all:", makefile)

    def test_v3_current_matrix_excludes_v4_preparatory_modules(self) -> None:
        v3_modules = run_test_matrix.group_modules("v3_current")
        v4_modules = run_test_matrix.group_modules("v4_prep")
        forbidden_tokens = (
            "c_abi",
            "embedd",
            "zero_copy",
            "ctypes",
            "dlpack",
            "binding_interop",
            "toolchain_support",
            "neutral_buffer",
        )
        for module in v3_modules:
            for token in forbidden_tokens:
                self.assertNotIn(token, module)
        self.assertTrue(any("c_abi" in module for module in v4_modules))
        self.assertTrue(any("embedd" in module for module in v4_modules))
        self.assertTrue(any("zero_copy" in module for module in v4_modules))

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

    def test_benchmark_index_keeps_v4_prep_as_hidden_audit_anchors(self) -> None:
        index = (ROOT / "docs" / "learn" / "benchmark_evidence_index.md").read_text(encoding="utf-8")
        visible = re.sub(r"<!--.*?-->", "", index, flags=re.DOTALL)
        self.assertIn("V4 preparatory embedding/C ABI anchors are archived", visible)
        self.assertNotIn("Goal4550 C ABI draft", visible)
        self.assertNotIn("Goal4613 prefix-stage C examples smoke", visible)
        self.assertIn("Goal4550 C ABI draft", index)
        self.assertIn("Goal4613 prefix-stage C examples smoke", index)

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
