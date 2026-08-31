from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3828_current_benchmark_scale_profile_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3876_scale_runner_prepared_session_profile_integration_2026-06-08.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3876_scale_runner_profile_integration_a5000" / "summary.json"


class Goal3876ScaleRunnerPreparedSessionProfileIntegrationTest(unittest.TestCase):
    def _dry_run(self, *only: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "payload.json"
            command = [
                sys.executable,
                str(RUNNER),
                "--dry-run",
                "--output-json",
                str(output),
            ]
            for value in only:
                command.extend(["--only", value])
            subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            return json.loads(output.read_text(encoding="utf-8"))

    def test_full_dry_run_carries_prepared_session_summary(self) -> None:
        payload = self._dry_run()
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["prepared_session_residency_validation"]["status"], "accept")
        self.assertEqual(payload["selected_prepared_session_residency_profile_count"], 4)
        self.assertGreater(
            payload["prepared_session_residency_summary"]["geomean_prepare_to_hot_query_ratio"],
            400.0,
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])

        profiled = [row for row in payload["rows"] if row["prepared_session_residency_profiled"]]
        self.assertEqual(len(profiled), 4)
        for row in profiled:
            profile = row["prepared_session_residency_profile"]
            self.assertEqual(profile["scale_profile_row_id"], row["row_id"])
            self.assertFalse(profile["automatic_partner_selection_authorized"])
            self.assertFalse(profile["true_zero_copy_claim_authorized"])

    def test_selected_profiled_row_gets_profile_payload(self) -> None:
        payload = self._dry_run("rtnn")
        self.assertEqual(payload["selected_prepared_session_residency_profile_count"], 1)
        self.assertEqual(len(payload["rows"]), 1)
        row = payload["rows"][0]
        self.assertTrue(row["prepared_session_residency_profiled"])
        profile = row["prepared_session_residency_profile"]
        self.assertEqual(profile["app"], "rtnn")
        self.assertEqual(profile["primitive"], "fixed_radius_neighbors_3d_ranked_summary")
        self.assertGreater(profile["timing"]["prepare_to_hot_query_ratio"], 12_000.0)

    def test_selected_unprofiled_row_records_false_not_missing(self) -> None:
        payload = self._dry_run("raydb_style")
        self.assertEqual(payload["selected_prepared_session_residency_profile_count"], 0)
        self.assertEqual(len(payload["rows"]), 1)
        row = payload["rows"][0]
        self.assertFalse(row["prepared_session_residency_profiled"])
        self.assertIsNone(row["prepared_session_residency_profile"])

    def test_report_documents_metadata_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3876",
            "metadata integration only",
            "prepared_session_residency_profile",
            "prepared_session_residency_summary",
            "automatic partner/backend selection",
            "not a hidden cache",
            "A5000 Evidence",
            "selected_prepared_session_residency_profile_count",
        ):
            self.assertIn(phrase, text)

    def test_a5000_artifact_carries_profiles_without_claim_leaks(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["json_pass_count"], 10)
        self.assertEqual(payload["selected_prepared_session_residency_profile_count"], 4)
        self.assertEqual(payload["prepared_session_residency_validation"]["status"], "accept")
        self.assertGreater(
            payload["prepared_session_residency_summary"]["geomean_prepare_to_hot_query_ratio"],
            400.0,
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])

        profiled = [row for row in payload["rows"] if row["prepared_session_residency_profiled"]]
        self.assertEqual(len(profiled), 4)
        for row in profiled:
            profile = row["prepared_session_residency_profile"]
            self.assertEqual(profile["scale_profile_row_id"], row["row_id"])
            self.assertFalse(profile["automatic_partner_selection_authorized"])
            self.assertFalse(profile["true_zero_copy_claim_authorized"])
            self.assertFalse(profile["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
