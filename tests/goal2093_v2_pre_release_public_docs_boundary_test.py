from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
FRONT = ROOT / "README.md"
DOCS = ROOT / "docs" / "README.md"
PRE_RELEASE = ROOT / "docs" / "release_reports" / "v2_0_pre_release_candidate_after_goal2086.md"
PARTNER = ROOT / "docs" / "partner_acceleration_boundaries.md"
CAPABILITY = ROOT / "docs" / "capability_boundaries.md"
ARCH = ROOT / "docs" / "current_architecture.md"
MAP = ROOT / "docs" / "public_documentation_map.md"
GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal2093V2PreReleasePublicDocsBoundaryTest(unittest.TestCase):
    def test_front_page_marks_v2_as_pre_release_not_final_release(self) -> None:
        text = FRONT.read_text(encoding="utf-8")
        self.assertIn("## v2.0 Pre-Release Candidate", text)
        self.assertIn("not a final v2.0 release", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("fresh Claude-family final review is still missing", text)
        self.assertIn("v2.0 Pre-Release Candidate", text)

    def test_docs_index_points_to_pre_release_candidate_and_redline(self) -> None:
        text = DOCS.read_text(encoding="utf-8")
        self.assertIn("v2.0 pre-release candidate", text)
        self.assertIn("streaming exact", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("fresh Claude-family review is unavailable", text)

    def test_pre_release_report_preserves_allowed_and_blocked_wording(self) -> None:
        text = PRE_RELEASE.read_text(encoding="utf-8")
        self.assertIn("Status: `pre-release-candidate`", text)
        self.assertIn("RTDL v2.0 is not published yet", text)
        self.assertIn("Claude-family review is still missing", text)
        self.assertIn('"v2.0 is released."', text)
        self.assertIn('"RTDL accelerates arbitrary PyTorch or CuPy programs."', text)
        self.assertIn('"RTDL supports package installation."', text)

    def test_boundary_docs_keep_copilot_from_replacing_claude(self) -> None:
        partner = PARTNER.read_text(encoding="utf-8")
        self.assertIn("Do not use Copilot supplemental review as a replacement", partner)
        self.assertIn("strict 3-AI consensus redline", partner)
        capability = CAPABILITY.read_text(encoding="utf-8")
        self.assertIn("pre-release candidate", capability)
        self.assertIn("fresh Claude-family review", capability)

    def test_architecture_and_map_state_current_status(self) -> None:
        arch = ARCH.read_text(encoding="utf-8")
        doc_map = MAP.read_text(encoding="utf-8")
        gate = GATE.read_text(encoding="utf-8")
        self.assertIn("RTDL v2.0 is a pre-release candidate", arch)
        self.assertIn("final release is still held", arch)
        self.assertIn("v2.0-facing", doc_map)
        self.assertIn("strict 3-AI consensus redline", doc_map)
        self.assertIn("Current Status Note", gate)
        self.assertIn("fresh Claude-family review lands", gate)


if __name__ == "__main__":
    unittest.main()
