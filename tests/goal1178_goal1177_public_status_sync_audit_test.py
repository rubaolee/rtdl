from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1178_goal1177_public_status_sync_audit as goal1178


ROOT = Path(__file__).resolve().parents[1]


class Goal1178Goal1177PublicStatusSyncAuditTest(unittest.TestCase):
    def test_audit_passes_current_docs(self) -> None:
        payload = goal1178.build_audit()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["failing_doc_count"], 0)
        paths = {row["path"] for row in payload["rows"]}
        self.assertIn("docs/v1_0_rtx_app_status.md", paths)
        self.assertIn("docs/app_engine_support_matrix.md", paths)

    def test_audit_enforces_no_goal1177_public_wording_promotion(self) -> None:
        payload = goal1178.build_audit()
        checked_text = "\n".join(
            (ROOT / row["path"]).read_text(encoding="utf-8")
            for row in payload["rows"]
            if (ROOT / row["path"]).exists()
        )
        self.assertIn("Goal1177", checked_text)
        self.assertIn("external-review input only", checked_text)
        self.assertNotIn("Goal1177 authorizes public", checked_text)
        self.assertNotIn("Goal1177 public speedup", checked_text)

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "audit.json"
            output_md = Path(tmp) / "audit.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1178_goal1177_public_status_sync_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1178 Goal1177 Public RTX Status Sync Audit", markdown)
            self.assertIn("external-review input only", markdown)


if __name__ == "__main__":
    unittest.main()
