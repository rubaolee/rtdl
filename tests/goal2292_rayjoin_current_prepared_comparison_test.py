import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2292_rayjoin_current_prepared_comparison.py"
REPORT = ROOT / "docs" / "reports" / "goal2292_rayjoin_current_prepared_comparison_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2292_rayjoin_current_prepared_comparison_pod_2026-05-17.json"


class Goal2292RayJoinCurrentPreparedComparisonTest(unittest.TestCase):
    def test_script_uses_current_prepared_routes(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_segment_pair_intersection_optix", text)
        self.assertIn("prepare_point_closed_shape_membership_2d_optix", text)
        self.assertIn("pack_segments(records=left_records)", text)
        self.assertIn("pack_points(records=points, dimension=2)", text)
        self.assertIn("prepared_segment_pair_intersection_optix_with_prepacked_left", text)
        self.assertIn("prepared_point_closed_shape_membership_2d_optix_with_prepacked_points", text)

    def test_artifact_records_expected_current_results(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["commit"], "38399f3b847b6af7c3ccbbf9b1c290d1d8b7b090")
        self.assertEqual(data["goal"], 2292)
        self.assertTrue(data["lsi"]["row_count_parity"])
        self.assertTrue(data["pip"]["row_count_parity"])
        self.assertTrue(data["lsi"]["matches_prior_expected_count"])
        self.assertTrue(data["pip"]["matches_prior_expected_count"])
        self.assertEqual(data["lsi"]["expected_rows_from_prior_cpu_verified_artifacts"], 8921)
        self.assertEqual(data["pip"]["expected_rows_from_prior_cpu_verified_artifacts"], 8686)
        self.assertLess(data["lsi"]["raw_rows"]["median_sec"], 0.02)
        self.assertLess(data["lsi"]["scalar_count"]["median_sec"], 0.02)
        self.assertLess(data["pip"]["positive_rows"]["median_sec"], 0.07)
        self.assertLess(data["pip"]["scalar_count"]["median_sec"], data["pip"]["positive_rows"]["median_sec"])

    def test_report_marks_old_lsi_number_as_stale_route_context(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("older `compiled_rtdl_kernel` path", text)
        self.assertIn("stale Goal2252 LSI route", text)
        self.assertIn("about `7.89x` faster", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()
