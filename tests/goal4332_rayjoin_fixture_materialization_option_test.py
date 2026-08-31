from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.goal3828_current_benchmark_scale_profile_runner import (
    RAYJOIN_PUBLIC_CDB_REQUIRED_FILES,
    _configure_rayjoin_public_cdb,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3828_current_benchmark_scale_profile_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal4332_rayjoin_public_cdb_fixture_runner_option_2026-06-11.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4329_current_pod_validation"
    / "goal4332_runner_option"
    / "rayjoin_materialized_summary.json"
)
BUNDLE_POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4329_current_pod_validation"
    / "goal4332_bundle_pass_through_validation_fixed"
    / "bundle_summary.json"
)


class Goal4332RayJoinFixtureMaterializationOptionTest(unittest.TestCase):
    def test_dry_run_materialization_option_records_planned_fixture_without_download(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "dry_run.json"
            data_dir = Path(tmp) / "rayjoin_public_cdb"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--dry-run",
                    "--only",
                    "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default",
                    "--materialize-rayjoin-public-cdb",
                    "--rayjoin-public-cdb-dir",
                    str(data_dir),
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("rayjoin_public_cdb_fixture", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))

        fixture = payload["rayjoin_public_cdb_fixture"]
        self.assertEqual(fixture["status"], "dry_run_planned")
        self.assertFalse(fixture["download_attempted"])
        self.assertFalse(fixture["materialize_attempted"])
        self.assertTrue(fixture["needed_by_selected_rows"])
        self.assertFalse(fixture["release_authorized"])
        self.assertFalse(fixture["public_speedup_claim_authorized"])
        self.assertEqual(len(payload["rows"]), 1)

    def test_existing_fixture_is_detected_and_env_is_set(self) -> None:
        old_env = os.environ.get("RTDL_RAYJOIN_PUBLIC_CDB_DIR")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                data_dir = Path(tmp)
                for name in RAYJOIN_PUBLIC_CDB_REQUIRED_FILES:
                    (data_dir / name).write_bytes(b"fixture")
                payload = _configure_rayjoin_public_cdb(
                    [{"row_id": "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default"}],
                    data_dir=data_dir,
                    materialize=False,
                    dry_run=False,
                )
                self.assertEqual(payload["status"], "provided")
                self.assertTrue(payload["state"]["all_required_files_present"])
                self.assertTrue(payload["env_var_set"])
                self.assertEqual(os.environ["RTDL_RAYJOIN_PUBLIC_CDB_DIR"], str(data_dir.resolve()))
        finally:
            if old_env is None:
                os.environ.pop("RTDL_RAYJOIN_PUBLIC_CDB_DIR", None)
            else:
                os.environ["RTDL_RAYJOIN_PUBLIC_CDB_DIR"] = old_env

    def test_non_rayjoin_selection_reports_not_needed(self) -> None:
        payload = _configure_rayjoin_public_cdb(
            [{"row_id": "hausdorff_xhd_scale_default_optix_threshold"}],
            data_dir=None,
            materialize=False,
            dry_run=False,
        )
        self.assertEqual(payload["status"], "not_needed")
        self.assertFalse(payload["needed_by_selected_rows"])
        self.assertFalse(payload["release_authorized"])

    def test_report_documents_explicit_not_hidden_download_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("--materialize-rayjoin-public-cdb", text)
        self.assertIn("not to hide a download behind normal execution", text)
        self.assertIn("benchmark-runner orchestration only", text)
        self.assertIn("RTX pod validation", text)
        self.assertIn("pod-validation bundle pass-through", text)
        self.assertIn("one-command SSH pod sessions", text)
        self.assertIn("does not authorize release action", text)

    def test_pod_artifact_validates_explicit_materialization_path(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertIs(payload["all_pass"], True)
        self.assertEqual(payload["json_pass_count"], 1)
        fixture = payload["rayjoin_public_cdb_fixture"]
        self.assertEqual(fixture["status"], "materialized")
        self.assertTrue(fixture["state_after"]["all_required_files_present"])
        self.assertFalse(fixture["release_authorized"])
        self.assertFalse(fixture["public_speedup_claim_authorized"])

    def test_pod_bundle_pass_through_checks_file_backed_scale_profile_artifact(self) -> None:
        payload = json.loads(BUNDLE_POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual("pass", payload["status"])
        self.assertTrue(payload["rayjoin_public_cdb_fixture_request"]["materialize_requested"])
        self.assertFalse(payload["rayjoin_public_cdb_fixture_request"]["download_hidden_by_bundle"])
        step = next(item for item in payload["steps"] if item["name"] == "scale_profile_hardware_run")
        self.assertEqual("pass", step["status"])
        self.assertEqual("artifact", step["json_source"])
        self.assertTrue(step["json_parseable"])
        self.assertFalse(step["stdout_json_parseable"])
        self.assertEqual([], step["claim_flag_violations"])


if __name__ == "__main__":
    unittest.main()
