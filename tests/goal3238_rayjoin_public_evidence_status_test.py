from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3238_rayjoin_public_evidence_status_after_row_continuation_2026-06-03.md"


class Goal3238RayJoinPublicEvidenceStatusTest(unittest.TestCase):
    def test_status_report_summarizes_all_three_families(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "PIP count",
            "PIP rows",
            "LSI count",
            "LSI rows",
            "Overlay count",
            "Overlay rows",
            "Overlay row scale",
            "233,766 rows, symmetric difference 0",
            "max_lsi_coordinate_delta = 0",
        ):
            self.assertIn(phrase, report)

    def test_status_report_names_remaining_gaps(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Full paper-scale Brazil county/soil datasets",
            "Cross-system RTDL-vs-RayJoin",
            "Multi-repeat steady-state statistics",
            "Device-resident row-stream continuation",
            "Broader GPU-family evidence",
        ):
            self.assertIn(phrase, report)

    def test_status_report_preserves_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "does not authorize release",
            "public speedup claims",
            "broad RT-core claims",
            "true zero-copy claims",
            "RTDL beats RayJoin",
            "RayJoin paper-reproduction claims",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
