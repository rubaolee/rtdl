from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1249_v1_0_release_candidate_audit as goal1249


ROOT = Path(__file__).resolve().parents[1]


class Goal1249V10ReleaseCandidateAuditTest(unittest.TestCase):
    def test_v1_0_release_candidate_audit_is_valid(self) -> None:
        payload = goal1249.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["recommendation"], "v1_0_release_action_complete")
        self.assertFalse(payload["pod_needed_now"])
        self.assertEqual(payload["release_marker"], "v1.5")
        self.assertTrue(payload["package_ok"])
        self.assertTrue(payload["support_ok"])
        self.assertTrue(payload["docs_index_ok"])
        self.assertTrue(payload["reports_ok"])

    def test_reviewed_phase_names_match_source_of_truth(self) -> None:
        payload = goal1249.build_audit()
        state = payload["support_state"]
        self.assertEqual(state["support_reviewed_count"], 12)
        self.assertEqual(state["status_reviewed_count"], 12)
        self.assertTrue(state["support_matches_expected"])
        self.assertTrue(state["status_matches_expected"])
        self.assertEqual(state["support_reviewed_phases"], state["status_reviewed_phases"])
        self.assertIn(
            "facility_knn_assignment / coverage_threshold_prepared_recentered",
            state["support_reviewed_phases"],
        )
        self.assertNotIn("facility_knn_assignment / prepared_query_knn", state["support_reviewed_phases"])

    def test_package_is_released_without_new_speedup_authorization(self) -> None:
        payload = goal1249.build_audit()
        for row in payload["package_rows"]:
            with self.subTest(path=row["path"]):
                self.assertEqual(row["status"], "ok")
                self.assertFalse(row["missing_required_phrases"])
                self.assertFalse(row["forbidden_phrases"])
        self.assertIn("released v1.0", payload["boundary"])
        self.assertIn("No pod is required", payload["pod_decision"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1249.json"
            output_md = Path(tmpdir) / "goal1249.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1249_v1_0_release_candidate_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("Goal1249 v1.0 Release Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("support matrix reviewed rows: `12`", markdown)
            self.assertIn("release marker: `v1.5`", markdown)


if __name__ == "__main__":
    unittest.main()
