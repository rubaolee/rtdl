from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3996_grouped_union_extended_telemetry_sweep_pod.py"
ARTIFACT = ROOT / "docs" / "reports" / "goal3996_grouped_union_extended_telemetry_sweep_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal3996_grouped_union_extended_telemetry_sweep_2026-06-08.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal3996GroupedUnionExtendedTelemetrySweepTest(unittest.TestCase):
    def test_sweep_script_is_progressive_and_bounded(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("[goal3996] start point_count=", script)
        self.assertIn("[goal3996] point_count=", script)
        self.assertIn("--repeats", script)
        self.assertIn("performance_claim_authorized", script)
        self.assertIn("telemetry_is_diagnostic", script)

    def test_pod_artifact_records_all_mode_variants(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["claim_boundary"]["performance_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertEqual(payload["point_counts"], [4096, 16384, 65536])
        labels = {
            variant["label"]
            for row in payload["rows"]
            for variant in row["variants"]
        }
        self.assertEqual(
            labels,
            {
                "same_root_on_direct_off",
                "same_root_off_direct_off",
                "same_root_on_direct_on",
                "same_root_off_direct_on",
            },
        )

    def test_large_row_shows_candidate_work_dominates_unions(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        large = next(row for row in payload["rows"] if row["point_count"] == 65536)
        default = next(
            variant for variant in large["variants"]
            if variant["label"] == "same_root_on_direct_off"
        )
        telemetry = default["last_telemetry"]
        self.assertGreater(telemetry[4], 800_000_000)
        self.assertEqual(telemetry[1], 65_535)
        self.assertGreater(telemetry[4], telemetry[1] * 10_000)
        self.assertGreater(telemetry[5], telemetry[7])

    def test_report_keeps_next_step_generic_and_non_authorizing(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")
        for fragment in [
            "simple mode switches are exhausted",
            "generic dense grouped-union primitive",
            "convergence/staleness/status metadata",
            "not a performance optimization",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)
        self.assertIn("Dense Fixed-Radius Grouped Union", todo)
        self.assertNotIn("DBSCAN native ABI", report)


if __name__ == "__main__":
    unittest.main()
