from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.v3_phoenix_spatial_lsi_optix_m9_intake import (
    DEFAULT_JSON_OUT,
    DEFAULT_MD_OUT,
    TARGET_ROW_ID,
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_lsi_optix_m9_intake.py"


class V3PhoenixSpatialLsiOptixM9IntakeTest(unittest.TestCase):
    def test_intake_classifies_lsi_loss_without_authorizing_pod(self) -> None:
        payload = build_payload()

        self.assertEqual(payload["tool"], "v3_phoenix_spatial_lsi_optix_m9_intake")
        self.assertEqual(payload["status"], "m9_spatial_lsi_optix_mechanics_intake_not_release_not_pod")
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["focused_pod_spend_authorized"])
        self.assertFalse(payload["full_all_app_pod_spend_authorized"])
        self.assertFalse(payload["implementation_authorized_by_this_packet"])
        self.assertTrue(payload["needs_2ai_review_before_m10"])

        self.assertEqual(payload["target"]["row_id"], TARGET_ROW_ID)
        self.assertAlmostEqual(payload["source_row"]["v3_speedup_vs_v2"], 0.8881209503239741)
        self.assertAlmostEqual(payload["source_row"]["absolute_delta_microseconds"], 15.437602996826172)
        self.assertEqual(payload["source_row"]["primary_metric_source_v2"], "phases_sec.prepared_query_sec")
        self.assertEqual(payload["source_row"]["primary_metric_source_v3"], "phases_sec.prepared_query_sec")

        route = payload["route_mapping"]
        self.assertEqual(route["workload"], "lsi")
        self.assertEqual(route["execution_route"], "prepared_optix_left_id_dense_count_prepared_left_reuse")
        self.assertIsNone(route["productized_execution_path"])
        self.assertFalse(route["prepared_execution_session_runner_present"])
        self.assertFalse(route["topology_stream_prepared_handle_present"])

        coverage = payload["productized_runner_coverage"]
        self.assertTrue(coverage["point_location_topology_stream_productized_runner_exists"])
        self.assertIsInstance(
            coverage["segment_intersection_topology_stream_productized_runner_exists_in_current_code"],
            bool,
        )
        self.assertIn("generic segment_intersection_topology_stream", coverage["gap"])

        metric = payload["metric_interpretation"]
        self.assertTrue(metric["row_is_v3_vs_v2_regression_not_optix_vs_embree_result"])
        self.assertGreater(metric["current_optix_vs_current_embree_ratio"], 300.0)

    def test_cli_writes_non_release_outputs(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--pretty"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(DEFAULT_JSON_OUT.exists())
        self.assertTrue(DEFAULT_MD_OUT.exists())
        markdown = DEFAULT_MD_OUT.read_text(encoding="utf-8")
        self.assertIn("Phoenix V3 M9 Spatial LSI OptiX Mechanics Intake", markdown)
        self.assertIn("focused_pod_spend_authorized: false", markdown)
        self.assertIn("implementation_authorized_by_this_packet: false", markdown)
        self.assertIn("Segment-intersection topology-stream runner exists", markdown)
        self.assertIn("V3-vs-V2 regression row, not an OptiX-vs-Embree result", markdown)


if __name__ == "__main__":
    unittest.main()
