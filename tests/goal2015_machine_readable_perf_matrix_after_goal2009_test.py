from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs" / "reports" / "goal2015_current_all_app_v18_v2_perf_analysis_after_goal2009_2026-05-14.json"
REPORT = ROOT / "docs" / "reports" / "goal2015_machine_readable_perf_matrix_after_goal2009_2026-05-14.md"


class Goal2015MachineReadablePerfMatrixAfterGoal2009Test(unittest.TestCase):
    def test_json_refreshes_only_current_road_hazard_evidence(self) -> None:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))
        row = next(item for item in data["rows"] if item["app"] == "road_hazard_screening")

        self.assertEqual(data["goal"], "Goal2015")
        self.assertTrue(data["claim_boundary"]["road_hazard_row_refreshed_after_goal2009"])
        self.assertEqual(row["artifact"], "docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_4096.json")
        self.assertEqual(row["matrix_state"], "implemented-and-pod-timed-current-goal2009")
        self.assertEqual(row["claim_class"], "implemented-prepared-cupy-exact-filter")
        self.assertEqual(row["size"], 4096)
        self.assertAlmostEqual(row["v18_prepared_s"], 0.009691450744867325)
        self.assertAlmostEqual(row["v2_prepared_partner_s"], 0.00393231026828289)
        self.assertLess(row["ratio_vs_v18_prepared"], 0.41)

    def test_json_keeps_release_boundary_false(self) -> None:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))
        boundary = data["claim_boundary"]

        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["control_rows_are_speedup_evidence"])
        self.assertEqual(data["row_count"], 16)

    def test_report_documents_the_json_delta(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2015 creates the machine-readable successor", text)
        self.assertIn("0.4057504259994795", text)
        self.assertIn("2.46x", text)
        self.assertIn("does not reclassify the other 15 rows", text)


if __name__ == "__main__":
    unittest.main()
