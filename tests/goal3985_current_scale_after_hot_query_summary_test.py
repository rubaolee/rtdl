import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3985_current_scale_after_hot_query_summary_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3985_current_scale_after_hot_query_summary_2026-06-08"
SUMMARY = ARTIFACT / "summary.json"
OUTPUTS = ARTIFACT / "outputs"


class Goal3985CurrentScaleAfterHotQuerySummaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.rows = {row["row_id"]: row for row in cls.summary["rows"]}

    def test_full_current_scale_packet_passes(self) -> None:
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(self.summary["json_pass_count"], 10)
        self.assertEqual(len(self.rows), 10)
        self.assertFalse(self.summary["release_authorized"])
        self.assertFalse(self.summary["public_speedup_claim_authorized"])
        self.assertFalse(self.summary["broad_rt_core_claim_authorized"])
        self.assertEqual((ARTIFACT / "runner.stderr.log").read_text(encoding="utf-8"), "")

    def test_raydb_summary_only_iterations_make_aggregate_hot_metric_seconds_level(self) -> None:
        payload = json.loads(
            (OUTPUTS / "raydb_style_optix_count_scale_default_262k.stdout.json").read_text(
                encoding="utf-8"
            )
        )
        metadata = payload["metadata"]
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertTrue(metadata["prepared_iteration_wall_sec_suppressed"])
        self.assertEqual(metadata["prepared_iteration_wall_sec"], [])
        self.assertGreater(
            metadata["prepared_phase_timing_summary"]["native_call_wall"]["total_sec"],
            1.0,
        )
        self.assertGreater(metadata["prepared_iteration_wall_summary"]["total_sec"], 1.0)

    def test_robot_summary_only_runs_make_aggregate_hot_metric_seconds_level(self) -> None:
        payload = json.loads(
            (OUTPUTS / "robot_collision_optix_scale_default_1024_no_probe_reference.stdout.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(payload["run_details_suppressed"])
        self.assertEqual(payload["runs"], [])
        self.assertEqual(payload["reuse_metadata"]["repeat_count"], 50000)
        self.assertEqual(payload["reuse_metadata"]["prepared_run_index_summary"]["last"], 50000)
        self.assertGreater(
            payload["run_summary"]["phase_timing_seconds"]["traversal"]["total_sec"],
            1.0,
        )
        self.assertGreater(payload["run_summary"]["total_run_seconds"]["total_sec"], 1.0)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "fresh RTX 4000 Ada pod checkout",
            "The two former short rows now produce seconds-level aggregate hot-path summaries",
            "does not authorize release action",
            "Wrapper elapsed remains pod-budget evidence",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
