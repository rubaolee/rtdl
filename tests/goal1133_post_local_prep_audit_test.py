import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1133PostLocalPrepAuditTest(unittest.TestCase):
    def test_audit_validates_recent_goal_artifacts_and_boundaries(self) -> None:
        from scripts import goal1133_post_local_prep_audit as audit

        payload = audit.build_audit()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["goal_count"], 5)
        self.assertEqual(payload["summary"]["tracked_app_count"], 6)
        self.assertTrue(payload["summary"]["all_goal_artifacts_present"])
        self.assertTrue(payload["summary"]["ready_for_review"])
        self.assertTrue(payload["summary"]["public_wording_not_promoted"])
        self.assertIn("Do not start/stop pods per app", payload["cloud_policy"])
        self.assertIn("does not run cloud", payload["boundary"])
        by_goal = {row["goal"]: row for row in payload["rows"]}
        self.assertIn("database_analytics", by_goal["Goal1128"]["apps"])
        self.assertIn("polygon_set_jaccard", by_goal["Goal1131"]["apps"])
        self.assertIn("capability/phase evidence", by_goal["Goal1132"]["cloud_next"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            output_json = Path(tmpdir) / "goal1133.json"
            output_md = Path(tmpdir) / "goal1133.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1133_post_local_prep_audit.py",
                    "--output-json",
                    str(output_json.relative_to(ROOT)),
                    "--output-md",
                    str(output_md.relative_to(ROOT)),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1133 Post-Local-Prep RTX App Audit", markdown)
            self.assertIn("Goal1132", markdown)


if __name__ == "__main__":
    unittest.main()
