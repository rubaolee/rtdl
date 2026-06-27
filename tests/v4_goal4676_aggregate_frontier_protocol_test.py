from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_maintainer as v4


class V4Goal4676AggregateFrontierProtocolTest(unittest.TestCase):
    def test_protocol_freezes_serious_scale_and_bars(self) -> None:
        protocol = v4.v4_goal4676_aggregate_frontier_protocol().as_dict()
        bars = protocol["pass_fail_bar"]

        self.assertEqual("goal4676_aggregate_frontier_focused_pod_protocol_frozen_not_run", protocol["status"])
        self.assertEqual("v4_aggregate_frontier_device_columns_2d_prepared_runner", protocol["target_surface"])
        self.assertEqual("AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D", protocol["generic_primitive"])
        self.assertEqual(32768, protocol["body_count"])
        self.assertEqual(7, protocol["repeat"])
        self.assertEqual(2, protocol["warmup"])
        self.assertEqual(2048, protocol["correctness_companion_body_count"])
        self.assertEqual(1.20, bars["v4_frontier_only_hot_over_v2_14_min"])
        self.assertEqual(1.20, bars["v4_full_hot_over_v2_14_min"])
        self.assertEqual(1.10, bars["v4_full_wall_over_v2_14_min"])
        self.assertFalse(bars["partner_migration_counts_as_speed"])
        self.assertFalse(bars["host_frontier_materialization_in_hot_path_allowed"])

    def test_protocol_rejects_weak_v2_denominator_and_release_claims(self) -> None:
        protocol = v4.v4_goal4676_aggregate_frontier_protocol().as_dict()

        self.assertIn("collect_aggregate_frontier_2d_optix", protocol["v2_14_denominator"])
        self.assertIn("must not silently fall back to a weak CPU-only denominator", protocol["v2_14_denominator"])
        self.assertIn("host-materialized row_offsets/frontier_i64_rows", protocol["v2_14_denominator"])
        self.assertIn("device-column primitive already exists in V3.0.2", protocol["v3_0_2_control"])
        self.assertTrue(all(value is False for value in protocol["non_authorization"].values()))

    def test_validation_passes_current_protocol(self) -> None:
        validation = v4.validate_v4_goal4676_aggregate_frontier_protocol()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertTrue(validation["pod_benchmark_protocol_frozen"])
        self.assertFalse(validation["release_authorized"])


if __name__ == "__main__":
    unittest.main()
