from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1163PreCloudRtxReadinessSupersessionTest(unittest.TestCase):
    def test_payload_supersedes_goal1125_without_authorizing_public_wording(self) -> None:
        module = __import__("scripts.goal1163_pre_cloud_rtx_readiness_supersession", fromlist=["build_payload"])
        payload = module.build_payload()
        self.assertTrue(payload["valid"])
        self.assertIn("goal1125", payload["supersedes"])
        self.assertEqual(payload["summary"]["tracked_apps"], 6)
        self.assertEqual(payload["summary"]["local_pre_cloud_complete_next_pod_batch"], 6)
        self.assertEqual(payload["summary"]["public_wording_authorized"], 0)
        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(rows["database_analytics"]["local_remedy_goals"], ("Goal1155", "Goal1156", "Goal1157"))
        self.assertEqual(rows["graph_analytics"]["local_remedy_goals"], ("Goal1158", "Goal1159"))
        self.assertEqual(rows["road_hazard_screening"]["local_remedy_goals"], ("Goal1160",))
        self.assertEqual(rows["hausdorff_distance"]["local_remedy_goals"], ("Goal1161",))
        self.assertEqual(rows["polygon_pair_overlap_area_rows"]["local_remedy_goals"], ("Goal1162",))
        self.assertEqual(rows["polygon_set_jaccard"]["local_remedy_goals"], ("Goal1162",))
        self.assertTrue(
            all(row["public_wording_status"] == "blocked_until_real_rtx_artifact_and_review" for row in rows.values())
        )

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "status.json"
            output_md = Path(tmpdir) / "status.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1163_pre_cloud_rtx_readiness_supersession.py",
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
            self.assertEqual(payload["schema_version"], "goal1163_pre_cloud_rtx_readiness_supersession_v1")
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1163 Pre-Cloud RTX Readiness Supersession", markdown)
            self.assertIn("database_analytics", markdown)
            self.assertIn("polygon_set_jaccard", markdown)


if __name__ == "__main__":
    unittest.main()
