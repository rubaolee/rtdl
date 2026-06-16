from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_0_m31_robot_collision_prepared_any_hit_refresh.py"
REPORT = ROOT / "docs/reports/goal4428_v3_0_m31_robot_collision_prepared_any_hit_refresh_2026-06-16.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4428_v3_0_m31_robot_collision_prepared_any_hit_refresh_xlarge_2026-06-16.json"
)


class Goal4428V30M31RobotCollisionPreparedAnyHitRefreshTest(unittest.TestCase):
    def test_runner_dry_run_records_same_host_buffer_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--output",
                    str(output),
                ],
                cwd=str(ROOT),
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "dry_run")
        self.assertTrue(payload["claim_boundary"]["primitive_first_no_partner_needed"])
        self.assertFalse(payload["claim_boundary"]["partner_continuation_required"])
        self.assertFalse(payload["claim_boundary"]["continuous_collision_claim_authorized"])
        planned = {row["backend"]: row for row in payload["planned_rows"]}
        self.assertEqual(set(planned), {"embree", "optix"})
        self.assertEqual(planned["embree"]["pose_count"], 262_144)
        self.assertEqual(planned["optix"]["obstacle_count"], 8_192)
        self.assertTrue(planned["embree"]["reuse_query_buffers"])
        self.assertEqual(planned["embree"]["repeat"], planned["optix"]["repeat"])

    def test_report_and_runner_capture_m31_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1",
            "internal_same_contract_prepared_grouped_segment_any_hit_refresh_not_public_speedup",
            "all_signature_hashes_match_cross_backend",
            "all_host_buffer_reuse_same_contract",
            "continuous_collision_claim_authorized",
        ):
            self.assertIn(phrase, source)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Robot Collision Prepared Any-Hit Refresh",
            "same generic prepared grouped-segment any-hit contract",
            "1,048,576 groups",
            "9,437,184 query segments",
            "does not authorize continuous collision detection",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_same_contract_any_hit_rows(self) -> None:
        self.assertTrue(EVIDENCE_JSON.exists(), f"missing M31 pod evidence: {EVIDENCE_JSON}")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["parameters"]["pose_count"], 262_144)
        self.assertEqual(payload["parameters"]["obstacle_count"], 8_192)
        self.assertTrue(payload["comparison"]["all_same_contract"])
        self.assertTrue(payload["comparison"]["all_signature_hashes_match_cross_backend"])
        self.assertTrue(payload["comparison"]["all_flagged_group_counts_match_cross_backend"])
        self.assertTrue(payload["comparison"]["all_host_buffer_reuse_same_contract"])
        self.assertFalse(payload["comparison"]["public_speedup_claim_authorized"])
        rows = {row["backend"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"embree", "optix"})
        self.assertEqual(rows["embree"]["measured_signature_hashes"], rows["optix"]["measured_signature_hashes"])
        self.assertEqual(rows["embree"]["flagged_group_count_values"], rows["optix"]["flagged_group_count_values"])
        for row in rows.values():
            self.assertEqual(row["contract"], "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1")
            self.assertEqual(row["group_count"], 1_048_576)
            self.assertEqual(row["segment_count"], 9_437_184)
            self.assertEqual(row["static_obstacle_triangle_count"], 16_384)
            self.assertTrue(row["host_query_output_buffers_reused"])
            self.assertFalse(row["native_query_output_buffers_reused"])
            self.assertFalse(row["probe_reference_validated"])
            self.assertGreater(row["tail_total_run_window_sec"], 1.0)
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
        pair = payload["comparison"]["same_contract_backend_pair"]
        self.assertTrue(pair["same_contract"])
        self.assertTrue(pair["same_case_shape"])
        self.assertTrue(pair["same_signature_hashes"])
        self.assertGreater(pair["embree_over_optix_traversal_median"], 1.0)


if __name__ == "__main__":
    unittest.main()
