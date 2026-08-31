from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5053_v2144_release_preflight.py"
REPORT = ROOT / "history" / "internal_docs" / "goal5060_v2_14_4_substantive_review_gate_hardening_2026-07-06.md"
CALL = ROOT / "history" / "internal_docs" / "call_for_review_goal5060_v2_14_4_substantive_review_gate_hardening_2026-07-06.md"
CONSOLIDATED_CALL = ROOT / "history" / "internal_docs" / "call_for_review_v2_14_4_all_open_review_debt_2026-07-06.md"


class Goal5060V2144SubstantiveReviewGateTest(unittest.TestCase):
    def _run_preflight(self) -> dict:
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
            return json.loads(output.read_text(encoding="utf-8"))

    def test_template_reviews_are_rejected_as_malformed(self) -> None:
        probe = ROOT / "history" / "internal_docs" / "review_goal5060_template_probe.md"
        probe.write_text(
            "# Review for Goal5060\n\n"
            "verdict_label: approve\n"
            "pass/fail/required_amendments: pass\n"
            "blocking_findings: None\n"
            "non_blocking_notes: None\n",
            encoding="utf-8",
        )
        try:
            payload = self._run_preflight()
        finally:
            probe.unlink(missing_ok=True)

        review_check = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
        self.assertEqual("blocked", review_check["status"])
        self.assertIn("malformed_reasons", review_check)

        reasons = review_check["malformed_reasons"]["Goal5060"]["review_goal5060_template_probe.md"]
        self.assertIn("too_short_min_800_characters", reasons)
        self.assertTrue(any(reason.startswith("missing_goal_specific_terms:") for reason in reasons))

    def test_gate_supports_substantive_consolidated_review_patterns(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("*review*v2_14_4*review*debt*.md", text)
        self.assertIn("*review*all_open_review_debt*.md", text)
        self.assertIn("REVIEW_REQUIRED_GOAL_TERMS", text)
        self.assertIn("REVIEW_MIN_GOAL_SECTION_CHARACTERS", text)
        self.assertIn("malformed_reasons", text)

    def test_reports_document_template_approval_failure(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        call = CALL.read_text(encoding="utf-8")
        consolidated = CONSOLIDATED_CALL.read_text(encoding="utf-8")
        self.assertIn("template", report.lower())
        self.assertIn("approval", report.lower())
        self.assertIn("minimum length: 800 characters", report)
        self.assertIn("malformed_reasons", report)
        self.assertIn("approve_goal5060_substantive_review_gate_hardening", call)
        self.assertIn("Goal5060", consolidated)


if __name__ == "__main__":
    unittest.main()
