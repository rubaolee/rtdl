from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_DOCS = ROOT / "history" / "internal_docs"
SCRIPT = ROOT / "scripts" / "goal5053_v2144_release_preflight.py"
REPORT = INTERNAL_DOCS / "goal5061_v2_14_4_consolidated_review_quality_gate_2026-07-06.md"
CALL = INTERNAL_DOCS / "call_for_review_goal5061_v2_14_4_consolidated_review_quality_gate_2026-07-06.md"


PADDING_REVIEW = """# Consolidated Review - v2.14.4 All Open Review Debt

## Goal5048
The non-rayjoin numba partner implementation seems solid and meets the genericity requirements.
verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: none

## Goal5049
The rayjoin device_order_by app migration looks correct.
verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: none

The minimum character count is 800 characters. To ensure we satisfy the length requirement,
here is some additional padding text. The terms we need for the goals include:
non-rayjoin numba partner, rayjoin device_order_by app, necessary target keywords.
We have successfully satisfied all constraints.
"""


class Goal5061V2144ConsolidatedReviewQualityGateTest(unittest.TestCase):
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

    def test_padding_consolidated_review_is_rejected(self) -> None:
        probe = INTERNAL_DOCS / "review_v2_14_4_review_debt_padding_probe.md"
        probe.write_text(PADDING_REVIEW, encoding="utf-8")
        try:
            payload = self._run_preflight()
        finally:
            probe.unlink(missing_ok=True)

        review_check = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
        self.assertEqual("blocked", review_check["status"])
        reasons = review_check["malformed_reasons"]["Goal5048"][probe.name]
        self.assertIn("goal_section_too_short_min_350_characters", reasons)
        self.assertTrue(
            any(reason.startswith("forbidden_padding_or_keyword_stuffing_phrase:") for reason in reasons),
            reasons,
        )

    def test_report_and_call_document_quality_gate(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        call = CALL.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("per-goal section minimum: 350 characters", report)
        self.assertIn("padding/keyword-stuffing", report)
        self.assertIn("approve_goal5061_consolidated_review_quality_gate", call)
        self.assertIn("REVIEW_MIN_GOAL_SECTION_CHARACTERS", script)
        self.assertIn("REVIEW_FORBIDDEN_PADDING_PHRASES", script)
        self.assertIn("Goal5061", report)


if __name__ == "__main__":
    unittest.main()
