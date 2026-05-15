from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class Goal2100DocsInformationArchitectureReorgTest(unittest.TestCase):
    def test_three_reader_doors_exist(self) -> None:
        for rel in (
            "docs/learn/README.md",
            "docs/research/README.md",
            "docs/audit/README.md",
        ):
            with self.subTest(rel=rel):
                self.assertTrue((ROOT / rel).exists())

    def test_top_level_docs_are_not_cluttered_with_old_logs(self) -> None:
        root_markdown = sorted(path.name for path in DOCS.glob("*.md"))
        offenders = [
            name
            for name in root_markdown
            if name.startswith("goal_") or name.startswith("v0_") or name.startswith("v1_")
        ]
        self.assertEqual([], offenders)
        self.assertLessEqual(len(root_markdown), 20)

    def test_moved_archives_and_research_notes_exist(self) -> None:
        for rel in (
            "docs/history/root_archive/goal_logs/goal_432_v0_7_rt_db_phase_split_perf_clarification.md",
            "docs/history/root_archive/version_notes/v1_0_rtx_app_status.md",
            "docs/research/rayjoin/rayjoin_target.md",
            "docs/research/future/workloads_and_research_foundations.md",
            "docs/audit/process/audit_flow.md",
            "docs/audit/runbooks/rtx_cloud_single_session_runbook.md",
        ):
            with self.subTest(rel=rel):
                self.assertTrue((ROOT / rel).exists())

    def test_docs_indices_explain_audience_model(self) -> None:
        docs_index = (DOCS / "README.md").read_text(encoding="utf-8")
        public_map = (DOCS / "public_documentation_map.md").read_text(encoding="utf-8")
        report = (DOCS / "reports" / "goal2100_docs_information_architecture_reorg_2026-05-15.md").read_text(
            encoding="utf-8"
        )

        for text in (docs_index, public_map, report):
            with self.subTest(text=text[:32]):
                self.assertIn("Learn", text)
                self.assertIn("Research", text)
                self.assertIn("Audit", text)


if __name__ == "__main__":
    unittest.main()
