from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
STATUS = (
    "source_symbols_present_python_adapter_routed_embree_optix_adapter_parity_ok_"
    "binary_validation_ok_generic_abi_parity_ok_stable_review_pending"
)


class Goal1427V151CollectKPythonI64AdapterRouteTest(unittest.TestCase):
    def test_python_i64_adapter_canonicalizes_and_marks_binary_validation_pending(self) -> None:
        result = rt.adapt_native_i64_rows_to_collect_k_bounded_result(
            ((2, 20), (1, 10), (2, 20)),
            capacity=2,
            row_width=2,
            backend="embree",
            source_symbol="rtdl_embree_collect_polygon_pair_candidates_bounded",
        )

        self.assertEqual(result["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(result["backend"], "embree")
        self.assertTrue(result["native_i64_adapter"])
        self.assertEqual(
            result["native_source_symbol"],
            "rtdl_embree_collect_polygon_pair_candidates_bounded",
        )
        self.assertEqual(result["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(result["valid_count"], 2)
        self.assertFalse(result["binary_symbol_validation_present"])
        self.assertIn("production wrapper use of built Embree/OptiX generic symbols", result["claim_boundary"])

    def test_python_i64_adapter_keeps_fail_closed_overflow(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "COLLECT_K_BOUNDED overflowed capacity 1; emitted 2",
        ):
            rt.adapt_native_i64_rows_to_collect_k_bounded_result(
                ((2, 20), (1, 10)),
                capacity=1,
                row_width=2,
                backend="optix",
                source_symbol="rtdl_optix_collect_polygon_pair_candidates_bounded",
            )

    def test_embree_and_optix_polygon_wrappers_route_through_python_i64_adapter(self) -> None:
        for relative_path, backend, source_symbol in (
            (
                "src/rtdsl/embree_runtime.py",
                "embree",
                "rtdl_embree_collect_polygon_pair_candidates_bounded",
            ),
            (
                "src/rtdsl/optix_runtime.py",
                "optix",
                "rtdl_optix_collect_polygon_pair_candidates_bounded",
            ),
        ):
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            function_start = source.index(f"def collect_polygon_pair_candidates_bounded_{backend}(")
            function_end = source.index("\ndef ", function_start + 1)
            function_source = source[function_start:function_end]
            with self.subTest(relative_path=relative_path):
                self.assertIn(
                    "adapt_native_i64_rows_to_collect_k_bounded_result(",
                    function_source,
                )
                self.assertIn(f'backend="{backend}"', function_source)
                self.assertIn(f'source_symbol="{source_symbol}"', function_source)
                self.assertIn('"binary_symbol_validation_present"', function_source)
                self.assertIn('"native_emitted_count"', function_source)
                self.assertIn('"overflow_policy": row_buffer["overflow_policy"]', function_source)
                self.assertIn("built generic native symbol validation", function_source)
                self.assertNotIn("collect_k_bounded_rows(candidate_pairs", function_source)

    def test_contract_records_adapter_route_but_keeps_binary_validation_pending(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(
            contract["status"],
            STATUS,
        )
        self.assertTrue(contract["native_source_symbols_present"])
        self.assertTrue(contract["native_binary_validation_present"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertEqual(
            contract["required_adapter_work"],
            (),
        )


if __name__ == "__main__":
    unittest.main()
