from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1125UnresolvedRtxPublicWordingPrioritizationTest(unittest.TestCase):
    def test_audit_covers_all_unresolved_nvidia_rows(self) -> None:
        module = __import__(
            "scripts.goal1125_unresolved_rtx_public_wording_prioritization",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        by_app = {row["app"]: row for row in payload["rows"]}

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["unresolved_nvidia_public_wording_apps"], 4)
        self.assertEqual(payload["summary"]["public_wording_blocked"], 2)
        self.assertEqual(payload["summary"]["public_wording_not_reviewed"], 2)
        self.assertEqual(set(by_app), {
            "database_analytics",
            "graph_analytics",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        })

    def test_buckets_prevent_wasteful_pod_runs(self) -> None:
        module = __import__(
            "scripts.goal1125_unresolved_rtx_public_wording_prioritization",
            fromlist=["build_audit"],
        )
        by_app = {row["app"]: row for row in module.build_audit()["rows"]}

        for app in (
            "database_analytics",
            "graph_analytics",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            self.assertEqual(by_app[app]["action_bucket"], "local_optimization_first")
            self.assertTrue(by_app[app]["pod_policy"].startswith("no_pod_until"))
            self.assertTrue(by_app[app]["goal1060_rejected_rows"])

    def test_cli_writes_reproducible_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1125.json"
            output_md = Path(tmpdir) / "goal1125.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1125_unresolved_rtx_public_wording_prioritization.py",
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
            self.assertIn("Goal1125 Unresolved RTX Public-Wording Prioritization", markdown)
            self.assertNotIn("robot_collision_screening", markdown)
            self.assertIn("local_optimization_first", markdown)


if __name__ == "__main__":
    unittest.main()
