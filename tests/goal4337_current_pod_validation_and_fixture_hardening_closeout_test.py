from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4337_current_pod_validation_and_fixture_hardening_closeout_2026-06-11.md"
)
ALLPASS = ROOT / "docs" / "reports" / "goal4329_current_pod_validation" / "scale_summary_allpass.json"
RUNNER_FIXTURE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4329_current_pod_validation"
    / "goal4332_runner_option"
    / "rayjoin_materialized_summary.json"
)
BUNDLE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4329_current_pod_validation"
    / "goal4332_bundle_pass_through_validation_fixed"
    / "bundle_summary.json"
)


class Goal4337CurrentPodValidationAndFixtureCloseoutTest(unittest.TestCase):
    def test_closeout_report_records_evidence_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4329", text)
        self.assertIn("Goal4332", text)
        self.assertIn("--materialize-rayjoin-public-cdb", text)
        self.assertIn("json_source: artifact", text)
        self.assertIn("Claude follow-up review for Goal4332 remains", text)
        self.assertIn("does not authorize release action", text)
        self.assertIn("33 tests passed", text)

    def test_referenced_pod_artifacts_remain_accepting_and_non_authorizing(self) -> None:
        allpass = json.loads(ALLPASS.read_text(encoding="utf-8"))
        self.assertIs(allpass["all_pass"], True)
        self.assertEqual(10, allpass["json_pass_count"])
        self.assertFalse(allpass["release_authorized"])
        self.assertFalse(allpass["public_speedup_claim_authorized"])

        runner_fixture = json.loads(RUNNER_FIXTURE.read_text(encoding="utf-8"))
        self.assertIs(runner_fixture["all_pass"], True)
        self.assertEqual("materialized", runner_fixture["rayjoin_public_cdb_fixture"]["status"])
        self.assertFalse(runner_fixture["release_authorized"])
        self.assertFalse(runner_fixture["public_speedup_claim_authorized"])

        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        self.assertEqual("pass", bundle["status"])
        step = next(item for item in bundle["steps"] if item["name"] == "scale_profile_hardware_run")
        self.assertEqual("artifact", step["json_source"])
        self.assertIs(step["json_parseable"], True)
        self.assertEqual([], step["claim_flag_violations"])
        self.assertFalse(bundle["release_authorized"])
        self.assertFalse(bundle["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
