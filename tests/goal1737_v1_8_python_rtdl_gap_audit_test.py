import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1737_v1_8_python_rtdl_gap_audit_2026-05-12.md"


class Goal1737V18PythonRtdlGapAuditTest(unittest.TestCase):
    def test_report_keeps_v1_8_close_but_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1_8_close_but_not_release_ready", text)
        self.assertIn("v1.8 is not ready to tag yet", text)
        self.assertIn("not a release command", text)

    def test_report_names_required_remaining_gates(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Release-Specific v1.8 Decision Artifact",
            "Public Documentation Alignment",
            "Packaging And Install Boundary",
            "Version And Tag Discipline",
            "Test Scope Definition",
            "Partner Track Remains v2.0",
        ):
            self.assertIn(phrase, text)

    def test_report_records_packaging_gap_without_mutating_version(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("no `pyproject.toml`", text)
        self.assertIn("no `setup.py`", text)
        self.assertIn("no `setup.cfg`", text)
        self.assertIn("`VERSION` still reads `v1.5`", text)
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v1.8")

    def test_report_preserves_partner_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1.8` finishes Python+RTDL productization", text)
        self.assertIn("v2.0` finishes Python+partner+RTDL", text)
        self.assertIn("protocol first, PyTorch reference first, CuPy conformance", text)
        self.assertIn("v1.8 should not absorb unfinished partner promises", text)


if __name__ == "__main__":
    unittest.main()
