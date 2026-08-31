import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3978_current_scale_repeatability_probe_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3978_current_scale_repeatability_probe_2026-06-08"
AGGREGATE = ARTIFACT / "aggregate.json"


class Goal3978CurrentScaleRepeatabilityProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.aggregate = json.loads(AGGREGATE.read_text(encoding="utf-8"))

    def test_three_runs_all_passed(self) -> None:
        self.assertEqual(self.aggregate["run_count"], 3)
        self.assertTrue(self.aggregate["all_runs_pass"])
        for run_id in (1, 2, 3):
            summary = json.loads((ARTIFACT / f"run_{run_id}" / "summary.json").read_text(encoding="utf-8"))
            self.assertTrue(summary["all_pass"])
            self.assertEqual(summary["json_pass_count"], 10)
            self.assertEqual((ARTIFACT / f"run_{run_id}" / "stderr.log").read_text(encoding="utf-8"), "")

    def test_aggregate_records_stability_and_short_row_variance(self) -> None:
        rows = {row["row_id"]: row for row in self.aggregate["rows"]}
        self.assertEqual(len(rows), 10)
        self.assertLess(
            rows["spatial_rayjoin_public_cdb_representative_mixed_route_scale_default"]["relative_range"],
            0.001,
        )
        self.assertLess(rows["rt_dbscan_optix_numba_scale_default_65536_no_validation"]["relative_range"], 0.001)
        self.assertGreater(rows["robot_collision_optix_scale_default_1024_no_probe_reference"]["relative_range"], 0.10)
        self.assertGreater(rows["raydb_style_optix_count_scale_default_262k"]["relative_range"], 0.10)

    def test_source_commit_and_report_boundary_are_recorded(self) -> None:
        self.assertEqual(
            self.aggregate["source_commit"],
            "62f005d90caca8eeea0d40cbbab430fe890a4fa3",
        )
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "timing stability",
            "All three runs passed all ten rows",
            "benchmark scale calibration",
            "does not authorize",
            "app-specific",
            "native-engine logic",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
