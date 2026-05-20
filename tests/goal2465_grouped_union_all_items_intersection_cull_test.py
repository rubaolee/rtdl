from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
GOAL2463_SUMMARY = ROOT / "docs" / "reports" / "goal2463_grouped_union_all_items_pod" / "summary.json"
GOAL2465_SUMMARY = ROOT / "docs" / "reports" / "goal2465_grouped_union_all_items_intersection_cull_pod" / "summary.json"


class Goal2465GroupedUnionAllItemsIntersectionCullTest(unittest.TestCase):
    def test_all_items_intersection_culls_hits_anyhit_would_ignore(self) -> None:
        core = OPTIX_CORE.read_text(encoding="utf-8")
        start = core.index("extern \"C\" __global__ void __intersection__frn3d_grouped_union_isect()")
        end = core.index("extern \"C\" __global__ void __anyhit__frn3d_grouped_union_anyhit()", start)
        intersection = core[start:end]

        self.assertIn("const uint32_t source = params.query_index_offset + qidx", intersection)
        self.assertIn("params.all_predicate != 0u && prim <= source", intersection)
        self.assertIn("return;", intersection)
        self.assertNotIn("dbscan", intersection.lower())

    def test_pod_evidence_improves_dense_all_items_row(self) -> None:
        previous = json.loads(GOAL2463_SUMMARY.read_text(encoding="utf-8"))
        current = json.loads(GOAL2465_SUMMARY.read_text(encoding="utf-8"))
        previous_by_count = {int(row["point_count"]): row for row in previous["summaries"]}
        current_by_count = {int(row["point_count"]): row for row in current["summaries"]}

        self.assertTrue(current["tiny_smoke"]["matches_reference"])
        row_65536 = current_by_count[65536]
        previous_65536 = previous_by_count[65536]
        self.assertTrue(row_65536["signatures_match"])
        self.assertEqual(row_65536["repeat_rows"][1]["grouped_predicate_mode"], "all_items_true_no_fallback_candidates")
        self.assertLess(row_65536["tail_median_sec"], previous_65536["tail_median_sec"] * 0.94)
        self.assertLess(
            row_65536["grouped_native_tail_median_sec"],
            previous_65536["grouped_native_tail_median_sec"] * 0.94,
        )


if __name__ == "__main__":
    unittest.main()
