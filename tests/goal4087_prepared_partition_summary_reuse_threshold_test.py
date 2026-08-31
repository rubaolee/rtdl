from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4087_prepared_partition_summary_reuse_threshold.py"
REPORT = ROOT / "docs" / "reports" / "goal4087_prepared_partition_summary_reuse_threshold_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4087_prepared_partition_summary_reuse_threshold_pod.json"
STDOUT = ROOT / "docs" / "reports" / "goal4087_prepared_partition_summary_reuse_threshold_pod.stdout.txt"


class Goal4087PreparedPartitionSummaryReuseThresholdTest(unittest.TestCase):
    def test_runner_records_reuse_threshold_fields(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for fragment in [
            "CURRENT_RECOMMENDED_REFERENCE_SEC",
            "break_even_runs_reference",
            "speedup_vs_current_reference_for_n_runs",
            "prepared_partition_summary_reuse_threshold",
            "automatic partner selection",
        ]:
            self.assertIn(fragment, source)

    def test_artifact_records_clustered_and_road_reuse_outcomes(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4087")
        self.assertEqual(payload["schema"], "rtdl.goal4087.prepared_partition_summary_reuse_threshold.v1")
        self.assertEqual(payload["source_commit"][:8], "534446d1")
        self.assertEqual(tuple(payload["profiles"]), ("clustered3d", "road3d"))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        rows = {row["profile"]: row for row in payload["rows"]}
        clustered = rows["clustered3d"]
        road = rows["road3d"]

        self.assertTrue(clustered["component_signature_match"])
        self.assertLess(
            clustered["component_signature_replay_sec"]["median_sec"],
            clustered["current_recommended_reference_sec"],
        )
        self.assertGreater(clustered["amortized"]["break_even_runs_reference"], 10.0)
        self.assertLess(clustered["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)

        self.assertTrue(road["component_signature_match"])
        self.assertGreater(
            road["component_signature_replay_sec"]["median_sec"],
            road["current_recommended_reference_sec"],
        )
        self.assertIsNone(road["amortized"]["break_even_runs_reference"])
        self.assertLess(road["amortized"]["speedup_vs_current_reference_for_n_runs"], 1.0)

    def test_report_sets_default_policy_and_next_direction(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "not a default route",
            "roughly 12 repeated",
            "road-shaped reuse does not break even",
            "thin prepared-summary wrapper should not become the default",
            "cheaper native/device producer",
            "at least 50% candidate-hit or root-call reduction",
            "does not promote",
        ]:
            self.assertIn(fragment, report)

    def test_stdout_contains_progress_markers(self) -> None:
        stdout = STDOUT.read_text(encoding="utf-8")
        for fragment in [
            "PROFILE_PREPARE_START clustered3d",
            "PROFILE_SIGNATURE_MEASURE_START clustered3d run=1",
            "PROFILE_PREPARE_START road3d",
            "PROFILE_SIGNATURE_MEASURE_START road3d run=1",
            '"goal": "Goal4087"',
        ]:
            self.assertIn(fragment, stdout)


if __name__ == "__main__":
    unittest.main()
