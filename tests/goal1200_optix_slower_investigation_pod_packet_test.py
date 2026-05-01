from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1200_optix_slower_investigation_pod_packet as goal1200


ROOT = Path(__file__).resolve().parents[1]


class Goal1200OptixSlowerInvestigationPodPacketTest(unittest.TestCase):
    def test_packet_builds_archive_and_replay_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = goal1200.build_packet(Path(tmp) / "source.tar.gz")
        self.assertTrue(payload["valid"])
        self.assertIn("EXPECTED_SHA256=" + payload["archive"]["archive_sha256"], payload["commands"]["run_on_pod"])
        self.assertEqual(
            payload["pod_batch"]["target_rows"],
            [
                "database_analytics",
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            ],
        )
        self.assertEqual(payload["pod_batch"]["positive_controls"], ["road_hazard_screening"])
        self.assertEqual(payload["pod_batch"]["same_scale_repairs"], ["hausdorff_distance"])
        self.assertIn("does not run cloud", payload["boundary"])

    def test_executor_preserves_failures_and_packages_results(self) -> None:
        text = (ROOT / "scripts/goal1200_optix_slower_investigation_pod_executor.sh").read_text(encoding="utf-8")
        self.assertIn("libgeos-dev", text)
        self.assertIn("libembree-dev", text)
        self.assertIn("cuda-nvcc-13-0", text)
        self.assertIn("run_step()", text)
        self.assertIn(".status.json", text)
        self.assertIn("make_build_optix.status.json", text)
        self.assertIn("Goal1200 build failed; partial result package created.", text)
        self.assertIn("goal1200_status_summary.json", text)
        self.assertIn("tar -czf", text)
        self.assertIn("does not authorize public", text)

    def test_cli_writes_packet_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_json = tmp_path / "packet.json"
            output_md = tmp_path / "packet.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1200_optix_slower_investigation_pod_packet.py",
                    "--archive",
                    str(tmp_path / "source.tar.gz"),
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
            self.assertIn("Goal1200 OptiX Slower-App Investigation Pod Packet", markdown)
            self.assertIn("Copy Back", markdown)


if __name__ == "__main__":
    unittest.main()
