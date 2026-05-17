import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "reports" / "goal2280_direct_index_ab_baseline_goal2276_pod_2026-05-17.json"
CURRENT = ROOT / "docs" / "reports" / "goal2280_direct_index_ab_current_goal2279_pod_2026-05-17.json"
SUMMARY = ROOT / "docs" / "reports" / "goal2280_direct_index_ab_same_pod_summary_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2280_direct_index_refinement_negative_ab_probe_2026-05-17.md"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal2280DirectIndexRefinementNegativeAbProbeTest(unittest.TestCase):
    def test_artifacts_record_same_stream_and_commits(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        current = json.loads(CURRENT.read_text(encoding="utf-8"))

        self.assertEqual(baseline["commit"], "5c41ade112fb7ebbcdd6ed593eea96eb806db75f")
        self.assertEqual(current["commit"], "2a63e71dcb31f7227673d2055b749757aa5e8f9b")
        self.assertEqual(baseline["query_stream"], current["query_stream"])
        self.assertEqual(baseline["query_stream_producer"], "rayjoin_query_exec_export_patch")
        self.assertEqual(current["query_stream_producer"], "rayjoin_query_exec_export_patch")
        self.assertEqual(baseline["query_count"], 100_000)
        self.assertEqual(current["query_count"], 100_000)

    def test_direct_index_candidate_is_not_an_accepted_speedup(self) -> None:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        current = json.loads(CURRENT.read_text(encoding="utf-8"))
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertTrue(baseline["parity"])
        self.assertTrue(current["parity"])
        self.assertEqual(baseline["raw_row_count"], 8_921)
        self.assertEqual(current["raw_row_count"], 8_921)
        row_speedup = baseline["row_raw_median_sec"] / current["row_raw_median_sec"]
        count_speedup = baseline["count_median_sec"] / current["count_median_sec"]
        self.assertAlmostEqual(summary["same_pod_speedups"]["raw_rows"], row_speedup)
        self.assertAlmostEqual(summary["same_pod_speedups"]["count"], count_speedup)
        self.assertEqual(summary["decision"], "reject_and_revert_direct_index_refinement")
        self.assertLess(row_speedup, 1.0)
        self.assertLess(count_speedup, 1.02)

    def test_main_source_no_longer_carries_direct_candidate_indices(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index("struct GpuSegmentPairIntersectionRecord")
        end = text.index("struct GpuPipRecord", start)
        record_body = text[start:end]

        self.assertIn("uint32_t left_id, right_id", record_body)
        self.assertIn("float ix, iy", record_body)
        self.assertNotIn("left_index", record_body)
        self.assertNotIn("right_index", record_body)

    def test_report_documents_reverted_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("negative evidence", text)
        self.assertIn("implementation was reverted", text)
        self.assertIn("canonical comparison", text)
        self.assertIn("direct-index host exact refinement was tested and rejected", text)
        self.assertIn("Not allowed", text)


if __name__ == "__main__":
    unittest.main()
