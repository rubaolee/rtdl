from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1943_v2_source_tree_only_release_decision_packet_2026-05-13.md"
HANDOFF = ROOT / "docs" / "handoff" / "GOAL1944_EXTERNAL_REVIEW_SOURCE_TREE_ONLY_POLICY.md"


class Goal1943V2SourceTreeOnlyReleaseDecisionPacketTest(unittest.TestCase):
    def test_packet_recommends_source_tree_only_and_blocks_install_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: source-tree-only-policy-ready-for-external-consensus", text)
        self.assertIn("Accept source-tree-only v2.0", text)
        self.assertIn("PYTHONPATH=src:.", text)
        for phrase in (
            "pip install rtdl",
            "pip install -e .",
            "RTDL is available as a Python package",
            "Install RTDL from PyPI",
            "Package-install support is validated",
        ):
            self.assertIn(phrase, text)

    def test_packet_requires_distinct_external_consensus(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Gemini", text)
        self.assertIn("Claude or another distinct non-Codex, non-Gemini AI", text)
        self.assertIn("Final 3-AI consensus file", text)
        self.assertIn("User release action", text)
        self.assertIn("does not broaden any performance claim", text)

    def test_external_review_handoff_exists(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("source-tree-only release policy", text)
        self.assertIn("package-install support explicitly out of scope", text)
        self.assertIn("goal1944_external_review_v2_source_tree_only_policy", text)
        self.assertIn("Codex+Codex does not count", text)


if __name__ == "__main__":
    unittest.main()
