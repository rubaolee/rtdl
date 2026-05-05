from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1315V15OptixNativeCandidateCollectionAbiTest(unittest.TestCase):
    def test_native_optix_exports_app_name_free_collection_symbol(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")

        self.assertIn("struct RtdlPolygonPairCandidate", prelude)
        self.assertIn("uint32_t left_polygon_id", prelude)
        self.assertIn("uint32_t right_polygon_id", prelude)
        self.assertIn("rtdl_optix_collect_polygon_pair_candidates_bounded", prelude)
        self.assertIn('extern "C" int rtdl_optix_collect_polygon_pair_candidates_bounded', api)
        self.assertNotIn("rtdl_optix_run_polygon_set_jaccard_fast", api)

    def test_native_optix_collection_is_fail_closed_and_stable_ordered(self) -> None:
        source = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")

        self.assertIn("collect_polygon_pair_candidates_bounded_optix", source)
        self.assertIn("*overflowed_out = 1u", source)
        self.assertIn("candidates.size() > candidate_capacity", source)
        self.assertIn("std::sort(", source)
        self.assertIn("std::unique(", source)
        self.assertIn("run_lsi_optix(", source)
        self.assertIn("run_pip_optix(", source)

    def test_python_and_native_abi_names_remain_aligned(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        source_files = (
            ROOT / "src/native/optix/rtdl_optix_prelude.h",
            ROOT / "src/native/optix/rtdl_optix_api.cpp",
        )

        symbol = "rtdl_optix_collect_polygon_pair_candidates_bounded"
        self.assertIn(symbol, runtime)
        for path in source_files:
            self.assertIn(symbol, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
