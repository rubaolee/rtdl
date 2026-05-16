from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EMBREE_API = ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp"


class Goal2155EmbreeSegmentEndpointIntersectionSupplementTest(unittest.TestCase):
    def test_embree_segment_pair_path_supplements_shared_endpoint_hits(self) -> None:
        text = EMBREE_API.read_text(encoding="utf-8")

        for phrase in (
            "struct SegmentEndpointKey",
            "build_segment_endpoint_index",
            "append_shared_endpoint_segment_hits",
            "const SegmentEndpointIndex endpoint_index = build_segment_endpoint_index(right_segments);",
            "append_shared_endpoint_segment_hits(probe, right_segments, endpoint_index, query_rows);",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_supplement_runs_before_final_stable_sort(self) -> None:
        text = EMBREE_API.read_text(encoding="utf-8")
        supplement = text.index("append_shared_endpoint_segment_hits(probe, right_segments, endpoint_index, query_rows);")
        sort_after = text.index("std::stable_sort(", supplement)

        self.assertLess(supplement, sort_after)


if __name__ == "__main__":
    unittest.main()
