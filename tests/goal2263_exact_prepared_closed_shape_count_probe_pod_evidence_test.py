import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2263_exact_prepared_closed_shape_count_probe_pod_evidence_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2263_exact_prepared_closed_shape_count_probe_pod_2026-05-17.json"
GOAL2262 = ROOT / "docs" / "reports" / "goal2262_exact_prepared_closed_shape_count_without_final_rows_2026-05-17.md"


class Goal2263ExactPreparedClosedShapeCountProbePodEvidenceTest(unittest.TestCase):
    def test_artifact_records_exact_count_parity(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["commit"], "4f03c1cb5d9bedc18963d07df49220fc38f3e4c4")
        self.assertEqual(data["query_count"], 100000)
        self.assertEqual(data["reference_count"], 8686)
        self.assertTrue(data["prepared_rows"]["all_match_reference_count"])
        self.assertTrue(data["prepared_count"]["all_match_reference_count"])
        self.assertEqual(set(data["prepared_rows"]["counts"]), {8686})
        self.assertEqual(set(data["prepared_count"]["counts"]), {8686})

    def test_exact_count_is_faster_than_row_return(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows_median = data["prepared_rows"]["elapsed_sec_median"]
        count_median = data["prepared_count"]["elapsed_sec_median"]

        self.assertLess(count_median, rows_median)
        self.assertLess(count_median / rows_median, 0.75)

    def test_report_keeps_boundary_and_semantic_cleanup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        goal2262 = GOAL2262.read_text(encoding="utf-8")

        self.assertIn("1.37x", text)
        self.assertIn("1.04x", text)
        self.assertIn("semantic cleanup", text)
        self.assertIn("not a true device-resident output stream", text)
        self.assertIn("pod timing recorded by Goal2263", goal2262)


if __name__ == "__main__":
    unittest.main()
