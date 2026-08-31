from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3827_scale_profile_file_stdout_correction_a5000_2026-06-07.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3827_scale_profile_file_stdout_a5000" / "summary.json"


class Goal3827ScaleProfileFileStdoutCorrectionA5000Test(unittest.TestCase):
    def test_file_stdout_probe_records_corrected_pass_timeout_set(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in payload["rows"]}

        self.assertEqual(payload["commit"], "15c2d437")
        self.assertTrue(payload["stdout_to_file_probe"])
        self.assertFalse(payload["all_pass"])
        self.assertEqual(payload["json_pass_count"], 9)
        self.assertEqual(len(rows), 10)

        timeout_rows = {name for name, row in rows.items() if row["status"] == "timeout"}
        self.assertEqual(timeout_rows, {"rt_dbscan_numba_65536"})

    def test_large_stdout_false_negatives_are_corrected(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in payload["rows"]}

        robot = rows["robot_collision_4096"]
        self.assertEqual(robot["status"], "pass")
        self.assertTrue(robot["json_ok"])
        self.assertLess(robot["elapsed_sec"], 90.0)
        self.assertGreater(robot["stdout_bytes"], 100_000)

        barnes = rows["barnes_hut_numba_8192"]
        self.assertEqual(barnes["status"], "pass")
        self.assertTrue(barnes["json_ok"])
        self.assertLess(barnes["elapsed_sec"], 10.0)
        self.assertGreater(barnes["stdout_bytes"], 800_000)

    def test_rt_dbscan_65k_remains_the_real_timeout(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        row = {row["name"]: row for row in payload["rows"]}["rt_dbscan_numba_65536"]

        self.assertEqual(row["status"], "timeout")
        self.assertFalse(row["json_ok"])
        self.assertEqual(row["stdout_bytes"], 0)
        self.assertGreaterEqual(row["elapsed_sec"], 300.0)

    def test_report_records_methodology_correction_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3827",
            "Popen(..., stdout=PIPE)",
            "Barnes-Hut and robot collision were false negatives",
            "stdout and stderr redirected to files",
            "Nine of ten larger candidates pass",
            "still included CPU reference validation",
            "same 65k performance row passes",
            "does not authorize release action",
            "automatic partner selection",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
