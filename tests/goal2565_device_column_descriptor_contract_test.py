from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl import optix_runtime as optix_rt

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
COLUMNAR_PARTNER = ROOT / "src/rtdsl/columnar_partner.py"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2565_device_column_descriptor_contract_2026-05-23.md"


class Goal2565DeviceColumnDescriptorContractTest(unittest.TestCase):
    def test_device_column_descriptor_is_exported_and_compat_alias_remains(self) -> None:
        self.assertTrue(hasattr(rt, "DeviceColumnDescriptor"))
        self.assertIs(rt.PartnerResidentColumnHandoff, rt.DeviceColumnDescriptor)
        self.assertIn("DeviceColumnDescriptor", rt.__all__)
        self.assertIn("PartnerResidentColumnHandoff", rt.__all__)

    def test_record_set_fields_are_unified_device_column_descriptors(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        self.assertTrue(all(isinstance(field, rt.DeviceColumnDescriptor) for field in descriptor.fields))
        row_id = descriptor.fields[0]
        self.assertEqual(row_id.name, "row_id")
        self.assertEqual(row_id.logical_kind, "row_id")
        self.assertEqual(row_id.dtype_token, "int64")
        self.assertEqual(row_id.device_ptr, 0x1000)
        self.assertEqual(row_id.element_count, 3)
        self.assertEqual(row_id.stride_bytes, 8)
        self.assertEqual(row_id.host_materialization_boundary, rt.DEVICE_COLUMN_DESCRIPTOR_HOST_MATERIALIZATION_BOUNDARY)

    def test_legacy_handoff_constructor_shape_still_builds_descriptor(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        legacy = rt.PartnerResidentColumnHandoff(
            "row_id",
            "row_id",
            descriptor.fields[0].handoff,
        )
        self.assertIsInstance(legacy, rt.DeviceColumnDescriptor)
        self.assertEqual(legacy.dtype_token, "int64")
        self.assertEqual(legacy.device_ptr, 0x1000)
        self.assertEqual(legacy.element_count, 3)

    def test_metadata_records_stable_descriptor_fields(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        metadata = descriptor.to_metadata()
        first = metadata["fields"][0]
        self.assertEqual(first["dtype_token"], "int64")
        self.assertEqual(first["device_ptr"], 0x1000)
        self.assertEqual(first["element_count"], 3)
        self.assertEqual(first["stride_bytes"], 8)
        self.assertEqual(first["host_materialization_boundary"], "explicit_host_materialization_at_api_boundary")
        self.assertEqual(first["data_ptr"], 0x1000)

    def test_optix_encoder_consumes_descriptor_fields(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        fields_array, _keepalive = optix_rt._encode_partner_resident_device_payload_fields(descriptor)
        self.assertEqual(fields_array[0].element_count, descriptor.fields[0].element_count)
        self.assertEqual(fields_array[0].stride_bytes, descriptor.fields[0].stride_bytes)
        self.assertEqual(fields_array[0].device_ptr, descriptor.fields[0].device_ptr)

        runtime_text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("field.dtype_token", runtime_text)
        self.assertIn("field.element_count", runtime_text)
        self.assertIn("field.stride_bytes", runtime_text)
        self.assertIn("field.device_ptr", runtime_text)

    def test_report_records_unified_descriptor_contract(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2565", text)
        self.assertIn("DeviceColumnDescriptor", text)
        self.assertIn("PartnerResidentColumnHandoff remains a compatibility alias", text)
        self.assertIn("OptiX ctypes encoding now consumes descriptor fields", text)
        self.assertIn("no public zero-copy or speedup claim", text)


if __name__ == "__main__":
    unittest.main()
