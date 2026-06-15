from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4383_robot_collision_large_prepared_buffers_2026-06-14.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal4383_robot_collision_large_prepared_buffers_2026-06-14"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal4383RobotCollisionLargePreparedBuffersTest(unittest.TestCase):
    def test_xlarge_rows_use_same_host_prepared_buffer_contract(self) -> None:
        for name in (
            "embree_pose262144_obs8192_link4_r2_no_probe.json",
            "optix_pose262144_obs8192_link4_r2_no_probe.json",
        ):
            payload = _load(name)
            self.assertEqual(payload["contract"], "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1")
            self.assertEqual(payload["case_shape"]["group_count"], 1_048_576)
            self.assertEqual(payload["case_shape"]["segment_count"], 9_437_184)
            self.assertEqual(payload["case_shape"]["static_obstacle_triangle_count"], 16_384)
            self.assertTrue(payload["reuse_metadata"]["host_query_output_buffers_reused"])
            self.assertFalse(payload["reuse_metadata"]["native_query_output_buffers_reused"])
            self.assertFalse(payload["reuse_metadata"]["probe_reference_validated"])
            self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_xlarge_total_and_traversal_speedups_are_recorded(self) -> None:
        embree = _load("embree_pose262144_obs8192_link4_r2_no_probe.json")
        optix = _load("optix_pose262144_obs8192_link4_r2_no_probe.json")

        embree_total = embree["tail_medians"]["total_run_seconds"]
        optix_total = optix["tail_medians"]["total_run_seconds"]
        embree_traversal = embree["tail_medians"]["phase_timing_seconds"]["traversal"]
        optix_traversal = optix["tail_medians"]["phase_timing_seconds"]["traversal"]

        self.assertGreater(embree_total, 1.0)
        self.assertGreater(optix_total, 0.5)
        self.assertGreater(embree_total / optix_total, 1.8)
        self.assertGreater(embree_traversal / optix_traversal, 6.0)

    def test_report_keeps_robot_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("1,048,576 groups and 9,437,184 query segments", text)
        self.assertIn("6.69x faster in traversal", text)
        self.assertIn("not continuous collision detection", text)
        self.assertIn("not robot-planner acceleration", text)
        self.assertIn("not exact solid collision", text)


if __name__ == "__main__":
    unittest.main()
