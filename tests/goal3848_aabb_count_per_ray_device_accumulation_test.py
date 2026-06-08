from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3848_aabb_count_payload_local_accumulation_2026-06-08.md"


class Goal3848AabbCountPayloadLocalAccumulationTest(unittest.TestCase):
    def test_count_only_aabb_path_uses_second_payload_register(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("unsigned int p1 = 0u;", text)
        self.assertIn("optixGetPayload_1", text)
        self.assertIn("optixSetPayload_1(count + 1u)", text)
        self.assertIn("p0, p1);", text)
        self.assertIn("nullptr, 2).release();", text)

    def test_row_collection_still_reserves_rows_with_atomic_counter(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("if (params.collect_rows == 0u)", text)
        self.assertIn("const unsigned long long row_index = atomicAdd(params.hit_count, 1ULL);", text)
        self.assertIn("if (row_index < params.row_capacity)", text)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        flattened = " ".join(text.split())

        for phrase in (
            "Goal3848",
            "AABB_INDEX_QUERY_2D",
            "one global `atomicAdd` per accepted hit",
            "one aggregate add per ray",
            "not LibRTS-specific",
            "does not authorize release action",
        ):
            self.assertIn(phrase, flattened)


if __name__ == "__main__":
    unittest.main()
