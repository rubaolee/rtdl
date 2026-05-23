from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2473_grouped_union_atomic_scale_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2473_grouped_union_atomic_scale_telemetry_2026-05-21.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2473_grouped_union_atomic_scale_pod.json"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2473GroupedUnionAtomicScaleTelemetryTest(unittest.TestCase):
    def test_runner_collects_generic_telemetry_without_claiming_performance(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("goal2473_grouped_union_atomic_scale_pod.json", script)
        self.assertIn("parent_atomic_attempts", script)
        self.assertIn("fallback_atomic_attempts", script)
        self.assertIn("performance_claim_authorized", script)
        self.assertIn("dbscan_native_abi_added", script)
        self.assertIn("apply_device_grouped_union_all_self", script)
        self.assertIn("apply_device_grouped_union_self", script)

    def test_report_records_atomic_count_not_dominant_interpretation(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("not a new native optimization", report)
        self.assertIn("does not authorize a performance claim", report)
        self.assertIn("1.19x-1.23x the", report)
        self.assertIn("atomic-count reduction alone is not enough", report)
        self.assertIn("No DBSCAN-specific native ABI was added", report)
        self.assertIn("Goal2473", todo)
        self.assertIn("duplicate global parent atomics alone", todo)

    def test_pod_artifact_is_recorded(self) -> None:
        artifact = ARTIFACT.read_text(encoding="utf-8")

        self.assertIn('"goal": "Goal2473"', artifact)
        self.assertIn('"telemetry_only": true', artifact)
        self.assertIn('"tail_median_parent_attempts_per_point"', artifact)
        self.assertIn('"NVIDIA RTX A5000, 570.211.01"', artifact)


if __name__ == "__main__":
    unittest.main()
