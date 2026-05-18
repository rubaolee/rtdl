from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
FRONT = ROOT / "README.md"
DOCS = ROOT / "docs" / "README.md"
RELEASE = ROOT / "docs" / "release_reports" / "v2_0" / "README.md"
PARTNER = ROOT / "docs" / "partner_acceleration_boundaries.md"
CAPABILITY = ROOT / "docs" / "capability_boundaries.md"
ARCH = ROOT / "docs" / "current_architecture.md"
MAP = ROOT / "docs" / "public_documentation_map.md"
GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal2093V2PublicDocsBoundaryTest(unittest.TestCase):
    def test_front_page_marks_v2_as_released_with_boundaries(self) -> None:
        text = FRONT.read_text(encoding="utf-8")
        self.assertIn("## v2.0 Release", text)
        self.assertIn("current released version is `v2.0`", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("v2.0 Release Package", text)
        self.assertNotIn("fresh Claude-family final review is still missing", text)

    def test_docs_index_points_to_release_and_redline(self) -> None:
        text = DOCS.read_text(encoding="utf-8")
        self.assertIn("current released version is `v2.0`", text)
        self.assertIn("streaming exact", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("Codex, Claude, and Gemini", text)

    def test_release_package_preserves_allowed_and_blocked_wording(self) -> None:
        text = RELEASE.read_text(encoding="utf-8")
        self.assertIn("Status: released source-tree Python+partner+RTDL language boundary", text)
        self.assertIn("Version marker: `v2.0`", text)
        self.assertIn("not a package-install release", text)
        self.assertIn("No arbitrary PyTorch/CuPy acceleration claim", text)
        self.assertIn("Goal2322", text)

    def test_boundary_docs_keep_copilot_from_replacing_claude(self) -> None:
        partner = PARTNER.read_text(encoding="utf-8")
        self.assertIn("Copilot supplemental review", partner)
        self.assertIn("strict 3-AI consensus rule", partner)
        capability = CAPABILITY.read_text(encoding="utf-8")
        self.assertIn("source-tree Python+partner+RTDL release", capability)
        self.assertIn("Codex, Claude, and Gemini", capability)

    def test_architecture_and_map_state_current_status(self) -> None:
        arch = ARCH.read_text(encoding="utf-8")
        doc_map = MAP.read_text(encoding="utf-8")
        gate = GATE.read_text(encoding="utf-8")
        self.assertIn("RTDL v2.0 is the current source-tree", arch)
        self.assertIn("passed the\n3-AI consensus", arch)
        self.assertIn("v2.0 release", doc_map)
        self.assertIn("completed 3-AI consensus boundary", doc_map)
        self.assertIn("Current Status Note", gate)
        self.assertIn("v2.0 is the current source-tree", gate)


if __name__ == "__main__":
    unittest.main()
