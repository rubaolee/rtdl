from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4085_partition_summary_build_feasibility.py"
REPORT = ROOT / "docs" / "reports" / "goal4085_partition_summary_build_feasibility_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4085_partition_summary_build_feasibility_pod.json"
STDOUT = ROOT / "docs" / "reports" / "goal4085_partition_summary_build_feasibility_pod.stdout.txt"


class Goal4085PartitionSummaryBuildFeasibilityTest(unittest.TestCase):
    def test_runner_records_partition_build_metric_and_claim_boundary(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("partition_summary_build_sec", script)
        self.assertIn("device_count_then_emit", script)
        self.assertIn("public_speedup_claim_authorized", script)
        self.assertIn("native_abi_added", script)

    def test_pod_artifact_records_three_current_profiles(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4085")
        self.assertEqual(payload["source_commit"][:8], "0c1a717f")
        self.assertEqual(payload["point_count"], 65536)
        self.assertEqual(tuple(payload["profiles"]), ("clustered3d", "road3d", "ngsim_dense"))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["native_abi_added"])
        for row in payload["rows"]:
            self.assertEqual(row["pair_capacity_source"], "device_exact_count")
            self.assertTrue(row["device_pair_count_probe_used"])
            self.assertTrue(row["complete_candidate_coverage"])
            self.assertFalse(row["overflow"])
            self.assertGreater(row["partition_summary_build_sec"]["median_sec"], 0.0)
            self.assertGreater(row["pair_count"], 0)

    def test_report_explains_blocking_feasibility_conclusion(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "build cost is already too high",
            "not be a thin wrapper around the current CuPy preview summary builder",
            "Prepared-reuse route",
            "Cheaper native producer",
            "Fused native route",
            "contiguous query-range entry points",
            "does not promote",
        ]:
            self.assertIn(fragment, report)

    def test_stdout_contains_progress_for_all_profiles(self) -> None:
        stdout = STDOUT.read_text(encoding="utf-8")
        for profile in ["clustered3d", "road3d", "ngsim_dense"]:
            self.assertIn(f"PROFILE_WARMUP {profile}", stdout)
            self.assertIn(f"PROFILE_MEASURE {profile}", stdout)


if __name__ == "__main__":
    unittest.main()
