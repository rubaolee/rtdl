from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1947_v2_source_tree_only_policy_consensus_2026-05-13.md"


class Goal1947V2SourceTreeOnlyPolicyConsensusTest(unittest.TestCase):
    def test_consensus_records_three_distinct_inputs(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Codex", text)
        self.assertIn("Gemini", text)
        self.assertIn("Claude", text)
        self.assertIn("goal1943_v2_source_tree_only_release_decision_packet", text)
        self.assertIn("goal1944_gemini_review_v2_source_tree_only_policy", text)
        self.assertIn("goal1945_claude_review_v2_source_tree_only_policy", text)
        self.assertIn("accept-with-boundary", text)

    def test_consensus_accepts_source_tree_only_but_blocks_install_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("The v2.0 release may be source-tree-only", text)
        self.assertIn("PYTHONPATH=src:.", text)
        self.assertIn("Package-install support is not part of this", text)
        self.assertIn("release", text)
        for phrase in (
            "pip install rtdl",
            "pip install -e .",
            "RTDL is available as a Python package",
            "Install RTDL from PyPI",
            "Package-install support is validated",
        ):
            self.assertIn(phrase, text)

    def test_consensus_does_not_authorize_release_or_broad_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize v2.0 release", text)
        self.assertIn("Whole-app speedup claims remain blocked", text)
        self.assertIn("Broad RT-core speedup claims remain blocked", text)
        self.assertIn("Arbitrary PyTorch/CuPy acceleration claims remain blocked", text)
        self.assertIn("The remaining", text)
        self.assertIn("hard blockers", text)


if __name__ == "__main__":
    unittest.main()
