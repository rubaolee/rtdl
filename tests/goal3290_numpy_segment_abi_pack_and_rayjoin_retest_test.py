from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3290_numpy_segment_abi_pack_and_rayjoin_retest_2026-06-04.md"
MICRO = ROOT / "docs" / "reports" / "goal3290_numpy_segment_abi_pack_final_micro_pod_2026-06-04.json"
COMPARISON = ROOT / "docs" / "reports" / "goal3290_rayjoin_same_slice_final_numpy_pack_pod_2026-06-04.json"
EMBREE_RUNTIME = ROOT / "src" / "rtdsl" / "embree_runtime.py"


class Goal3290NumpySegmentAbiPackAndRayjoinRetest(unittest.TestCase):
    def test_report_records_boundary_and_next_bottleneck(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("NumPy-owned structured buffer", text)
        self.assertIn("No native ABI changed", text)
        self.assertIn("enough to claim RTDL beats RayJoin", text)
        self.assertIn("Python record ingestion and record-to-column construction", text)
        self.assertIn("generic bulk", text)
        self.assertIn("segment-column ingestion/prepared-layout path", text)

    def test_runtime_uses_numpy_owned_abi_buffer(self) -> None:
        source = EMBREE_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("owner: object | None = None", source)
        self.assertIn("def _pack_segments_numpy_structured_arrays", source)
        self.assertIn("def _pack_segment_records_numpy_structured_one_pass", source)
        self.assertIn("ctypes.POINTER(_RtdlSegment)", source)
        self.assertIn('"itemsize": ctypes.sizeof(_RtdlSegment)', source)

    def test_micro_artifact_records_final_pack_split(self) -> None:
        data = json.loads(MICRO.read_text(encoding="utf-8"))

        self.assertEqual(data["schema_version"], "goal3290_numpy_segment_abi_pack_final_micro_v1")
        self.assertEqual(data["left_count"], 19987)
        self.assertEqual(data["record_owner_type"], "ndarray")
        self.assertEqual(data["column_owner_type"], "ndarray")
        self.assertLess(data["segment_columns_pack_ms"]["median"], 1.0)
        self.assertLess(data["record_pack_ms"]["median"], 20.0)
        self.assertGreater(data["segment_columns_prepare_ms"]["median"], data["segment_columns_pack_ms"]["median"])
        self.assertFalse(data["release_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["rtdl_beats_rayjoin_claim_authorized"])

    def test_comparison_artifact_keeps_claims_blocked_and_lsi_count_matching(self) -> None:
        data = json.loads(COMPARISON.read_text(encoding="utf-8"))

        self.assertEqual(data["status"], "pass_with_optimization_gap")
        for value in data["claim_boundary"].values():
            self.assertFalse(value)
        lsi = next(row for row in data["comparisons"] if row["workload"] == "lsi")
        self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(lsi["rtdl_count"], 269)
        self.assertEqual(lsi["rayjoin_visible_count"], 269)
        self.assertGreater(lsi["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertLess(data["rtdl"]["lsi"]["query_pack_ms"]["median"], 20.0)
        self.assertLess(data["rtdl"]["lsi"]["static_segment_pack_ms"]["median"], 8.0)


if __name__ == "__main__":
    unittest.main()
