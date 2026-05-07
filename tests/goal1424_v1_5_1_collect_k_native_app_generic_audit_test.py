from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1424V151CollectKNativeAppGenericAuditTest(unittest.TestCase):
    def test_audit_keeps_stable_promotion_blocked_until_native_abi_is_generic(self) -> None:
        audit = rt.validate_v1_5_1_collect_k_bounded_native_app_generic_audit()

        self.assertEqual(
            audit["status"],
            "blocked_for_stable_promotion_native_abi_still_polygon_pair_specific",
        )
        self.assertTrue(audit["contract_layer_app_generic"])
        self.assertTrue(audit["python_reference_app_generic"])
        self.assertTrue(audit["result_validator_app_generic"])
        self.assertFalse(audit["native_engine_fully_app_agnostic"])
        self.assertTrue(audit["stable_promotion_blocked"])
        self.assertEqual(
            audit["public_docs_candidate_status_remains"],
            "documented_experimental_public_candidate",
        )

    def test_audit_records_current_polygon_pair_specific_native_symbols(self) -> None:
        audit = rt.validate_v1_5_1_collect_k_bounded_native_app_generic_audit()
        observed = audit["observed_native_symbols"]

        self.assertEqual(
            observed,
            (
                {
                    "backend": "embree",
                    "path": "src/native/embree/rtdl_embree_api.cpp",
                    "symbol": "rtdl_embree_collect_polygon_pair_candidates_bounded",
                    "path_exists": True,
                    "symbol_present": True,
                    "app_specific_reason": "polygon_pair_specific_native_entrypoint",
                },
                {
                    "backend": "optix",
                    "path": "src/native/optix/rtdl_optix_api.cpp",
                    "symbol": "rtdl_optix_collect_polygon_pair_candidates_bounded",
                    "path_exists": True,
                    "symbol_present": True,
                    "app_specific_reason": "polygon_pair_specific_native_entrypoint",
                },
            ),
        )
        self.assertEqual(audit["missing_expected_symbols"], ())

    def test_native_symbol_files_still_contain_polygon_pair_specific_names(self) -> None:
        for _backend, relative_path, symbol in (
            rt.V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_AUDIT_SYMBOLS
        ):
            with self.subTest(symbol=symbol):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(symbol, text)
                self.assertIn("polygon_pair", symbol)

    def test_required_next_steps_define_generic_native_abi_work(self) -> None:
        audit = rt.validate_v1_5_1_collect_k_bounded_native_app_generic_audit()

        self.assertEqual(
            audit["required_next_steps"],
            rt.V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_REQUIRED_NEXT_STEPS,
        )
        self.assertIn("add_embree_optix_generic_abi_parity_tests", audit["required_next_steps"])
        self.assertIn("rerun_optix_polygon_pair_adapter_parity_on_gpu_pod", audit["required_next_steps"])
        self.assertIn("validate_generic_native_symbols_in_built_libraries", audit["required_next_steps"])
        self.assertIn("rerun_3_ai_stable_promotion_review", audit["required_next_steps"])


if __name__ == "__main__":
    unittest.main()
