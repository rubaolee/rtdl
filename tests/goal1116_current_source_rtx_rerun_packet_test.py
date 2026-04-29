from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1116CurrentSourceRtxRerunPacketTest(unittest.TestCase):
    def test_packet_targets_three_engineering_ready_apps(self) -> None:
        module = __import__("scripts.goal1116_current_source_rtx_rerun_packet", fromlist=["build_packet"])
        payload = module.build_packet()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 5)
        self.assertEqual(payload["summary"]["app_count"], 3)
        self.assertEqual(payload["summary"]["validation_row_count"], 3)
        self.assertEqual(payload["summary"]["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_rows_use_current_contracts_not_stale_goal1068_contracts(self) -> None:
        module = __import__("scripts.goal1116_current_source_rtx_rerun_packet", fromlist=["build_packet"])
        rows = module.build_packet()["rows"]
        by_output = {row["output_json"]: row for row in rows}

        facility = by_output[
            "docs/reports/goal1116_current_source_rtx_rerun_packet/"
            "facility_recentered_coverage_threshold_2_5m_optix_validation.json"
        ]
        self.assertIn("facility_service_coverage_recentered", facility["command"])
        self.assertIn("2500000", facility["command"])
        self.assertFalse(facility["contains_skip_validation"])

        barnes_timing = by_output[
            "docs/reports/goal1116_current_source_rtx_rerun_packet/"
            "barnes_hut_depth8_20m_timing.json"
        ]
        self.assertIn("20000000", barnes_timing["command"])
        self.assertIn("0.1", barnes_timing["command"])
        self.assertIn("--barnes-tree-depth", barnes_timing["command"])
        self.assertIn("--skip-validation", barnes_timing["command"])

    def test_robot_large_timing_is_safe_current_source_target(self) -> None:
        module = __import__("scripts.goal1116_current_source_rtx_rerun_packet", fromlist=["build_packet"])
        rows = module.build_packet()["rows"]
        robot_timing = next(row for row in rows if row["output_json"].endswith("robot_prepared_pose_flags_8m_timing.json"))

        self.assertEqual(robot_timing["timing_floor_sec"], 0.100)
        self.assertIn("8000000", robot_timing["command"])
        self.assertIn("packed_arrays", robot_timing["command"])
        self.assertIn("pose_count", robot_timing["command"])
        self.assertTrue(robot_timing["contains_skip_validation"])

    def test_cli_writes_manifest_markdown_and_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "packet.json"
            output_md = Path(tmpdir) / "packet.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1116_current_source_rtx_rerun_packet.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--output-sh",
                    str(output_sh),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["row_count"], 5)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1116 Current-Source RTX Rerun Packet", markdown)
            self.assertIn("barnes_hut_depth8_20m_timing.json", markdown)
            runner = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_SOURCE_COMMIT", runner)
            self.assertIn("goal1116_runner.log", runner)
            self.assertIn("git_head=", runner)
            self.assertIn("utc_start=", runner)
            self.assertIn("utc_end=", runner)
            self.assertIn("nvidia-smi", runner)
            self.assertIn("Goal1116 complete", runner)


if __name__ == "__main__":
    unittest.main()
