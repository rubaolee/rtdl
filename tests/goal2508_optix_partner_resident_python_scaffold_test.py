from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl import optix_runtime as optix_rt

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2508_optix_partner_resident_python_scaffold_2026-05-22.md"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"


class Goal2508OptixPartnerResidentPythonScaffoldTest(unittest.TestCase):
    def test_python_scaffold_entrypoint_is_exported(self) -> None:
        self.assertEqual(
            rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL,
            "rtdl_optix_columnar_payload_create_from_device_columns",
        )
        self.assertIn("prepare_optix_partner_resident_columnar_record_set", rt.__all__)
        self.assertTrue(hasattr(rt, "prepare_optix_partner_resident_columnar_record_set"))

    def test_python_entrypoint_fails_closed_before_backend_load_by_default(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        with self.assertRaisesRegex(RuntimeError, "native_execution_allowed=False"):
            rt.prepare_optix_partner_resident_columnar_record_set(descriptor)
        with self.assertRaisesRegex(RuntimeError, "allow_scaffold_probe=True"):
            rt.prepare_optix_partner_resident_columnar_record_set(_record_set())

    def test_runtime_can_encode_device_payload_fields_without_copying_values(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        fields_array, keepalive = optix_rt._encode_partner_resident_device_payload_fields(descriptor)
        self.assertEqual(len(fields_array), 3)
        self.assertEqual(fields_array[0].name, b"row_id")
        self.assertEqual(fields_array[0].kind, 1)
        self.assertEqual(fields_array[0].dtype, 1)
        self.assertEqual(fields_array[0].device_type, 1)
        self.assertEqual(fields_array[0].device_id, 0)
        self.assertEqual(fields_array[0].element_count, 3)
        self.assertEqual(fields_array[0].stride_bytes, 8)
        self.assertEqual(fields_array[0].device_ptr, 0x1000)
        self.assertEqual(fields_array[2].name, b"revenue")
        self.assertEqual(fields_array[2].kind, 2)
        self.assertEqual(fields_array[2].dtype, 3)
        self.assertEqual(fields_array[2].device_ptr, 0x3000)
        self.assertEqual(len(keepalive), 3)

    def test_runtime_registers_optional_device_symbol_argtypes(self) -> None:
        text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("class _RtdlDevicePayloadField", text)
        self.assertIn("OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL", text)
        self.assertIn("ctypes.POINTER(_RtdlDevicePayloadField)", text)
        self.assertIn("allow_scaffold_probe=True", text)

    def test_report_records_python_scaffold_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2508", text)
        self.assertIn("prepare_optix_partner_resident_columnar_record_set", text)
        self.assertIn("fails before backend load by default", text)
        self.assertIn("scaffold probe only", text)
        self.assertIn("native execution remains unauthorized", text)


if __name__ == "__main__":
    unittest.main()
