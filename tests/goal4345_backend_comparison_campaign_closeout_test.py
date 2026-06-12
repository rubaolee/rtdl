from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from rtdsl.backend_comparison_campaign_closeout import (
    backend_comparison_campaign_closeout,
    validate_backend_comparison_campaign_closeout,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_backend_comparison_campaign_closeout.py"
REPORT = ROOT / "docs" / "reports" / "goal4345_backend_comparison_campaign_closeout_2026-06-11.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4345_backend_comparison_campaign_closeout_2026-06-11.json"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal4345_gemini_backend_comparison_closeout_review_2026-06-11.md"
CONSENSUS_REPORT = (
    ROOT / "docs" / "reports" / "goal4345_external_review_and_campaign_closeout_consensus_2026-06-11.md"
)


class Goal4345BackendComparisonCampaignCloseoutTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = backend_comparison_campaign_closeout()

    def test_validation_accepts_closeout_sources(self) -> None:
        validation = validate_backend_comparison_campaign_closeout()
        self.assertEqual("accept", validation["status"], validation["errors"])
        self.assertEqual(0, self.payload["comparison_buckets"]["rt_core_remaining_high_leverage_work_count"])
        self.assertEqual(0, self.payload["comparison_buckets"]["embree_same_contract_scale_pair_needed_count"])
        self.assertEqual(4, self.payload["comparison_buckets"]["contract_choice_blocker_count"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["release_authorized"])

    def test_ready_answers_are_yes_but_bounded(self) -> None:
        answers = self.payload["answers"]
        self.assertEqual(
            "yes_internal_current_optix_paths",
            answers["ready_to_use_high_performance_nvidia_rt_cores"]["answer"],
        )
        self.assertEqual(
            "yes_for_native_embree_primitive_rows_with_contract_boundaries",
            answers["ready_to_use_high_performance_intel_embree_cpus"]["answer"],
        )
        self.assertIn("not release authorization", answers["ready_to_use_high_performance_nvidia_rt_cores"]["boundary"])
        self.assertIn("Four apps still require a contract choice", answers["ready_to_use_high_performance_intel_embree_cpus"]["boundary"])

    def test_partner_policy_does_not_force_numba_universally(self) -> None:
        policy = self.payload["partner_policy"]
        self.assertEqual("do_not_force_numba_universally", policy["default"])
        self.assertIn("hold the continuation contract fixed", policy["configured_route_table"])
        self.assertIn("Numba is acceptable", policy["configured_route_table"])
        self.assertIn("not an OptiX-vs-Embree backend comparison", policy["partner_only_rows"])
        self.assertFalse(policy["automatic_partner_selection_authorized"])

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "closeout.json"
            out_md = Path(tmp) / "closeout.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Goal4345", report)
            self.assertIn("do_not_force_numba_universally", report)
            self.assertIn("NVIDIA RT cores: yes", report)
            self.assertIn("Intel Embree CPUs: yes", report)

    def test_committed_report_and_json_artifact_are_present(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("Backend Comparison Campaign Closeout", text)
        self.assertIn("Partner Policy", text)
        self.assertEqual("accept", payload["validation"]["status"])
        self.assertEqual(5, payload["comparison_buckets"]["fresh_scale_comparison_row_count"])

    def test_external_review_and_consensus_note_are_present(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS_REPORT.read_text(encoding="utf-8")
        self.assertIn("verdict: accept", gemini)
        self.assertIn("required fixes: none", gemini.lower())
        self.assertIn("Claude review: unavailable", consensus)
        self.assertIn("Ran 44 tests", consensus)
        self.assertIn("do not force Numba universally", consensus)


if __name__ == "__main__":
    unittest.main()
