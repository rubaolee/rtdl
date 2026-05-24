from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/reports/goal2578_librts_paperlike_uniform_authors_pod_evidence_2026-05-24.json"
REPORT = ROOT / "docs/reports/goal2578_librts_paperlike_uniform_authors_pod_evidence_2026-05-24.md"


class LibRTSPaperlikeAuthorsPodEvidenceTest(unittest.TestCase):
    def test_artifact_records_paperlike_parameters_and_query_times(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["paperlike_parameters"]["max_box_width"], 0.005)
        self.assertEqual(artifact["paperlike_parameters"]["max_query_width"], 0.005)
        row = artifact["results"]["uniform_1m_1k_paperlike"]
        self.assertEqual(row["rtspatial_results"]["point_contains"], 6251)
        self.assertLess(row["rtspatial_query_ms"]["point_contains"], 1.0)
        self.assertLess(row["rtspatial_query_ms"]["range_contains"], 1.0)
        self.assertLess(row["rtspatial_query_ms"]["range_intersects"], 1.0)

    def test_10k_row_matches_cpu_reference(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        row = artifact["results"]["uniform_10k_1k_paperlike"]
        self.assertTrue(row["cpu_reference_counts_available"])
        self.assertTrue(row["all_counts_match_cpu_reference"])
        raw = json.loads(
            (ROOT / artifact["raw_summaries"]["uniform_10k_1k_paperlike"]).read_text(encoding="utf-8")
        )
        for operation, expected in raw["cpu_counts"].items():
            self.assertEqual(raw["rtspatial"][operation]["results"], expected)
            self.assertTrue(raw["rtspatial"][operation]["matches_cpu_reference"])

    def test_report_records_selectivity_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("highly workload/selectivity dependent", text)
        self.assertIn("Not exact paper artifact reproduction", text)
        self.assertIn("Not RTDL performance evidence", text)


if __name__ == "__main__":
    unittest.main()
