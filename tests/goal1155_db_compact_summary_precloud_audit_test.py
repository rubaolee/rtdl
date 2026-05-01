from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1155DbCompactSummaryPrecloudAuditTest(unittest.TestCase):
    def test_build_audit_identifies_db_precloud_work(self) -> None:
        from scripts import goal1155_db_compact_summary_precloud_audit as goal1155

        payload = goal1155.build_audit()
        self.assertTrue(payload["valid"], payload["blockers"])
        self.assertEqual(payload["app"], "database_analytics")
        self.assertEqual(payload["cloud_policy"], "no_pod_until_code_or_contract_changes")
        self.assertTrue(payload["source_observations"]["optix_grouped_summary_uses_grouped_row_api"])
        self.assertTrue(payload["source_observations"]["regional_dashboard_runs_three_compact_native_ops"])
        self.assertIn("generic prepared DB compact-summary batch primitive", " ".join(payload["conclusions"]))

    def test_profile_json_is_summarized(self) -> None:
        from scripts import goal1155_db_compact_summary_precloud_audit as goal1155

        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "scenario": "all",
                        "copies": 1000,
                        "iterations": 3,
                        "output_mode": "compact_summary",
                        "results": [
                            {
                                "backend": "embree",
                                "status": "ok",
                                "db_review_observation": {"status": "needs_native_counter_artifact"},
                                "prepared_session_warm_query_sec": {"median_sec": 0.006},
                                "reported_run_phase_totals_sec": {
                                    "row_materializing_operation_count": 0,
                                    "compact_summary_operation_count": 6,
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = goal1155.build_audit(profile)
            self.assertTrue(payload["valid"], payload["blockers"])
            self.assertTrue(payload["local_profile_observations"]["included"])
            self.assertEqual(
                payload["local_profile_observations"]["rows"]["embree"]["compact_summary_operation_count"],
                6,
            )

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "audit.json"
            output_md = Path(tmp) / "audit.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1155_db_compact_summary_precloud_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1155 DB Compact-Summary Pre-Cloud Audit", markdown)
            self.assertIn("no_pod_until_code_or_contract_changes", markdown)


if __name__ == "__main__":
    unittest.main()
