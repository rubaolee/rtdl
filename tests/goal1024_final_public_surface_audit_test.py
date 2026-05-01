from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1024FinalPublicSurfaceAuditTest(unittest.TestCase):
    def test_public_surface_is_aligned_after_history_repair(self) -> None:
        module = __import__(
            "scripts.goal1024_final_public_surface_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["missing_file_count"], 0)
        self.assertEqual(payload["failing_phrase_doc_count"], 0)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        checks = {row["name"]: row for row in payload["recorded_checks"]}
        self.assertEqual(checks["full_unittest_discovery"]["tests"], 1969)
        self.assertEqual(checks["full_unittest_discovery"]["skipped"], 196)
        self.assertEqual(checks["focused_public_surface_suite"]["tests"], 20)
        self.assertEqual(checks["history_repair_suite"]["tests"], 7)

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1024.json"
            output_md = Path(tmpdir) / "goal1024.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1024_final_public_surface_audit.py",
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
            self.assertIn("Goal1024 Final Public Surface Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("public speedup claims authorized here: `0`", markdown)
            self.assertIn("Goal1023", markdown)


if __name__ == "__main__":
    unittest.main()
