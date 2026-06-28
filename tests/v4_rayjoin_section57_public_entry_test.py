from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V4RayJoinSection57PublicEntryTest(unittest.TestCase):
    def test_public_entry_describes_section57_surface(self) -> None:
        completed = subprocess.run(
            [sys.executable, "examples/paper_reproduction/rayjoin.py", "--json"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["paper_entry"], "RayJoin")
        self.assertIn("--section57-plan", payload["section57_overlay_plan"])
        self.assertIn("--section57-run", payload["section57_overlay_run"])
        self.assertIn("rayjoin_paper_suite.py", payload["paper_suite"])

    def test_section57_plan_lists_all_eight_overlay_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "section57"
            plan_json = output_dir / "plan.json"
            plan_md = output_dir / "plan.md"
            subprocess.run(
                [
                    sys.executable,
                    "examples/paper_reproduction/rayjoin.py",
                    "--section57-plan",
                    "--dataset-root",
                    str(root / "missing_inputs"),
                    "--output-dir",
                    str(output_dir),
                    "--output-json",
                    str(plan_json),
                    "--output-md",
                    str(plan_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(plan_json.read_text(encoding="utf-8"))
            markdown = plan_md.read_text(encoding="utf-8")

        self.assertEqual(payload["coverage"]["overlay_pairs_total"], 8)
        self.assertEqual(payload["coverage"]["overlay_pairs_blocked"], 8)
        self.assertIn("RayJoin Section 5.7 Overlay 8/8 Execution Plan", markdown)
        self.assertIn("County x Zipcode", markdown)

    def test_section57_dry_run_records_commands_without_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "section57"
            run_json = output_dir / "run.json"
            summary_json = output_dir / "summary.json"
            summary_md = output_dir / "summary.md"
            subprocess.run(
                [
                    sys.executable,
                    "examples/paper_reproduction/rayjoin.py",
                    "--section57-run",
                    "--dry-run",
                    "--allow-missing-inputs",
                    "--dataset-root",
                    str(root / "missing_inputs"),
                    "--output-dir",
                    str(output_dir),
                    "--query-exec",
                    "/workspace/RayJoin_fresh/release/bin/query_exec",
                    "--polyover-exec",
                    "/workspace/RayJoin_fresh/release/bin/polyover_exec",
                    "--run-json",
                    str(run_json),
                    "--summary-json",
                    str(summary_json),
                    "--summary-md",
                    str(summary_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            )
            run_payload = json.loads(run_json.read_text(encoding="utf-8"))
            summary_payload = json.loads(summary_json.read_text(encoding="utf-8"))

        self.assertEqual(run_payload["schema"], "rtdl.rayjoin.section57_overlay_matrix.run.v1")
        self.assertTrue(any(row["status"] == "dry_run" for row in run_payload["attempts"]))
        self.assertEqual(summary_payload["coverage"]["overlay_pairs_total"], 8)
        self.assertEqual(summary_payload["coverage"]["overlay_pairs_complete"], 0)

    def test_v214_comparison_protocol_is_same_contract(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "examples/paper_reproduction/rayjoin.py",
                "--section57-compare-v214",
                "--pairs",
                "county_zipcode",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["comparison"], "RayJoin Section 5.7 polygon overlay")
        self.assertEqual(payload["pairs"], "county_zipcode")
        self.assertIn("same dataset root", payload["important_boundary"])
        self.assertIn("--overlay-pairs", payload["v2_14_plan_command"])
        self.assertIn("--section57-run", payload["v4_0_command"])


if __name__ == "__main__":
    unittest.main()
