from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
STATUS = (
    "source_symbols_present_python_adapter_routed_embree_optix_adapter_parity_ok_"
    "binary_validation_ok_generic_abi_parity_ok_production_wrapper_generic_symbol_route_ok_"
    "stable_review_pending"
)


class _FakeNativeCollectKSymbol:
    def __init__(self) -> None:
        self.argtypes = None
        self.restype = None

    def __call__(
        self,
        candidate_rows,
        candidate_count,
        row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        error_out,
        error_size,
    ) -> int:
        rows = []
        for row_index in range(int(candidate_count)):
            start = row_index * int(row_width)
            rows.append(
                tuple(int(candidate_rows[start + column]) for column in range(int(row_width)))
            )
        normalized = tuple(sorted(set(rows)))
        emitted_count_out._obj.value = len(normalized)
        overflowed_out._obj.value = 1 if len(normalized) > int(row_capacity) else 0
        if overflowed_out._obj.value:
            return 0
        for row_index, row in enumerate(normalized):
            for column, value in enumerate(row):
                rows_out[row_index * int(row_width) + column] = value
        return 0


class _FakeLibrary:
    def __init__(self) -> None:
        self.rtdl_embree_collect_k_bounded_i64 = _FakeNativeCollectKSymbol()


class Goal1432V151CollectKProductionWrapperGenericSymbolTest(unittest.TestCase):
    def test_contract_records_production_wrapper_generic_symbol_route(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(contract["status"], STATUS)
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertEqual(
            contract["production_wrapper_generic_symbol_evidence"],
            (
                "docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_linux_embree_2026-05-06.md",
                "docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_pod_optix_2026-05-06.md",
            ),
        )
        self.assertIn("production wrappers now route native candidate rows", contract["claim_boundary"])
        self.assertIn("stable primitive wording", contract["claim_boundary"])

    def test_native_generic_symbol_helper_canonicalizes_and_marks_binary_route(self) -> None:
        result = rt.collect_native_i64_rows_with_backend_symbol(
            ((2, 20), (1, 10), (2, 20)),
            capacity=2,
            row_width=2,
            backend="embree",
            library=_FakeLibrary(),
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            candidate_source_symbol="rtdl_embree_collect_shape_pair_candidates_bounded",
        )

        self.assertEqual(result["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(result["native_source_symbol"], "rtdl_embree_collect_k_bounded_i64")
        self.assertEqual(result["native_generic_symbol"], "rtdl_embree_collect_k_bounded_i64")
        self.assertEqual(
            result["native_candidate_source_symbol"],
            "rtdl_embree_collect_shape_pair_candidates_bounded",
        )
        self.assertFalse(result["native_i64_adapter"])
        self.assertTrue(result["binary_symbol_validation_present"])
        self.assertIn("production Python wrapper", result["claim_boundary"])
        self.assertIn("does not authorize stable promotion", result["claim_boundary"])

    def test_native_generic_symbol_helper_keeps_fail_closed_overflow(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "COLLECT_K_BOUNDED overflowed capacity 1; emitted 2",
        ):
            rt.collect_native_i64_rows_with_backend_symbol(
                ((2, 20), (1, 10), (2, 20)),
                capacity=1,
                row_width=2,
                backend="embree",
                library=_FakeLibrary(),
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="rtdl_embree_collect_shape_pair_candidates_bounded",
            )

    def test_embree_and_optix_wrappers_call_generic_native_symbols(self) -> None:
        for relative_path, backend in (
            ("src/rtdsl/embree_runtime.py", "embree"),
            ("src/rtdsl/optix_runtime.py", "optix"),
        ):
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            function_start = source.index(f"def collect_polygon_pair_candidates_bounded_{backend}(")
            function_end = source.index("\ndef ", function_start + 1)
            function_source = source[function_start:function_end]
            with self.subTest(backend=backend):
                self.assertIn("collect_native_i64_rows_with_backend_symbol(", function_source)
                self.assertIn(f'symbol_name="rtdl_{backend}_collect_k_bounded_i64"', function_source)
                self.assertIn(
                    f'candidate_source_symbol="rtdl_{backend}_collect_shape_pair_candidates_bounded"',
                    function_source,
                )
                self.assertIn('"native_generic_symbol"', function_source)
                self.assertIn('"native_candidate_source_symbol"', function_source)
                self.assertNotIn("adapt_native_i64_rows_to_collect_k_bounded_result(", function_source)

    def test_reports_and_consensus_accept_only_narrow_route_claim(self) -> None:
        summary = (
            ROOT
            / "docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_route_2026-05-06.md"
        ).read_text(encoding="utf-8")
        gemini = (
            ROOT
            / "docs/reports/gemini_goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_review_2026-05-06.md"
        ).read_text(encoding="utf-8")
        claude = (
            ROOT
            / "docs/reports/claude_goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_unavailable_2026-05-06.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs/reports/two_ai_goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_consensus_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPTED for the measured production-wrapper route package", summary)
        self.assertIn("pass=4, fail=0, skipped=0", summary)
        self.assertIn("does not authorize stable `COLLECT_K_BOUNDED` primitive promotion", summary)
        self.assertIn("ACCEPT", gemini)
        self.assertIn("No Claude acceptance is claimed", claude)
        self.assertIn("2-AI Consensus", consensus)
        self.assertIn("Gemini external review: accepted", consensus)
        self.assertIn("Stable `COLLECT_K_BOUNDED` promotion remains blocked", consensus)


if __name__ == "__main__":
    unittest.main()
