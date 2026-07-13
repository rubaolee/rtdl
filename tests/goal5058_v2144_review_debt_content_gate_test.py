from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5053_v2144_release_preflight.py"
REPORT = ROOT / "history" / "internal_docs" / "goal5058_v2_14_4_review_debt_content_gate_2026-07-06.md"
CALL = ROOT / "history" / "internal_docs" / "call_for_review_goal5058_v2_14_4_review_debt_content_gate_2026-07-06.md"


class Goal5058V2144ReviewDebtContentGateTest(unittest.TestCase):
    def test_preflight_reports_review_content_shape_fields_after_review_retired(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preflight.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--allow-blocked",
                    "--output-json",
                    str(output),
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
        review_check = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
        self.assertIn("malformed", review_check)
        self.assertIn("malformed_reasons", review_check)
        self.assertEqual("pass", review_check["status"])
        self.assertEqual([], review_check["open"])
        self.assertEqual({}, review_check["malformed"])
        self.assertIn("review_v2_14_4_all_open_review_debt_2026-07-06.md", review_check["found"]["Goal5058"])

    def test_preflight_still_rejects_template_review_files(self) -> None:
        probe = ROOT / "history" / "internal_docs" / "review_goal5058_template_probe.md"
        probe.write_text(
            "# Review for Goal5058\n\nverdict_label: approve\nblocking_findings: none\n",
            encoding="utf-8",
        )
        try:
            with tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "preflight.json"
                proc = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--allow-blocked",
                        "--output-json",
                        str(output),
                    ],
                    cwd=str(ROOT),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(0, proc.returncode, proc.stderr)
                payload = json.loads(output.read_text(encoding="utf-8"))
            review_check = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
            self.assertIn("Goal5058", review_check["malformed_reasons"])
            reasons = review_check["malformed_reasons"]["Goal5058"]["review_goal5058_template_probe.md"]
            self.assertIn("too_short_min_800_characters", reasons)
        finally:
            probe.unlink(missing_ok=True)

    def test_report_and_call_preserve_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        call = CALL.read_text(encoding="utf-8")
        self.assertIn("completed_review_debt_content_gate__external_review_still_pending", report)
        self.assertIn("placeholder_review_files_do_not_retire_debt", report)
        self.assertIn("review_debt_retired", report)
        self.assertIn("approve_goal5058_review_debt_content_gate", call)


if __name__ == "__main__":
    unittest.main()
