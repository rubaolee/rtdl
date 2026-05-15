from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_DOCS = [
    "README.md",
    "docs/README.md",
    "docs/backend_maturity.md",
    "docs/current_architecture.md",
    "docs/current_main_support_matrix.md",
    "docs/app_engine_support_matrix.md",
    "docs/runtime_overhead_architecture.md",
    "docs/rtdl/README.md",
    "docs/rtdl/dsl_reference.md",
    "docs/rtdl/ir_and_lowering.md",
    "docs/rtdl/itre_app_model.md",
    "docs/rtdl/llm_authoring_guide.md",
    "docs/rtdl/programming_guide.md",
    "docs/rtdl/workload_cookbook.md",
]

ACTIVE_DOCS.extend(
    str(path.relative_to(ROOT)).replace("\\", "/")
    for path in sorted((ROOT / "docs" / "features").rglob("*.md"))
)

OLD_MARKER = re.compile(
    r"\bv0\.|\bv1\.|\bv0_|\bv1_|Goal\s*\d+|goal\s*\d+|"
    r"released `v|current released|old release|legacy|historical",
    re.IGNORECASE,
)


class Goal2099V2ApiInternalDocCleanupTest(unittest.TestCase):
    def test_active_api_internal_docs_do_not_mix_old_version_context(self) -> None:
        offenders: list[str] = []
        for rel in sorted(set(ACTIVE_DOCS)):
            text = (ROOT / rel).read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if OLD_MARKER.search(line):
                    offenders.append(f"{rel}:{line_no}: {line}")

        self.assertEqual([], offenders)

    def test_old_api_internal_docs_are_archived_outside_active_paths(self) -> None:
        self.assertFalse((ROOT / "docs" / "architecture_api_performance_overview.md").exists())
        self.assertFalse((ROOT / "docs" / "rtdl" / "minimal_itre_extension_demo_kernels.md").exists())
        self.assertFalse((ROOT / "docs" / "wiki_drafts" / "README.md").exists())

        archive = ROOT / "docs" / "history" / "legacy_api_internal_docs"
        self.assertTrue((archive / "architecture_api_performance_overview.md").exists())
        self.assertTrue((archive / "minimal_itre_extension_demo_kernels.md").exists())
        self.assertTrue((archive / "wiki_drafts" / "README.md").exists())

    def test_cleanup_report_lists_file_operations(self) -> None:
        report = (ROOT / "docs" / "reports" / "goal2099_v2_api_internal_doc_cleanup_2026-05-15.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "File-by-File Findings And Operations",
            "docs/backend_maturity.md",
            "docs/current_main_support_matrix.md",
            "docs/app_engine_support_matrix.md",
            "docs/rtdl/dsl_reference.md",
            "docs/history/legacy_api_internal_docs/",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
