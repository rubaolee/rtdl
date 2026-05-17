import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2259_prepared_closed_shape_count_probe_pod_evidence_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2259_prepared_closed_shape_count_probe_pod_2026-05-17.json"
GOAL2258 = ROOT / "docs" / "reports" / "goal2258_prepared_closed_shape_membership_count_mode_2026-05-17.md"


class Goal2259PreparedClosedShapeCountProbePodEvidenceTest(unittest.TestCase):
    def test_count_probe_artifact_matches_reference(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["commit"], "73f58a059e393788cf48b66694223c2c08944dd3")
        self.assertEqual(data["query_count"], 100000)
        self.assertEqual(data["reference_count"], 8686)
        self.assertTrue(data["prepared_rows"]["all_match_reference_count"])
        self.assertTrue(data["prepared_count"]["all_match_reference_count"])
        self.assertEqual(set(data["prepared_rows"]["counts"]), {8686})
        self.assertEqual(set(data["prepared_count"]["counts"]), {8686})

    def test_count_mode_is_faster_than_row_materialization_in_probe(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows_median = data["prepared_rows"]["elapsed_sec_median"]
        count_median = data["prepared_count"]["elapsed_sec_median"]

        self.assertLess(count_median, rows_median)
        self.assertLess(count_median / rows_median, 0.85)

    def test_reports_keep_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        goal2258 = GOAL2258.read_text(encoding="utf-8")

        self.assertIn("1.26x", text)
        self.assertIn("not the final RayJoin pure-GPU metric", text)
        self.assertIn("does not authorize", text)
        self.assertIn("pod timing recorded by Goal2259", goal2258)


if __name__ == "__main__":
    unittest.main()
