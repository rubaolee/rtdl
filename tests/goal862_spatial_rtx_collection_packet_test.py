from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal862SpatialRtxCollectionPacketTest(unittest.TestCase):
    def test_packet_contains_only_spatial_apps(self) -> None:
        module = __import__("scripts.goal862_spatial_rtx_collection_packet", fromlist=["build_packet"])
        payload = module.build_packet()
        self.assertEqual(payload["row_count"], 2)
        apps = {row["app"] for row in payload["rows"]}
        self.assertEqual(apps, {"service_coverage_gaps", "event_hotspot_screening"})

    def test_packet_carries_rtx_commands_and_valid_required_baselines(self) -> None:
        module = __import__("scripts.goal862_spatial_rtx_collection_packet", fromlist=["build_packet"])
        rows = {row["app"]: row for row in module.build_packet()["rows"]}
        for app in ("service_coverage_gaps", "event_hotspot_screening"):
            with self.subTest(app=app):
                self.assertEqual(rows[app]["gate_status"], "ready_for_review")
                self.assertEqual(len(rows[app]["required_local_baselines"]), 2)
                self.assertTrue(all(item["status"] == "valid" for item in rows[app]["required_local_baselines"]))
                self.assertIn("goal811_", rows[app]["rtx_output_json"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "packet.json"
            output_md = Path(tmpdir) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal862_spatial_rtx_collection_packet.py",
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
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            output_md_exists = output_md.exists()

        self.assertIn("Goal862 Spatial RTX Collection Packet", completed.stdout)
        self.assertEqual(payload["row_count"], 2)
        self.assertTrue(output_md_exists)


if __name__ == "__main__":
    unittest.main()
