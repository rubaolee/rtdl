import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2122_xhd_grouped_hausdorff_pod_perf_2026-05-16.md"
MILLION = ROOT / "docs" / "reports" / "goal2121_pod_grouped_million_hd_perf_2026-05-16.json"
XLARGE = ROOT / "docs" / "reports" / "goal2121_pod_grouped_xlarge_hd_perf_2026-05-16.json"
LARGE = ROOT / "docs" / "reports" / "goal2121_pod_grouped_large_hd_perf_2026-05-16.json"


class Goal2122XhdGroupedHausdorffPodPerfTest(unittest.TestCase):
    def test_report_records_boundary_and_next_primitive(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("RT 2.21x faster", text)
        self.assertIn("Same-dataset X-HD paper claim: `needs-more-evidence`", text)
        self.assertIn("POINT_GROUP_NEAREST_REDUCE(MAX_DISTANCE, ARGMAX_QUERY, ARGMIN_POINT)", text)

    def test_million_point_artifact_records_exact_speedup(self) -> None:
        payload = json.loads(MILLION.read_text(encoding="utf-8"))
        rows = payload["rows"]
        self.assertTrue(rows)
        best = min(rows, key=lambda row: row["grouped_vs_cupy_ratio"])
        self.assertEqual(best["n"], 1048576)
        self.assertTrue(best["matches_exact"])
        self.assertLess(best["grouped_vs_cupy_ratio"], 0.5)

    def test_crossover_artifacts_are_present(self) -> None:
        xlarge = json.loads(XLARGE.read_text(encoding="utf-8"))
        large = json.loads(LARGE.read_text(encoding="utf-8"))
        self.assertTrue(any(row["n"] == 524288 and row["grouped_vs_cupy_ratio"] < 1.0 for row in xlarge["rows"]))
        self.assertTrue(any(row["n"] == 262144 and row["matches_exact"] for row in large["rows"]))


if __name__ == "__main__":
    unittest.main()
