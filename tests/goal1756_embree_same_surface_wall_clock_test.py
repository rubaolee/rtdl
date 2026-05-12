import json
import unittest

from scripts.goal1756_embree_same_surface_wall_clock import (
    COMMANDS,
    REPORT_JSON,
    REPORT_MD,
    build_report,
    write_report,
)


class Goal1756EmbreeSameSurfaceWallClockTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        write_report(build_report())

    def test_embree_column_has_complete_same_surface_ratios(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["verdict"],
            "embree_same_surface_wall_clock_column_ready_without_public_speedup_claim",
        )
        self.assertEqual(payload["row_count"], len(COMMANDS))
        self.assertEqual(
            payload["class_counts"],
            {"same_surface_app_wall_clock_ratio": len(COMMANDS)},
        )
        for row in payload["rows"]:
            self.assertEqual(row["classification"], "same_surface_app_wall_clock_ratio")
            self.assertEqual(row["baseline_returncode"], 0)
            self.assertEqual(row["current_returncode"], 0)
            self.assertTrue(row["baseline_stdout_json"])
            self.assertTrue(row["current_stdout_json"])
            self.assertIsInstance(row["baseline_over_current_ratio"], float)
            self.assertGreater(row["baseline_over_current_ratio"], 0.0)

    def test_report_keeps_public_and_release_claims_blocked(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertFalse(payload["public_claim_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertIn("must not be used as public speedup wording", payload["boundary"])
        for row in payload["rows"]:
            self.assertFalse(row["public_claim_authorized"])

    def test_methodology_records_repaired_inputs_and_scaled_rows(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        notes = "\n".join(payload["methodology_notes"])
        self.assertIn("tests/fixtures/rayjoin/br_county_subset.cdb", notes)
        self.assertIn("polygon_set_jaccard uses --copies 2000", notes)
        self.assertIn("robot_collision_screening uses --pose-count 20000", notes)
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("same app-level CLI command", text)
        self.assertIn("not a practical complete-column workload", text)


if __name__ == "__main__":
    unittest.main()
