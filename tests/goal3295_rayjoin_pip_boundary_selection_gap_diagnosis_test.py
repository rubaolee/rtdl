from __future__ import annotations

from pathlib import Path
import unittest


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3295_rayjoin_pip_boundary_selection_gap_diagnosis_2026-06-04.md"
FUTURE = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal3295RayJoinPipBoundarySelectionGapDiagnosisTest(unittest.TestCase):
    def test_report_records_boundary_selection_as_generic_next_primitive(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("candidate_write_pass = 0.0", text)
        self.assertIn("candidate_download = 0.0", text)
        self.assertIn("exact_refine = 0.0", text)
        self.assertIn("point_closed_shape_best_boundary_crossing_2d", text)
        self.assertIn("point_closed_shape_first_crossing_2d", text)
        self.assertIn("not the same contract", text)
        self.assertIn("Do not put RayJoin-specific", text)
        self.assertIn("does not authorize", text)

    def test_future_list_captures_generic_boundary_selection_without_rayjoin_abi(self) -> None:
        text = FUTURE.read_text(encoding="utf-8")

        self.assertIn("Generic Closed-Shape Boundary Selection", text)
        self.assertIn("prepared edge/range traversal", text)
        self.assertIn("typed boundary-event columns", text)
        self.assertIn("do not merge RayJoin-specific", text)


if __name__ == "__main__":
    unittest.main()
