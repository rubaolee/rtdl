import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1135ChangedPathRtxPodPlanTest(unittest.TestCase):
    def test_plan_contains_one_changed_path_entry_per_tracked_app_group(self) -> None:
        from scripts import goal1135_changed_path_rtx_pod_plan as plan

        payload = plan.build_plan()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["entry_count"], 6)
        labels = {entry["label"] for entry in payload["entries"]}
        self.assertIn("database_analytics_compact_summary", labels)
        self.assertIn("graph_visibility_edges_gate", labels)
        self.assertIn("road_hazard_native_summary_count", labels)
        self.assertIn("polygon_pair_overlap_phase_gate", labels)
        self.assertIn("polygon_set_jaccard_phase_gate", labels)
        self.assertIn("hausdorff_threshold_phase_gate", labels)
        self.assertIn("Do not start/stop cloud per app", payload["cloud_policy"])
        self.assertIn("does not authorize public", payload["non_claim"])

    def test_commands_write_under_report_dir_and_use_existing_scripts(self) -> None:
        from scripts import goal1135_changed_path_rtx_pod_plan as plan

        payload = plan.build_plan(report_dir="docs/reports/test_goal1135")
        for entry in payload["entries"]:
            command = entry["command"]
            self.assertEqual(command[0], "python3")
            self.assertTrue((ROOT / command[1]).exists(), command[1])
            self.assertIn("--output-json", command)
            self.assertTrue(command[-1].startswith("docs/reports/test_goal1135/"))

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            output_json = Path(tmpdir) / "plan.json"
            output_md = Path(tmpdir) / "plan.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1135_changed_path_rtx_pod_plan.py",
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
            self.assertEqual(payload["entry_count"], 6)
            self.assertIn("Goal1135 Changed-Path RTX Pod Plan", markdown)


if __name__ == "__main__":
    unittest.main()
