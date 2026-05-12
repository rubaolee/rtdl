from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1679_pod_full_suite_triage_2026-05-10.md"
ROADMAP_GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal1679PodFullSuiteTriageTest(unittest.TestCase):
    def test_report_records_broad_suite_result(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'",
            "Ran 3613 tests in 332.008s",
            "FAILED (failures=65, errors=31, skipped=283)",
            "This is not a v1.8 release pass.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_separates_focused_gate_from_release_suite(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "The focused current gate remains green",
            "make build` and `make build-embree` also pass",
            "historical public-doc pinning tests",
            "repository-wide test\nsuite is not yet a release-quality green bar",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_roadmap_gate_links_full_suite_triage(self) -> None:
        gate_text = ROADMAP_GATE.read_text(encoding="utf-8")
        self.assertIn("goal1679_pod_full_suite_triage_2026-05-10.md", gate_text)


if __name__ == "__main__":
    unittest.main()
