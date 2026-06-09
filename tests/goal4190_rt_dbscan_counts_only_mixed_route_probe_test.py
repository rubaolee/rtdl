import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada"
REPORT = ROOT / "docs" / "reports" / "goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada_2026-06-09.md"
SCRIPT = ROOT / "scripts" / "goal4190_rt_dbscan_counts_only_mixed_route_probe.py"
POINT_COUNTS = (262_144, 1_048_576, 2_097_152, 4_194_304)


class Goal4190RtDbscanCountsOnlyMixedRouteProbeTest(unittest.TestCase):
    def _payload(self, point_count: int) -> dict:
        path = ARTIFACT_DIR / f"goal4190_road3d_{point_count}_radius0003_min16.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_probe_artifacts_record_counts_only_match_without_component_match(self) -> None:
        for point_count in POINT_COUNTS:
            payload = self._payload(point_count)
            self.assertEqual(payload["goal"], "Goal4190")
            self.assertEqual(payload["source_commit"][:8], "94933000")
            self.assertEqual(payload["point_count"], point_count)
            self.assertEqual(payload["radius"], 0.003)
            self.assertEqual(payload["min_neighbors"], 16)
            self.assertEqual(len(payload["rows"]), 3)
            rows = {row["label"]: row for row in payload["rows"]}
            self.assertTrue(rows["current_grouped_stream_numba"]["same_policy_bound_component_sizes_as_reference"])
            self.assertTrue(rows["current_grouped_stream_numba"]["same_counts_only_as_reference"])
            for label in (
                "predicate_direct_status_until_stable",
                "predicate_direct_status_single_pass_candidate",
            ):
                self.assertFalse(rows[label]["same_policy_bound_component_sizes_as_reference"], (point_count, label))
                self.assertTrue(rows[label]["same_counts_only_as_reference"], (point_count, label))
                self.assertTrue(rows[label]["rt_core_accelerated"], (point_count, label))

    def test_performance_result_stays_bounded_and_non_promotional(self) -> None:
        speedups = {
            point_count: {
                row["label"]: float(row["speedup_vs_grouped_elapsed"])
                for row in self._payload(point_count)["rows"]
            }
            for point_count in POINT_COUNTS
        }
        self.assertLess(speedups[262_144]["predicate_direct_status_single_pass_candidate"], 1.0)
        self.assertGreater(speedups[4_194_304]["predicate_direct_status_single_pass_candidate"], 1.0)
        self.assertLess(speedups[4_194_304]["predicate_direct_status_single_pass_candidate"], 1.1)
        for point_count in POINT_COUNTS:
            self.assertLess(speedups[point_count]["predicate_direct_status_until_stable"], 1.0)
            payload = self._payload(point_count)
            self.assertFalse(payload["route_promotion_authorized"])
            self.assertFalse(payload["public_speedup_claim_authorized"])
            self.assertFalse(payload["release_authorized"])

    def test_report_and_script_keep_engine_boundary_generic(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("does not add an engine", report)
        self.assertIn("not a major win", report)
        self.assertIn("Goal4165/Goal4166 remain the evidence", report)
        self.assertIn("generic predicate-aware direct-status grouped-union", report)
        self.assertIn("DBSCAN policy remains in", report)
        self.assertIn("route_promotion_authorized", script)
        self.assertIn("component_size_contract=\"core_noise_assigned_counts_only\"", script)
        self.assertNotIn("rtdl_optix_dbscan", script.lower())

    def test_stderr_contains_only_numba_warnings(self) -> None:
        for point_count in POINT_COUNTS:
            stderr = (ARTIFACT_DIR / f"goal4190_road3d_{point_count}.stderr.txt").read_text(encoding="utf-8")
            self.assertNotIn("Traceback", stderr)
            self.assertNotIn("ERROR", stderr.upper())
            stripped = stderr.strip()
            if stripped:
                self.assertIn("NumbaPerformanceWarning", stripped)


if __name__ == "__main__":
    unittest.main()
