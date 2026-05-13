from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1902_v2_source_tree_only_release_exception_proposal_2026-05-13.md"


class Goal1902V2SourceTreeOnlyReleaseExceptionProposalTest(unittest.TestCase):
    def test_proposal_allows_source_tree_only_but_blocks_package_install_wording(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: proposal-needs-3ai-review", text)
        self.assertIn("source-tree-only", text)
        self.assertIn("PYTHONPATH=src:.", text)
        for phrase in (
            "pip install rtdl",
            "pip install -e .",
            "RTDL is available as a Python package",
            "Install RTDL from PyPI",
            "Package-install support is validated",
        ):
            self.assertIn(phrase, text)

    def test_proposal_requires_distinct_ai_consensus_and_keeps_other_blockers(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("3-AI consensus", text)
        self.assertIn("second distinct external AI", text)
        self.assertIn("RTX pod evidence is still required", text)
        self.assertIn("Whole-app and broad RT-core speedup claims remain evidence-limited", text)
        self.assertIn("Final v2.0 release still requires", text)


if __name__ == "__main__":
    unittest.main()
