import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2266_prepared_closed_shape_count_scale_probe_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2266_prepared_closed_shape_count_scale_probe_pod_2026-05-17.json"


class Goal2266PreparedClosedShapeCountScaleProbeTest(unittest.TestCase):
    def test_artifact_records_expected_scales(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["commit"], "749158335c6a2d86832890c5d627b803a32041a7")
        self.assertEqual(data["query_stream_transform"], "repeat_rayjoin_exported_100k_queries_with_new_ids")
        factors = [row["factor"] for row in data["results"]]
        self.assertEqual(factors, [1, 2, 5, 10])

    def test_count_is_faster_and_exact_at_every_scale(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for row in data["results"]:
            self.assertTrue(row["rows_all_match_expected"])
            self.assertTrue(row["count_all_match_expected"])
            self.assertEqual(set(row["row_counts"]), {row["expected_count"]})
            self.assertEqual(set(row["count_values"]), {row["expected_count"]})
            self.assertLess(row["count_elapsed_sec_median"], row["rows_elapsed_sec_median"])
            self.assertLess(row["count_vs_rows_ratio"], 0.8)

    def test_report_keeps_synthetic_scale_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("scale diagnostic", text)
        self.assertIn("not a new RayJoin paper dataset claim", text)
        self.assertIn("1,000,000", text)
        self.assertIn("does not authorize", text)
        self.assertIn("not a substitute", text)


if __name__ == "__main__":
    unittest.main()
