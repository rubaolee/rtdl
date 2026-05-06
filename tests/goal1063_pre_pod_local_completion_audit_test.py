from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1063PrePodLocalCompletionAuditTest(unittest.TestCase):
    def test_audit_separates_pod_ready_blocked_rows_from_local_only_rows(self) -> None:
        module = __import__(
            "scripts.goal1063_pre_pod_local_completion_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"])
        self.assertFalse(payload["pod_ready_now"])
        self.assertEqual(payload["summary"]["reviewed_public_wording_apps"], 13)
        self.assertEqual(payload["blocked_apps"], ["graph_analytics"])
        self.assertEqual(payload["not_reviewed_apps"], ["database_analytics", "polygon_set_jaccard"])
        self.assertEqual(payload["summary"]["blocked_rows_ready_for_one_pod"], 0)
        self.assertEqual(payload["summary"]["rejected_current_speedup_rows"], 4)
        self.assertEqual(payload["summary"]["local_only_blockers_before_broader_pod"], 4)
        self.assertIn("stale Goal1062 pod manifest", payload["pod_ready_scope"])

    def test_rejected_rows_are_not_marked_pod_ready_without_local_changes(self) -> None:
        module = __import__(
            "scripts.goal1063_pre_pod_local_completion_audit",
            fromlist=["build_audit"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_audit()["rejected_rows_requiring_local_work"]
        }
        self.assertIn(("database_analytics", "prepared_db_session_sales_risk"), rows)
        self.assertIn(("graph_analytics", "graph_visibility_edges_gate"), rows)
        self.assertIn(("polygon_set_jaccard", "polygon_set_jaccard_optix_native_assisted_phase_gate"), rows)
        for row in rows.values():
            self.assertTrue(row["pod_policy"].startswith("no_pod_until"))
            self.assertTrue(row["local_next"].strip())

    def test_cli_writes_reproducible_audit_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "audit.json"
            output_md = Path(tmpdir) / "audit.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1063_pre_pod_local_completion_audit.py",
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
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1063 Pre-Pod Local Completion Audit", markdown)
            self.assertIn("no_pod_until_code_or_scale_changes", markdown)
            self.assertIn("stale Goal1062 pod manifest", markdown)


if __name__ == "__main__":
    unittest.main()
