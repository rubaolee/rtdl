from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1179_public_docs_goal1177_boundary_audit as goal1179


ROOT = Path(__file__).resolve().parents[1]


class Goal1179PublicDocsGoal1177BoundaryAuditTest(unittest.TestCase):
    def test_public_docs_preserve_goal1177_boundary(self) -> None:
        payload = goal1179.build_audit()
        self.assertTrue(payload["valid"], payload["rows"])
        self.assertEqual(payload["failing_doc_count"], 0)
        self.assertEqual(payload["public_wording_row_count_expected"], 11)
        by_path = {row["path"]: row for row in payload["rows"]}
        self.assertEqual(by_path["README.md"]["status"], "ok")
        self.assertEqual(by_path["docs/quick_tutorial.md"]["status"], "ok")
        self.assertEqual(by_path["docs/v1_0_rtx_app_status.md"]["status"], "ok")

    def test_combined_docs_do_not_promote_goal1177_public_speedup(self) -> None:
        payload = goal1179.build_audit()
        combined = "\n".join(
            (ROOT / row["path"]).read_text(encoding="utf-8")
            for row in payload["rows"]
            if (ROOT / row["path"]).exists()
        )
        self.assertIn("Goal1177", combined)
        self.assertIn("external-review input only", combined)
        self.assertIn("does not add a new reviewed public wording row", combined)
        self.assertNotIn("Goal1177 authorizes public", combined)
        self.assertNotIn("Goal1177 public speedup", combined)
        self.assertIn("reviewed public RTX sub-path wording rows: `11`", combined)
        self.assertIn("Goal1208 adds exactly one reviewed public wording row", combined)

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "audit.json"
            output_md = Path(tmp) / "audit.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1179_public_docs_goal1177_boundary_audit.py",
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
            self.assertIn("Goal1179 Public Docs Goal1177 Boundary Audit", markdown)
            self.assertIn("expected reviewed public wording rows: `11`", markdown)


if __name__ == "__main__":
    unittest.main()
