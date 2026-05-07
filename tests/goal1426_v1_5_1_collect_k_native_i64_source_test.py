from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1426V151CollectKNativeI64SourceTest(unittest.TestCase):
    def test_embree_declares_and_defines_generic_i64_collector(self) -> None:
        prelude = (ROOT / "src/native/embree/rtdl_embree_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/embree/rtdl_embree_api.cpp").read_text(encoding="utf-8")

        self.assertIn("int rtdl_embree_collect_k_bounded_i64(", prelude)
        self.assertIn("RTDL_EMBREE_EXPORT int rtdl_embree_collect_k_bounded_i64(", api)
        self.assertIn("const int64_t* candidate_rows", api)
        self.assertIn("int64_t* rows_out", api)

    def test_optix_declares_and_defines_generic_i64_collector(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_bounded_i64(", prelude)
        self.assertIn('extern "C" int rtdl_optix_collect_k_bounded_i64(', api)
        self.assertIn("const int64_t* candidate_rows", api)
        self.assertIn("int64_t* rows_out", api)

    def test_native_i64_collectors_are_canonical_and_fail_closed(self) -> None:
        for relative_path in (
            "src/native/embree/rtdl_embree_api.cpp",
            "src/native/optix/rtdl_optix_api.cpp",
        ):
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(relative_path=relative_path):
                self.assertIn("std::vector<std::vector<int64_t>> rows", source)
                self.assertIn("std::sort(rows.begin(), rows.end())", source)
                self.assertIn("std::unique(rows.begin(), rows.end())", source)
                self.assertIn("*emitted_count_out = rows.size()", source)
                self.assertIn("if (rows.size() > row_capacity)", source)
                self.assertIn("*overflowed_out = 1u", source)
                self.assertIn("sizeof(int64_t) * row_width", source)

    def test_native_i64_collectors_guard_invalid_buffers(self) -> None:
        for relative_path in (
            "src/native/embree/rtdl_embree_api.cpp",
            "src/native/optix/rtdl_optix_api.cpp",
        ):
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(relative_path=relative_path):
                self.assertIn("row_width == 0", source)
                self.assertIn("candidate_rows", source)
                self.assertIn("candidate_count != 0", source)
                self.assertIn("rows_out", source)
                self.assertIn("row_capacity != 0", source)
                self.assertIn("COLLECT_K_BOUNDED row buffer size overflow", source)

    def test_contract_records_source_symbols_but_keeps_stable_blocked(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertTrue(contract["native_source_symbols_present"])
        self.assertTrue(contract["native_binary_validation_present"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertIn("built_symbol_validation_evidence", contract)


if __name__ == "__main__":
    unittest.main()
