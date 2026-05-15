from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LEARNER_DOCS = [
    "README.md",
    "docs/README.md",
    "docs/quick_tutorial.md",
    "docs/current_architecture.md",
    "docs/capability_boundaries.md",
    "docs/public_documentation_map.md",
    "docs/rtdl/README.md",
    "docs/rtdl/ir_and_lowering.md",
    "docs/rtdl/programming_guide.md",
    "docs/rtdl/dsl_reference.md",
    "docs/rtdl/itre_app_model.md",
    "docs/rtdl/workload_cookbook.md",
    "docs/rtdl_feature_guide.md",
    "docs/app_example_quickstart.md",
    "docs/application_catalog.md",
    "docs/tutorials/README.md",
    "docs/tutorials/hello_world.md",
    "docs/tutorials/partner_anyhit.md",
    "docs/tutorials/partner_optix_zero_copy_anyhit.md",
    "docs/release_reports/v2_0_pre_release_candidate.md",
]
REPORT = ROOT / "docs" / "reports" / "goal2094_v2_learner_doc_single_version_cleanup_2026-05-15.md"
LEGACY = ROOT / "docs" / "history" / "legacy_learner_doc_version_notes.md"


class Goal2094V2LearnerDocSingleVersionCleanupTest(unittest.TestCase):
    def test_learner_docs_do_not_expose_old_version_markers(self) -> None:
        old_version_pattern = re.compile(
            r"\bv0\.|\bv1\.|\bv0_|\bv1_|released `v|current released|Goal\s*\d+",
            re.IGNORECASE,
        )
        offenders: list[str] = []
        for rel in LEARNER_DOCS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if old_version_pattern.search(line):
                    offenders.append(f"{rel}:{line_no}: {line}")
        self.assertEqual([], offenders)

    def test_current_docs_state_v2_pre_release_boundary(self) -> None:
        for rel in ("README.md", "docs/README.md", "docs/current_architecture.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("v2.0", text)
            self.assertIn("pre-release candidate", text)
        front = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("fresh Claude-family review", front)

    def test_legacy_context_has_separate_home(self) -> None:
        text = LEGACY.read_text(encoding="utf-8")
        self.assertIn("parking place for version-history context", text)
        self.assertIn("release-report archive", text)
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("File-by-File Findings And Operations", report)
        self.assertIn("docs/current_architecture.md", report)
        self.assertIn("docs/rtdl/dsl_reference.md", report)


if __name__ == "__main__":
    unittest.main()
