from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EMBREE_API = ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal4383_librts_large_aabb_2026-06-14.md"


class Goal4383LibrtsAabbFp32ContractTest(unittest.TestCase):
    def test_embree_aabb_native_predicate_declares_fp32_envelope_contract(self) -> None:
        source = EMBREE_API.read_text(encoding="utf-8")
        self.assertIn("Native AABB backends use fp32 envelope traversal", source)
        self.assertIn("static_cast<float>(box.min_x)", source)
        self.assertIn("std::nextafter(points[index].x", source)

    def test_large_librts_report_records_matching_fp32_counts(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("float32 envelope count: `6251`", report)
        self.assertIn("1M boxes x 1K queries", report)
        self.assertIn("Hot-query speedup", report)
        self.assertIn("13.39x", report)


if __name__ == "__main__":
    unittest.main()
