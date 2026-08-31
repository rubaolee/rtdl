from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3864_full_scale_after_librts_multi_operation_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3864_full_scale_after_librts_multi_operation_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
GEMINI_REVIEW = ROOT / "docs/reviews/goal3863_gemini_review_goal3859_3862_perf_chain_2026-06-08.md"
GOAL3859_FOCUSED = ROOT / "docs/reports/goal3859_rt_dbscan_numba_grouped_stream_a5000/summary.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3864FullScaleAfterLibRtsMultiOperationTest(unittest.TestCase):
    def test_full_scale_packet_passes_all_ten_rows(self) -> None:
        summary = _load(SUMMARY)

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["json_pass_count"], 10)
        self.assertEqual(len(summary["rows"]), 10)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])

        for row in summary["rows"]:
            self.assertEqual(row["status"], "pass", row["app"])
            self.assertEqual(row["stderr_bytes"], 0, row["app"])
            self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [], row["app"])

    def test_librts_row_uses_multi_operation_path(self) -> None:
        summary = _load(SUMMARY)
        row = next(row for row in summary["rows"] if row["app"] == "librts_spatial_index")
        payload = _load(ROOT / row["stdout_path"])

        self.assertTrue(payload["multi_operation_native_used"])
        self.assertEqual(payload["mode"], "optix_aabb_index")
        self.assertEqual(payload["operation"], "all")
        self.assertEqual(payload["run_phases"]["query_sec"].keys(), {"multi_operation_packed_queries"})
        self.assertLess(payload["run_phases"]["query_median_sec"], 0.05)
        self.assertFalse(payload["native_engine_customization"])

    def test_gemini_review_exists_but_canonical_ratio_stays_in_json(self) -> None:
        self.assertTrue(GEMINI_REVIEW.exists())
        review = GEMINI_REVIEW.read_text(encoding="utf-8")
        focused = _load(GOAL3859_FOCUSED)

        self.assertIn("accept-with-boundary", review)
        self.assertAlmostEqual(focused["new_vs_cupy_ratio"], 1.0170780716207275)

    def test_report_records_boundary_and_review_limitation(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3864",
            "All ten rows passed",
            "multi_operation_native_used: true",
            "Gemini Flash",
            "should not be treated as canonical",
            "does not authorize",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()

