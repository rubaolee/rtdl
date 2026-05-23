import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2505_partner_resident_columnar_descriptor_contract_2026-05-22.md"
POD_TORCH_ARTIFACT = ROOT / "docs/reports/goal2505_partner_resident_torch_descriptor_pod_2026-05-22.json"


class FakeCudaColumn:
    def __init__(
        self,
        *,
        ptr: int,
        dtype: str,
        shape: tuple[int, ...] = (3,),
        strides: tuple[int, ...] | None = None,
        device_id: int = 0,
    ) -> None:
        self._ptr = int(ptr)
        self.dtype = dtype
        self.shape = shape
        self.strides = strides
        self._device_id = int(device_id)
        self.__cuda_array_interface__ = {
            "data": (self._ptr, False),
            "shape": shape,
            "strides": strides,
            "typestr": "<i8" if dtype == "int64" else "<f8",
            "version": 3,
        }

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, self._device_id)


def _record_set(**overrides):
    columns = {
        "region_id": FakeCudaColumn(ptr=0x2000, dtype="int64"),
        "revenue": FakeCudaColumn(ptr=0x3000, dtype="float64"),
    }
    columns.update(overrides.pop("columns", {}))
    return {
        "row_ids": overrides.pop("row_ids", FakeCudaColumn(ptr=0x1000, dtype="int64")),
        "columns": columns,
        **overrides,
    }


class Goal2505PartnerResidentColumnarDescriptorContractTest(unittest.TestCase):
    def test_public_partner_resident_descriptor_api_is_exported(self) -> None:
        self.assertEqual(rt.PARTNER_RESIDENT_COLUMNAR_BACKENDS, ("optix",))
        self.assertEqual(rt.PARTNER_RESIDENT_COLUMNAR_TRANSFER_MODE, "partner_resident_column_descriptor_only")
        self.assertTrue(hasattr(rt, "prepare_partner_resident_columnar_record_set"))

    def test_descriptor_contract_accepts_cuda_columns_without_native_execution_claim(self) -> None:
        handoff = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        self.assertIsInstance(handoff, rt.PartnerResidentColumnarRecordSet)
        self.assertEqual(handoff.row_count, 3)
        self.assertEqual(handoff.field_names, ("row_id", "region_id", "revenue"))
        self.assertEqual(handoff.device_type, "cuda")
        self.assertEqual(handoff.device_id, 0)
        metadata = handoff.to_metadata()
        self.assertEqual(metadata["transfer_mode"], "partner_resident_column_descriptor_only")
        self.assertFalse(metadata["native_execution_authorized"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["row_id_uniqueness_validated"])
        self.assertEqual(metadata["fields"][0]["data_ptr"], 0x1000)

    def test_descriptor_contract_fails_closed_for_non_optix_backend(self) -> None:
        with self.assertRaisesRegex(ValueError, "only backend='optix'"):
            rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="embree")

    def test_descriptor_contract_requires_matching_lengths(self) -> None:
        with self.assertRaisesRegex(ValueError, "matching lengths"):
            rt.prepare_partner_resident_columnar_record_set(
                _record_set(columns={"revenue": FakeCudaColumn(ptr=0x3000, dtype="float64", shape=(2,))})
            )

    def test_descriptor_contract_requires_same_cuda_device(self) -> None:
        with self.assertRaisesRegex(ValueError, "same CUDA device"):
            rt.prepare_partner_resident_columnar_record_set(
                _record_set(columns={"revenue": FakeCudaColumn(ptr=0x3000, dtype="float64", device_id=1)})
            )

    def test_descriptor_contract_requires_contiguous_columns(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be contiguous"):
            rt.prepare_partner_resident_columnar_record_set(
                _record_set(columns={"revenue": FakeCudaColumn(ptr=0x3000, dtype="float64", strides=(16,))})
            )

    def test_lowering_plan_points_to_native_execution_as_next_target(self) -> None:
        plan = rt.plan_columnar_aggregate_lowering("optix")
        self.assertEqual(
            plan.next_engine_target,
            "optix_partner_resident_columnar_payload_native_execution",
        )

    def test_report_records_descriptor_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("partner-resident columnar descriptor", text)
        self.assertIn("descriptor-only", text)
        self.assertIn("native execution remains blocked", text)
        self.assertIn("true zero-copy remains blocked", text)
        self.assertIn("9 tests OK", text)

    def test_pod_torch_artifact_records_real_cuda_partner_descriptor(self) -> None:
        payload = json.loads(POD_TORCH_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["backend"], "optix")
        self.assertEqual(payload["transfer_mode"], "partner_resident_column_descriptor_only")
        self.assertEqual(payload["device"], "cuda:0")
        self.assertIn("torch", payload["source_protocols"])
        self.assertEqual(payload["row_count"], 4)
        self.assertEqual(payload["field_names"], ["row_id", "region_id", "ship_year", "revenue"])
        self.assertFalse(payload["native_execution_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertGreater(payload["fields"][0]["data_ptr"], 0)


if __name__ == "__main__":
    unittest.main()
