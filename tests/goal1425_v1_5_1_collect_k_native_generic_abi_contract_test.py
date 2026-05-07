from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1425V151CollectKNativeGenericAbiContractTest(unittest.TestCase):
    def test_contract_defines_app_name_free_backend_symbols_without_implementation_claim(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(contract["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(
            contract["status"],
            "source_symbols_present_python_adapter_routed_embree_parity_ok_optix_pending_binary_validation_pending",
        )
        self.assertTrue(contract["native_source_symbols_present"])
        self.assertFalse(contract["native_binary_validation_present"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertTrue(contract["app_name_free"])
        self.assertEqual(
            contract["backend_symbols"],
            (
                "rtdl_embree_collect_k_bounded_i64",
                "rtdl_optix_collect_k_bounded_i64",
            ),
        )

    def test_symbols_are_not_app_specific(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        for symbol in contract["backend_symbols"]:
            lowered = symbol.lower()
            with self.subTest(symbol=symbol):
                self.assertIn("collect_k_bounded", lowered)
                for forbidden in contract["forbidden_symbol_substrings"]:
                    self.assertNotIn(forbidden, lowered)

    def test_prototypes_use_generic_i64_row_buffers(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        for prototype in contract["prototypes"]:
            with self.subTest(prototype=prototype):
                self.assertIn("const int64_t* candidate_rows", prototype)
                self.assertIn("size_t candidate_count", prototype)
                self.assertIn("size_t row_width", prototype)
                self.assertIn("int64_t* rows_out", prototype)
                self.assertIn("size_t row_capacity", prototype)
                self.assertIn("size_t* emitted_count_out", prototype)
                self.assertIn("uint32_t* overflowed_out", prototype)
                self.assertIn("char* error_out", prototype)
                self.assertIn("size_t error_size", prototype)

    def test_contract_preserves_fail_closed_collection_policy(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(contract["input_layout"], "row_major_int64_candidate_id_rows")
        self.assertEqual(contract["output_layout"], rt.V1_5_1_COLLECT_K_BOUNDED_RESULT_LAYOUT)
        self.assertEqual(contract["capacity_unit"], "candidate_id_rows")
        self.assertEqual(contract["overflow_policy"], rt.V1_5_1_COLLECT_K_BOUNDED_OVERFLOW_POLICY)
        self.assertEqual(contract["failure_mode"], "fail_closed_overflow")
        self.assertFalse(contract["partial_result_on_overflow_allowed"])

    def test_contract_names_required_adapter_work_before_stable_review(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(
            contract["required_adapter_work"],
            (
                "prove_existing_polygon_pair_optix_parity_is_unchanged",
                "validate_embree_optix_generic_i64_symbols_in_built_libraries",
            ),
        )
        self.assertIn("linux_embree_required", contract["post_adapter_parity_evidence"])
        self.assertIn("linux_optix_required_not_accepted", contract["post_adapter_parity_evidence"])
        self.assertIn("native source-level ABI implementation step only", contract["claim_boundary"])
        self.assertIn("does not claim built Embree or OptiX library validation", contract["claim_boundary"])
        self.assertIn("Python generic i64 adapter", contract["claim_boundary"])
        self.assertIn("Post-adapter Embree polygon-pair parity is accepted", contract["claim_boundary"])
        self.assertIn("OptiX post-adapter parity remains pending", contract["claim_boundary"])
        self.assertIn("not through validated built native generic symbols yet", contract["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
