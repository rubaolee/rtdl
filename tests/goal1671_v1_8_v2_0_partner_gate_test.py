from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"
CURRENT_ARCHITECTURE = ROOT / "docs" / "current_architecture.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
PUBLIC_MAP = ROOT / "docs" / "public_documentation_map.md"
GOAL1670 = ROOT / "docs" / "reviews" / "goal1670_all_external_partner_analysis_consensus_2026-05-10.md"


class Goal1671V18V20PartnerGateTest(unittest.TestCase):
    def test_gate_records_active_roadmap_and_partner_priority(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in (
            "`v1.8` finishes Python+RTDL productization",
            "`v2.0` finishes Python+partner+RTDL",
            "Protocol first. PyTorch reference first. CuPy conformance alongside it.",
            "Primary public/reference partner | PyTorch",
            "Lightweight conformance and CI partner | CuPy",
            "must not link directly against PyTorch, CuPy",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_gate_preserves_app_agnostic_and_claim_boundaries(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        for phrase in (
            "must not become a new route for app-shaped native code",
            "True zero-copy is a measured claim boundary",
            "RTDL accelerates arbitrary PyTorch/CuPy programs",
            "RTDL native internals are fully app-agnostic",
            "Device-resident handoff",
            "host staging must be reported separately",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_current_docs_link_the_live_gate(self) -> None:
        for path in (CURRENT_ARCHITECTURE, DOCS_INDEX, PUBLIC_MAP):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("v1_8_v2_0_python_partner_rtdl_gate.md", text)

    def test_goal1670_remains_the_consensus_source(self) -> None:
        text = GOAL1670.read_text(encoding="utf-8")
        self.assertIn(
            "Protocol first. PyTorch reference first. CuPy conformance alongside it.",
            text,
        )
        self.assertIn("Goal1670 supersedes Goal1669 only on first-partner priority", text)


if __name__ == "__main__":
    unittest.main()
