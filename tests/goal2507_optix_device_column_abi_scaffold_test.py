from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2507_optix_device_column_abi_scaffold_2026-05-22.md"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"


class Goal2507OptixDeviceColumnAbiScaffoldTest(unittest.TestCase):
    def test_native_header_declares_device_column_payload_struct(self) -> None:
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        self.assertIn("struct RtdlDevicePayloadField", prelude)
        self.assertIn("kRtdlDevicePayloadDeviceCuda", prelude)
        self.assertIn("kRtdlDevicePayloadDtypeInt64", prelude)
        self.assertIn("kRtdlDevicePayloadDtypeUint32", prelude)
        self.assertIn("kRtdlDevicePayloadDtypeFloat64", prelude)
        self.assertIn("uint64_t device_ptr", prelude)
        self.assertIn("size_t stride_bytes", prelude)

    def test_native_api_declares_and_defines_fail_closed_symbol(self) -> None:
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        api = OPTIX_API.read_text(encoding="utf-8")
        symbol = "rtdl_optix_columnar_payload_create_from_device_columns"
        self.assertIn(symbol, prelude)
        self.assertIn(f'extern "C" int {symbol}', api)
        self.assertIn("fail-closed ABI scaffold", api)
        self.assertIn("partner-resident columnar native execution is not implemented", api)

    def test_python_requirements_still_block_native_execution(self) -> None:
        requirements = rt.partner_resident_columnar_native_execution_requirements()
        self.assertEqual(requirements["status"], "blocked_pending_optix_device_column_abi")
        self.assertIn(
            "Device-column OptiX symbol is a fail-closed scaffold only.",
            requirements["current_blockers"],
        )
        self.assertIn(
            "rtdl_optix_columnar_payload_create_from_device_columns",
            requirements["required_native_symbols"],
        )

    def test_report_records_scaffold_not_execution(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2507", text)
        self.assertIn("RtdlDevicePayloadField", text)
        self.assertIn("fail-closed ABI scaffold", text)
        self.assertIn("native execution remains unauthorized", text)
        self.assertIn("No speedup, zero-copy, SQL, or DBMS claim is authorized", text)


if __name__ == "__main__":
    unittest.main()
