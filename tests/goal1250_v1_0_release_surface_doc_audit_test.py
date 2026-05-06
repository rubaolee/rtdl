from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1250_v1_0_release_surface_doc_audit as goal1250


ROOT = Path(__file__).resolve().parents[1]


class Goal1250V10ReleaseSurfaceDocAuditTest(unittest.TestCase):
    def test_release_surface_doc_audit_is_valid(self) -> None:
        payload = goal1250.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(
            payload["recommendation"],
            "v1_0_release_surface_preserved_under_v1_5_current_release",
        )
        self.assertEqual(payload["version"], "v1.5")
        self.assertTrue(payload["version_ok"])
        self.assertFalse(payload["pod_needed_now"])
        self.assertGreaterEqual(payload["surface_count"], 18)
        self.assertEqual(payload["failure_count"], 0)

    def test_all_release_surface_rows_are_clean(self) -> None:
        payload = goal1250.build_audit()
        rows = {row["path"]: row for row in payload["rows"]}
        for required_path in (
            "README.md",
            "docs/quick_tutorial.md",
            "docs/app_example_quickstart.md",
            "docs/current_architecture.md",
            "docs/rtdl/ir_and_lowering.md",
            "docs/performance_model.md",
            "docs/v1_0_rtx_app_status.md",
            "docs/release_reports/v1_0/README.md",
        ):
            self.assertIn(required_path, rows)
        for path, row in rows.items():
            with self.subTest(path=path):
                self.assertEqual(row["status"], "ok")
                self.assertFalse(row["missing_required_phrases"])
                self.assertFalse(row["forbidden_phrases"])

    def test_boundary_and_next_steps_preserve_release_scope(self) -> None:
        payload = goal1250.build_audit()
        self.assertIn("released v1.0", payload["boundary"])
        self.assertIn("No pod is required", payload["pod_decision"])
        self.assertIn("Do not move or retag", " ".join(payload["next_steps"]))

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1250.json"
            output_md = Path(tmpdir) / "goal1250.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1250_v1_0_release_surface_doc_audit.py",
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
            self.assertIn("Goal1250 v1.0 Release-Surface Documentation Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("version: `v1.5`", markdown)
            self.assertIn("failure count: `0`", markdown)


if __name__ == "__main__":
    unittest.main()
