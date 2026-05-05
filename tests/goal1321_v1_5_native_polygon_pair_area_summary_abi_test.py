from __future__ import annotations

import unittest
from pathlib import Path

from examples import rtdl_polygon_set_jaccard as jaccard_app
import rtdsl as rt


class Goal1321V15NativePolygonPairAreaSummaryAbiTest(unittest.TestCase):
    def test_native_abi_symbol_is_declared_and_exported(self) -> None:
        abi = Path("src/native/oracle/rtdl_oracle_abi.h").read_text(encoding="utf-8")
        api = Path("src/native/oracle/rtdl_oracle_api.cpp").read_text(encoding="utf-8")

        self.assertIn("struct RtdlPolygonPairAreaSummary", abi)
        self.assertIn("rtdl_native_reduce_polygon_pair_exact_area_summary", abi)
        self.assertIn("RTDL_ORACLE_EXPORT int rtdl_native_reduce_polygon_pair_exact_area_summary", api)
        self.assertNotIn("rtdl_native_run_polygon_set_jaccard_fast", api)

    def test_native_area_summary_matches_existing_jaccard_refinement(self) -> None:
        case = jaccard_app.make_authored_polygon_set_jaccard_case(copies=2)
        candidate_pairs = {(1, 10), (2, 11), (101, 110), (102, 111)}

        summary = rt.reduce_polygon_pair_exact_area_summary_for_candidates(
            case["left"],
            case["right"],
            candidate_pairs,
        )
        legacy_rows = rt.refine_polygon_set_jaccard_for_pairs(
            case["left"],
            case["right"],
            candidate_pairs,
        )

        self.assertEqual(summary["intersection_area"], legacy_rows[0]["intersection_area"])
        self.assertEqual(summary["left_area"], legacy_rows[0]["left_area"])
        self.assertEqual(summary["right_area"], legacy_rows[0]["right_area"])
        self.assertEqual(summary["union_area"], legacy_rows[0]["union_area"])
        self.assertEqual(summary["overlap_pair_count"], 4)

    def test_jaccard_app_uses_generic_native_area_summary_for_score(self) -> None:
        case = jaccard_app.make_authored_polygon_set_jaccard_case(copies=2)
        candidate_pairs = {(1, 10), (2, 11), (101, 110), (102, 111)}

        rows = jaccard_app._native_jaccard_rows_for_candidates(
            case["left"],
            case["right"],
            candidate_pairs,
        )

        self.assertEqual(rows[0]["intersection_area"], 10)
        self.assertEqual(rows[0]["left_area"], 26)
        self.assertEqual(rows[0]["right_area"], 22)
        self.assertEqual(rows[0]["union_area"], 38)
        self.assertEqual(rows[0]["jaccard_similarity"], 10 / 38)


if __name__ == "__main__":
    unittest.main()
