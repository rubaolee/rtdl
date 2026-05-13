from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1814_v2_0_strict_birth_gate_2026-05-13.md"
GOAL1810 = ROOT / "docs" / "reports" / "goal1810_v2_0_release_readiness_audit_2026-05-13.md"
GOAL1813 = ROOT / "docs" / "reviews" / "goal1813_3ai_consensus_v2_0_release_readiness_2026-05-13.md"
GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"
README = ROOT / "README.md"
DOCS = ROOT / "docs" / "README.md"
PARTNER_TUTORIAL = ROOT / "docs" / "tutorials" / "partner_anyhit.md"


class Goal1814V20StrictBirthGateTest(unittest.TestCase):
    def test_strict_gate_blocks_v2_0_release_label(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Status: `needs-more-evidence`", text)
        self.assertIn("not the birth of v2.0", text)
        self.assertIn("Blocked wording before v2.0", text)
        self.assertIn("`RTDL v2.0 is released.`", text)
        self.assertIn("positive rule for what RTDL does", text)

    def test_required_blockers_are_first_class(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "True zero-copy",
            "Direct device-pointer handoff",
            "Broad RT-core speedup",
            "Whole-application acceleration",
            "Arbitrary PyTorch/CuPy acceleration boundary",
            "Package-install support",
            "3-AI-ratified release statement",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_prior_release_ready_files_are_superseded(self) -> None:
        old_audit = GOAL1810.read_text(encoding="utf-8")
        old_consensus = GOAL1813.read_text(encoding="utf-8")
        self.assertIn("Status: `superseded-by-stricter-v2.0-birth-gate`", old_audit)
        self.assertIn("Goal1814 supersedes", old_audit)
        self.assertIn("Verdict: `superseded-by-goal1814`", old_consensus)
        self.assertIn("no longer authorizes a v2.0 release", old_consensus)

    def test_user_facing_docs_call_partner_path_preview_not_release(self) -> None:
        for path in (README, DOCS, PARTNER_TUTORIAL, GATE):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("preview", text.lower())
                self.assertIn("true zero-copy", text)
                self.assertIn("direct device-pointer", text)
                self.assertIn("whole-application", text)


if __name__ == "__main__":
    unittest.main()
