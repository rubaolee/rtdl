from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1020PublicDocsRtxBoundaryAuditTest(unittest.TestCase):
    def test_public_docs_preserve_rtx_boundary_wording(self) -> None:
        module = __import__(
            "scripts.goal1020_public_docs_rtx_boundary_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"], payload["rows"])
        self.assertEqual(payload["doc_count"], 7)
        self.assertEqual(payload["failing_doc_count"], 0)
        self.assertEqual(payload["current_public_wording_source"], "rtdsl.rtx_public_wording_matrix()")
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        by_path = {row["path"]: row for row in payload["rows"]}
        self.assertEqual(by_path["docs/release_facing_examples.md"]["status"], "ok")
        self.assertEqual(by_path["docs/application_catalog.md"]["status"], "ok")
        self.assertEqual(by_path["docs/rtdl_feature_guide.md"]["status"], "ok")

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1020.json"
            output_md = Path(tmpdir) / "goal1020.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1020_public_docs_rtx_boundary_audit.py",
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
            self.assertIn("Goal1020 Public Docs RTX Boundary Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("public speedup claims authorized here: `0`", markdown)
            self.assertIn("rtdsl.rtx_public_wording_matrix()", markdown)


if __name__ == "__main__":
    unittest.main()
