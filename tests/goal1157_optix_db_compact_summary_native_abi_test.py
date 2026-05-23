from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1157OptixDbCompactSummaryNativeAbiTest(unittest.TestCase):
    def test_prelude_declares_compact_summary_abi(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")

        self.assertIn("struct RtdlColumnCompactSummaryRequest", prelude)
        self.assertIn("struct RtdlColumnCompactSummaryResult", prelude)
        self.assertIn("using RtdlDbCompactSummaryRequest = RtdlColumnCompactSummaryRequest;", prelude)
        self.assertIn("using RtdlDbCompactSummaryResult = RtdlColumnCompactSummaryResult;", prelude)
        self.assertIn("kRtdlColumnCompactSummaryScanCount", prelude)
        self.assertIn("kRtdlColumnCompactSummaryGroupedCount", prelude)
        self.assertIn("kRtdlColumnCompactSummaryGroupedSum", prelude)
        self.assertIn("kRtdlDbCompactSummaryScanCount", prelude)
        self.assertIn("kRtdlDbCompactSummaryGroupedCount", prelude)
        self.assertIn("kRtdlDbCompactSummaryGroupedSum", prelude)
        self.assertIn("rtdl_optix_columnar_payload_compact_summary_batch", prelude)
        self.assertIn("rtdl_optix_columnar_compact_summary_results_destroy", prelude)
        self.assertIn("size_t result_count", prelude)

    def test_api_exports_batch_and_frees_nested_rows(self) -> None:
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")

        self.assertIn('extern "C" int rtdl_optix_columnar_payload_compact_summary_batch', api)
        self.assertIn("run_columnar_multi_predicate_scan_count_optix_prepared", api)
        self.assertIn("run_columnar_grouped_count_optix_prepared", api)
        self.assertIn("run_columnar_grouped_sum_optix_prepared", api)
        self.assertIn("rtdl_optix_fill_columnar_compact_summary_phase", api)
        self.assertIn("std::free(results[index].count_rows)", api)
        self.assertIn("std::free(results[index].sum_rows)", api)
        self.assertIn("std::calloc(results.size(), sizeof(RtdlColumnCompactSummaryResult))", api)

    def test_python_runtime_configures_optional_native_symbols(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")

        self.assertIn("class _RtdlDbCompactSummaryRequest", runtime)
        self.assertIn("class _RtdlDbCompactSummaryResult", runtime)
        self.assertIn("_RtdlColumnCompactSummaryRequest = _RtdlDbCompactSummaryRequest", runtime)
        self.assertIn("_RtdlColumnCompactSummaryResult = _RtdlDbCompactSummaryResult", runtime)
        self.assertIn("rtdl_optix_columnar_payload_compact_summary_batch", runtime)
        self.assertIn("rtdl_optix_columnar_compact_summary_results_destroy", runtime)
        self.assertIn("destroy_compact_summary_batch_results(results_ptr, result_count)", runtime)
        self.assertIn("ctypes.POINTER(_RtdlColumnCompactSummaryRequest)", runtime)
        self.assertIn("ctypes.POINTER(ctypes.POINTER(_RtdlColumnCompactSummaryResult))", runtime)


if __name__ == "__main__":
    unittest.main()
