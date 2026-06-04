from __future__ import annotations

from pathlib import Path
import unittest


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3288_segment_id_pack_boundary_hardening_2026-06-04.md"
EMBREE = ROOT / "src" / "rtdsl" / "embree_runtime.py"
COLUMNS = ROOT / "src" / "rtdsl" / "segment_columns.py"


class Goal3288SegmentIdPackBoundaryHardeningTest(unittest.TestCase):
    def test_report_records_claude_finding_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Claude's Goal3286 review", text)
        self.assertIn("preventing silent wraparound", text)
        self.assertIn("No native ABI changed", text)

    def test_runtime_keeps_ids_wide_then_validates_before_native_pack(self) -> None:
        embree = EMBREE.read_text(encoding="utf-8")
        columns = COLUMNS.read_text(encoding="utf-8")

        self.assertIn("dtype=_np.int64", embree)
        self.assertIn("dtype=np.int64", columns)
        self.assertIn("def _segment_id_to_packed_u32", embree)
        self.assertIn("segment ids must fit the uint32 packed segment ABI", embree)


if __name__ == "__main__":
    unittest.main()
