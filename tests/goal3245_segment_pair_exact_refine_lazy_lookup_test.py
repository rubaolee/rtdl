from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3245SegmentPairExactRefineLazyLookupTest(unittest.TestCase):
    def test_segment_pair_refine_uses_lazy_id_lookup(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        for function_name in (
            "finalize_segment_pair_intersection_rows",
            "count_segment_pair_intersection_rows",
        ):
            start = text.index(f"static {'void' if function_name.startswith('finalize') else 'size_t'} {function_name}")
            end = text.index("static std::vector<uint64_t> collect_segment_first_hits_optix", start)
            if function_name.startswith("finalize"):
                end = text.index("static size_t count_segment_pair_intersection_rows", start)
            body = text[start:end]
            self.assertIn("bool left_lookup_ready = false", body)
            self.assertIn("bool local_right_lookup_ready = false", body)
            self.assertIn("auto find_left_by_id", body)
            self.assertIn("auto find_right_by_id", body)
            self.assertIn("if (gpu_row.left_index < left_count && gpu_row.right_index < right_count)", body)

            indexed_path = body[
                body.index("if (gpu_row.left_index < left_count && gpu_row.right_index < right_count)"):
                body.index("} else {", body.index("if (gpu_row.left_index < left_count && gpu_row.right_index < right_count)"))
            ]
            self.assertIn("left_seg = &left[gpu_row.left_index]", indexed_path)
            self.assertIn("right_seg = &right[gpu_row.right_index]", indexed_path)
            self.assertNotIn("find_left_by_id", indexed_path)
            self.assertNotIn("find_right_by_id", indexed_path)

    def test_exactness_and_dedupe_guards_remain_present(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        for phrase in (
            "std::unordered_set<uint64_t> seen_pairs",
            "if (seen_pairs.find(pair_key) != seen_pairs.end())",
            "if (!exact_segment_intersection(*left_seg, *right_seg, &ix, &iy))",
            "seen_pairs.insert(pair_key)",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
