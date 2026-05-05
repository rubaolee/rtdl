from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1267_v1_2_optix_targeted_pod_packet as goal1267


ROOT = Path(__file__).resolve().parents[1]
EXECUTOR = ROOT / "scripts" / "goal1267_v1_2_optix_targeted_pod_executor.sh"


class Goal1267V12OptixTargetedPodPacketTest(unittest.TestCase):
    def test_packet_tracks_current_v1_2_plan_and_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = goal1267.build_packet(Path(tmp) / "source.tar.gz")
        self.assertTrue(payload["valid"])
        self.assertIn("EXPECTED_SHA256=" + payload["archive"]["archive_sha256"], payload["commands"]["run_on_pod"])
        self.assertEqual(
            payload["pod_batch"]["target_rows"],
            [
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "database_analytics",
                "polygon_set_jaccard",
            ],
        )
        self.assertEqual(payload["pod_batch"]["active_backends"], ["embree", "optix"])
        self.assertEqual(payload["pod_batch"]["frozen_backends"], ["vulkan", "hiprt", "apple_rt"])
        self.assertEqual(
            payload["pod_batch"]["plan_source"],
            "docs/reports/goal1266_v1_2_optix_plan_after_v1_1_findings_2026-05-05.md",
        )
        self.assertIn("execution-only", payload["boundary"])
        self.assertIn("does not authorize public wording", payload["boundary"])
        self.assertIn("speedup claims", payload["boundary"])

    def test_packet_records_required_phase_fields(self) -> None:
        targets = {target["row"]: target for target in goal1267.TARGETS}
        self.assertIn("ray_pack_mode", targets["graph_analytics"]["required_fields"])
        self.assertIn("blocker_pack_mode", targets["graph_analytics"]["required_fields"])
        self.assertIn("ray_pack_sec", targets["graph_analytics"]["required_fields"])
        self.assertEqual(targets["graph_analytics"]["expected_metadata"]["ray_pack_mode"], "numpy_packed_rays")
        self.assertEqual(targets["graph_analytics"]["expected_metadata"]["blocker_pack_mode"], "numpy_packed_triangles")
        self.assertIn(
            "candidate_count_matches_expected",
            targets["polygon_pair_overlap_area_rows"]["required_fields"],
        )
        self.assertIn("warm_query_median_seconds", targets["database_analytics"]["required_fields"])
        self.assertIn("chunk_copies", targets["polygon_set_jaccard"]["required_fields"])

    def test_executor_uses_current_scales_and_not_stale_db_all_scenario(self) -> None:
        text = EXECUTOR.read_text(encoding="utf-8")
        self.assertIn("libgeos-dev", text)
        self.assertIn("libembree-dev", text)
        self.assertIn("cuda-nvcc-13-0", text)
        self.assertIn("run_step()", text)
        self.assertIn(".status.json", text)
        self.assertIn("goal1267_status_summary.json", text)
        self.assertIn("tar -czf", text)
        self.assertIn("--scenario sales_risk --copies ${copies}", text)
        self.assertIn("for copies in 100000 300000", text)
        self.assertNotIn("--scenario all --copies 300000", text)
        self.assertIn("for copies in 30000 60000", text)
        self.assertIn("for copies in 40000 80000 160000", text)
        self.assertIn("for copies in 4096 8192", text)
        self.assertIn("--chunk-copies 1024", text)
        self.assertIn("goal1267_graph_ray_pack_metadata.json", text)
        self.assertIn("all_numpy_packed_rays", text)
        self.assertIn("all_numpy_packed_triangles", text)
        self.assertIn("ray_pack_mode", text)
        self.assertIn("blocker_pack_mode", text)
        self.assertIn("no public wording", text)

    def test_cli_writes_packet_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_json = tmp_path / "packet.json"
            output_md = tmp_path / "packet.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1267_v1_2_optix_targeted_pod_packet.py",
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
            self.assertIn("Goal1267 v1.2 Targeted OptiX Pod Packet", markdown)
            self.assertIn("Run On Pod", markdown)
            self.assertIn("Copy Back", markdown)


if __name__ == "__main__":
    unittest.main()
