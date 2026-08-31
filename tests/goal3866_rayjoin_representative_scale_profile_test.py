from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3866_rayjoin_representative_scale_profile.py"
REPORT = ROOT / "docs" / "reports" / "goal3866_rayjoin_representative_scale_profile_2026-06-08.md"
A5000_ARTIFACT = (
    ROOT / "docs" / "reports" / "goal3866_rayjoin_representative_scale_profile_a5000" / "summary.json"
)


class Goal3866RayJoinRepresentativeScaleProfileTest(unittest.TestCase):
    def test_runner_dry_run_emits_parseable_json_without_stdout_progress(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dry-run",
                "--data-dir",
                "does-not-need-to-exist-for-dry-run",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["schema"], "rtdl.goal3866.rayjoin_representative_scale_profile.v1")
        self.assertTrue(payload["dry_run"])
        self.assertIn("PIP one-shot", " ".join(payload["planned_cases"]))
        self.assertNotIn("[goal", completed.stderr)

    def test_current_scale_registry_uses_representative_rayjoin_route(self) -> None:
        row = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "spatial_rayjoin")
        self.assertEqual(
            row["row_id"],
            "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default",
        )
        self.assertIn("scripts/goal3866_rayjoin_representative_scale_profile.py", row["command"])
        self.assertIn("Goal3866", row["evidence_refs"])
        self.assertIn("Goal3834", row["evidence_refs"])
        self.assertIn("Goal3838", row["evidence_refs"])
        self.assertIn("Goal3842", row["evidence_refs"])
        self.assertTrue(row["requires_numba"])
        self.assertEqual(row["expected_runtime_class"], "representative_mixed_route_public_cdb")
        self.assertNotIn("spatial_rayjoin_pip_count_scale_default_prepared_optix", row["row_id"])
        self.assertFalse(row["automatic_partner_selection_authorized"])

    def test_report_and_a5000_artifact_record_boundaries_when_present(self) -> None:
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3866", text)
        self.assertIn("representative mixed route", text)
        self.assertIn("does not authorize", text)
        if A5000_ARTIFACT.exists():
            payload = json.loads(A5000_ARTIFACT.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "rtdl.goal3866.rayjoin_representative_scale_profile.v1")
            self.assertFalse(payload["dry_run"])
            self.assertTrue(payload["all_counts_match"])
            self.assertTrue(payload["numba_reference_available_for_custom_logic"])
            self.assertFalse(payload["cupy_required_for_reference_route"])
            self.assertFalse(payload["claim_boundary"]["automatic_partner_selection_authorized"])
            self.assertFalse(payload["claim_boundary"]["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
