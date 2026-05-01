from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from examples import rtdl_barnes_hut_force_app as barnes_app
from scripts import goal1106_barnes_hut_chunked_embree_timing_baseline as goal1106


ROOT = Path(__file__).resolve().parents[1]


class _FakePreparedThreshold:
    def __init__(self) -> None:
        self.run_calls: list[int] = []
        self.closed = False

    def run(self, query_points, *, radius: float, threshold: int = 1):
        self.run_calls.append(len(query_points))
        return tuple(
            {"query_id": point.id, "neighbor_count": threshold, "threshold_reached": 1}
            for point in query_points
        )

    def close(self) -> None:
        self.closed = True


class Goal1106BarnesHutChunkedEmbreeTimingBaselineTest(unittest.TestCase):
    def test_streamed_node_points_match_canonical_fixed_depth_nodes(self) -> None:
        body_count = 33
        depth = 3
        canonical_bodies = barnes_app.make_generated_bodies(body_count)
        canonical_nodes = barnes_app.build_fixed_depth_quadtree_cells(canonical_bodies, depth=depth)
        canonical_points = barnes_app._node_points(canonical_nodes)

        streamed_points = goal1106._fixed_depth_node_points_for_generated_bodies(body_count, depth=depth)

        self.assertEqual(len(streamed_points), len(canonical_points))
        self.assertEqual(
            [(point.id, round(point.x, 12), round(point.y, 12)) for point in streamed_points],
            [(point.id, round(point.x, 12), round(point.y, 12)) for point in canonical_points],
        )

    def test_chunked_profile_uses_bounded_query_chunks_and_no_claim_boundary(self) -> None:
        fake = _FakePreparedThreshold()
        with mock.patch.object(
            goal1106.rt,
            "prepare_embree_fixed_radius_count_threshold_2d",
            return_value=fake,
        ):
            payload = goal1106.run_chunked_profile(
                body_count=10,
                chunk_size=4,
                iterations=2,
                radius=10.0,
                barnes_tree_depth=2,
                hit_threshold=3,
            )

        self.assertEqual(fake.run_calls, [4, 4, 2, 4, 4, 2])
        self.assertTrue(fake.closed)
        self.assertEqual(payload["schema_version"], "goal1101_current_contract_non_optix_baseline_v1")
        self.assertEqual(payload["app"], "barnes_hut_force_app")
        self.assertEqual(payload["path_name"], "node_coverage_prepared_rich")
        self.assertEqual(payload["backend"], "embree")
        self.assertEqual(payload["scenario"]["result"]["query_count"], 10)
        self.assertEqual(payload["scenario"]["result"]["barnes_tree_depth"], 2)
        self.assertEqual(payload["scenario"]["result"]["hit_threshold"], 3)
        self.assertIsNone(payload["scenario"]["result"]["matches_oracle"])
        self.assertEqual(payload["parameters"]["chunk_count"], 3)
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_cli_writes_goal1101_compatible_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "chunked.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1106_barnes_hut_chunked_embree_timing_baseline.py",
                    "--body-count",
                    "8",
                    "--chunk-size",
                    "3",
                    "--iterations",
                    "1",
                    "--barnes-tree-depth",
                    "1",
                    "--hit-threshold",
                    "1",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            self.assertIn("barnes_hut_node_coverage", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "goal1101_current_contract_non_optix_baseline_v1")
        self.assertEqual(payload["scenario"]["result"]["query_count"], 8)
        self.assertIsNone(payload["scenario"]["result"]["matches_oracle"])


if __name__ == "__main__":
    unittest.main()
