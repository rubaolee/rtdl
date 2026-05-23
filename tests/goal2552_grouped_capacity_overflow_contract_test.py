from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2552_grouped_capacity_overflow_contract_2026-05-23.md"

WITH_CAPACITY_SYMBOLS = (
    "rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity",
    "rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity",
    "rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity",
    "rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity",
    "rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity",
    "rtdl_optix_columnar_device_payload_grouped_stats_i64_with_capacity",
)

WITH_CAPACITY_CONSTANTS = (
    "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL",
    "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_WITH_CAPACITY_SYMBOL",
    "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MIN_I64_WITH_CAPACITY_SYMBOL",
    "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MAX_I64_WITH_CAPACITY_SYMBOL",
    "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_COUNT_I64_WITH_CAPACITY_SYMBOL",
    "OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_STATS_I64_WITH_CAPACITY_SYMBOL",
)


def _function_block(source: str, name: str) -> str:
    match = re.search(rf"{re.escape(name)}\s*\((.*?)\)\s*(?:;|\{{)", source, re.S)
    if match is None:
        raise AssertionError(f"missing function block for {name}")
    return match.group(1)


class Goal2552GroupedCapacityOverflowContractTest(unittest.TestCase):
    def test_public_optix_capacity_abi_exposes_overflowed_out(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for symbol in WITH_CAPACITY_SYMBOLS:
            for source in (prelude, api):
                block = _function_block(source, symbol)
                self.assertIn("size_t group_capacity", block)
                self.assertIn("uint32_t* overflowed_out", block)
                self.assertLess(block.index("row_count_out"), block.index("overflowed_out"))
                self.assertLess(block.index("overflowed_out"), block.index("error_out"))

    def test_native_grouped_capacity_hit_sets_overflow_without_partial_rows(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("*overflowed_out = 0u;", workloads)
        self.assertIn("*overflowed_out = 1u;", workloads)
        self.assertIn("if (*overflowed_out != 0u) {\n        return;\n    }", workloads)
        self.assertIn(
            "throw std::runtime_error(\"device-column grouped execution requires dense non-negative group keys below group_capacity\")",
            workloads,
        )

    def test_python_ctypes_and_wrappers_fail_closed_on_overflow(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        register_start = runtime.index("def _register_argtypes")
        register_section = runtime[
            runtime.index(WITH_CAPACITY_CONSTANTS[0], register_start) :
            runtime.index('symbol = _find_optional_backend_symbol(lib, "rtdl_optix_columnar_payload_destroy")')
        ]
        for constant in WITH_CAPACITY_CONSTANTS:
            self.assertIn(constant, register_section)
        self.assertEqual(register_section.count("ctypes.POINTER(ctypes.c_uint32),"), 5)
        self.assertIn("_raise_on_partner_resident_grouped_capacity_overflow", runtime)
        self.assertIn("overflowed explicit group_capacity", runtime)
        self.assertGreaterEqual(runtime.count("ctypes.byref(overflowed),"), 6)

    def test_report_records_boundary_and_followup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2552", text)
        self.assertIn("fail-closed", text)
        self.assertIn("broader `RtdlDb*` and `DbScan*` rename", text)
        self.assertIn("not a public release", text)


if __name__ == "__main__":
    unittest.main()
