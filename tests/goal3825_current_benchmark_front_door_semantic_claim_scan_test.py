from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3825_current_benchmark_front_door_semantic_claim_scan_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3825_current_benchmark_front_door_semantic_a5000" / "summary.json"
RUNNER = ROOT / "scripts" / "goal3823_current_benchmark_front_door_runner.py"


class Goal3825CurrentBenchmarkFrontDoorSemanticClaimScanTest(unittest.TestCase):
    def test_runner_contains_recursive_forbidden_claim_scan(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("FORBIDDEN_TRUE_FLAGS", text)
        self.assertIn("_find_forbidden_true_flags", text)
        self.assertIn("_semantic_stdout_check", text)
        self.assertIn("claim_flag_violations", text)
        self.assertIn("stdout_json_parseable", text)

    def test_a5000_artifact_has_json_and_zero_claim_violations_for_all_rows(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_pass"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertEqual(len(payload["rows"]), 10)

        for row in payload["rows"]:
            semantic = row["semantic_stdout_check"]
            self.assertEqual(row["status"], "pass", row["row_id"])
            self.assertTrue(semantic["stdout_json_parseable"], row["row_id"])
            self.assertIsNone(semantic["stdout_json_error"], row["row_id"])
            self.assertEqual(semantic["claim_flag_violations"], [], row["row_id"])

    def test_report_records_semantic_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3825",
            "semantic_stdout_check",
            "all ten stdout payloads parsed as JSON",
            "zero violations",
            "does not authorize release action",
            "not a performance result",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
