from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3292_one_pass_segment_column_builder_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3292_one_pass_segment_column_builder_micro_pod_2026-06-04.json"
SEGMENT_COLUMNS = ROOT / "src" / "rtdsl" / "segment_columns.py"


class Goal3292OnePassSegmentColumnBuilderTest(unittest.TestCase):
    def test_source_uses_one_pass_builder_for_records(self) -> None:
        source = SEGMENT_COLUMNS.read_text(encoding="utf-8")

        self.assertIn("def _segment_record_arrays_one_pass", source)
        self.assertIn("arrays = _segment_record_arrays_one_pass(record_tuple, np)", source)
        self.assertIn("for index, record in enumerate(record_tuple):", source)
        self.assertIn("np.empty(count, dtype=np.int64)", source)
        self.assertIn("np.empty(count, dtype=np.float64)", source)

    def test_report_records_goal3290_to_goal3292_timing_delta(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("five separate `np.fromiter(...)` passes", text)
        self.assertIn("32.108 ms", text)
        self.assertIn("14.289 ms", text)
        self.assertIn("sub-ms time", text)
        self.assertIn("native prepared segment layout", text)

    def test_pod_artifact_preserves_boundary_and_improves_prepare_phase(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema_version"], "goal3292_one_pass_segment_column_builder_micro_v1")
        self.assertEqual(data["left_count"], 19987)
        self.assertLess(data["segment_columns_prepare_ms"]["median"], 20.0)
        self.assertLess(data["segment_columns_pack_ms"]["median"], 1.0)
        self.assertLess(data["segment_columns_total_ms"]["median"], 20.0)
        self.assertEqual(data["packed_owner_type"], "ndarray")
        self.assertFalse(data["release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["rtdl_beats_rayjoin_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
