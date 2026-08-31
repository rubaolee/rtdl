from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "docs" / "reports" / "goal3832_short_row_stress_candidates_a5000" / "summary.json"
FOLLOWUP = (
    ROOT
    / "docs"
    / "reports"
    / "goal3832_short_row_stress_candidates_followup_a5000"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3832_short_row_stress_candidate_calibration_a5000_2026-06-07.md"


class Goal3832ShortRowStressCandidateCalibrationA5000Test(unittest.TestCase):
    def test_primary_artifact_records_expected_passes_and_fail_closed_contact_probe(self) -> None:
        payload = json.loads(PRIMARY.read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in payload["rows"]}

        self.assertEqual(payload["commit"], "5cdb1cb5")
        self.assertFalse(payload["all_pass"])
        self.assertEqual(rows["hausdorff_copies4096"]["status"], "pass")
        self.assertEqual(rows["hausdorff_copies8192"]["status"], "pass")
        self.assertEqual(rows["contact_grid128"]["status"], "pass")
        self.assertEqual(rows["contact_grid256"]["status"], "fail")
        self.assertEqual(rows["contact_grid256"]["returncode"], 1)
        self.assertEqual(rows["triangle_copies32768"]["status"], "pass")
        self.assertEqual(rows["rayjoin_all_prepared_count_repeat50"]["status"], "pass")
        self.assertEqual(rows["rayjoin_pip_count_repeat500"]["status"], "pass")

    def test_followup_artifact_records_usable_stress_candidates(self) -> None:
        payload = json.loads(FOLLOWUP.read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in payload["rows"]}

        self.assertTrue(payload["all_pass"])
        self.assertEqual(rows["contact_grid256_cap256"]["status"], "pass")
        self.assertGreater(rows["contact_grid256_cap256"]["elapsed_sec"], 3.0)
        self.assertEqual(rows["hausdorff_copies32768"]["status"], "pass")
        self.assertGreater(rows["hausdorff_copies32768"]["elapsed_sec"], 5.0)
        self.assertEqual(rows["triangle_copies131072"]["status"], "pass")
        self.assertGreater(rows["triangle_copies131072"]["elapsed_sec"], 7.0)

    def test_report_records_stress_candidate_boundary_and_next_targets(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3832",
            "does not change the current default scale-profile registry",
            "hausdorff_copies32768",
            "contact_grid256_cap256",
            "correct fail-closed bounded-collect overflow",
            "triangle_copies131072",
            "rayjoin_all_prepared_count_repeat50",
            "larger RayJoin public-CDB scale row",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
