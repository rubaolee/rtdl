from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1317V15EmbreeNativeCandidateCollectionAbiTest(unittest.TestCase):
    def test_native_embree_exports_same_contract_collection_symbol(self) -> None:
        prelude = (ROOT / "src/native/embree/rtdl_embree_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/embree/rtdl_embree_api.cpp").read_text(encoding="utf-8")

        self.assertIn("struct RtdlPolygonPairCandidate", prelude)
        self.assertIn("uint32_t left_polygon_id", prelude)
        self.assertIn("uint32_t right_polygon_id", prelude)
        self.assertIn("rtdl_embree_collect_polygon_pair_candidates_bounded", prelude)
        self.assertIn("RTDL_EMBREE_EXPORT int rtdl_embree_collect_polygon_pair_candidates_bounded", api)
        self.assertNotIn("rtdl_embree_run_polygon_set_jaccard_fast", api)

    def test_native_embree_collection_is_fail_closed_and_stable_ordered(self) -> None:
        api = (ROOT / "src/native/embree/rtdl_embree_api.cpp").read_text(encoding="utf-8")

        self.assertIn("polygon_pair_flags(left_polygon, right_polygon", api)
        self.assertIn("*overflowed_out = 1u", api)
        self.assertIn("candidates.size() > candidate_capacity", api)
        self.assertIn("std::sort(", api)
        self.assertIn("std::unique(", api)
        self.assertIn("std::memcpy(candidates_out", api)

    def test_python_and_native_abi_names_remain_aligned(self) -> None:
        runtime = (ROOT / "src/rtdsl/embree_runtime.py").read_text(encoding="utf-8")
        symbol = "rtdl_embree_collect_polygon_pair_candidates_bounded"

        self.assertIn(symbol, runtime)
        self.assertIn(
            symbol,
            (ROOT / "src/native/embree/rtdl_embree_prelude.h").read_text(encoding="utf-8"),
        )
        self.assertIn(
            symbol,
            (ROOT / "src/native/embree/rtdl_embree_api.cpp").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
