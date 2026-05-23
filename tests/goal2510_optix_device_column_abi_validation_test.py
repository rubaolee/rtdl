import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2510_optix_device_column_abi_validation_2026-05-22.md"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
POD_ARTIFACT = ROOT / "docs/reports/goal2510_optix_partner_resident_validation_probe_pod_2026-05-22.json"


class Goal2510OptixDeviceColumnAbiValidationTest(unittest.TestCase):
    def test_native_scaffold_validates_device_column_abi_before_fail_closed(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        self.assertIn("device-column payload requires at least one field", api)
        self.assertIn("device-column payload fields must use CUDA device pointers", api)
        self.assertIn("device-column payload fields require non-zero device_ptr", api)
        self.assertIn("device-column payload field length must match row_count", api)
        self.assertIn("device-column payload fields must live on the same CUDA device", api)
        self.assertIn("device-column payload fields must be contiguous", api)
        self.assertIn("device-column payload requires a row_id field", api)
        self.assertIn("device-column descriptors validated", api)

    def test_public_native_header_names_db_and_device_column_kind_constants(self) -> None:
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        self.assertIn("kRtdlDbKindInt64", prelude)
        self.assertIn("kRtdlDbKindFloat64", prelude)
        self.assertIn("kRtdlDbKindBool", prelude)
        self.assertIn("kRtdlDbKindText", prelude)
        self.assertIn("kRtdlDevicePayloadDtypeUint32", prelude)

    def test_report_records_validation_not_execution(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2510", text)
        self.assertIn("ABI validation", text)
        self.assertIn("device-column descriptors validated", text)
        self.assertIn("still fail-closed", text)
        self.assertIn("native execution remains unauthorized", text)

    def test_pod_artifact_reaches_native_validation_then_fails_closed(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["probe_status"], "expected_fail_closed")
        self.assertTrue(payload["cuda_available"])
        self.assertIn("device-column descriptors validated", payload["error"])
        self.assertIn("native execution is not implemented", payload["error"])
        self.assertEqual(payload["descriptor"]["device"], "cuda:0")
        self.assertEqual(payload["descriptor"]["row_count"], 4)


if __name__ == "__main__":
    unittest.main()
