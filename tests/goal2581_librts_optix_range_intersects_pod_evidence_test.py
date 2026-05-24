from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "docs/reports/goal2581_librts_optix_range_intersects_path_2026-05-24.json"
REPORT_MD = ROOT / "docs/reports/goal2581_librts_optix_range_intersects_path_2026-05-24.md"


class LibRTSOptixRangeIntersectsPodEvidenceTest(unittest.TestCase):
    def test_report_records_all_three_native_aabb_operations(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["implementation"]["primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(
            payload["implementation"]["supported_operations"],
            ["point_contains", "range_contains", "range_intersects"],
        )
        self.assertFalse(payload["implementation"]["app_specific_native_code"])
        self.assertTrue(payload["implementation"]["box_query_buffers_build_query_gas"])

    def test_paperlike_counts_match_authors_code_for_range_intersects(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        expected = {
            "uniform_10k_1k_paperlike": 250,
            "uniform_100k_1k_paperlike": 2477,
            "uniform_1m_1k_paperlike": 25079,
        }
        for case, count in expected.items():
            row = payload["rtdl_optix_prepared_query_results"][case]
            self.assertEqual(row["counts"]["range_intersects"], count)
            self.assertLess(row["median_vs_authors_ratio"]["range_intersects"], 1.0)

    def test_markdown_keeps_claim_boundary_explicit(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("No native symbol or kernel name contains `LibRTS`", text)
        self.assertIn("not exact paper", text)
        self.assertIn("artifact datasets", text)
        self.assertIn("Public speedup wording still requires final review/consensus", text)


if __name__ == "__main__":
    unittest.main()
