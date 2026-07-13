from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "history" / "internal_docs" / "docs_reports" / "goal2990_v2_6_neutral_partner_handoff_2026-06-01.md"


class _FakeCupyInt64Column:
    __module__ = "cupy._core.core"
    dtype = "int64"
    shape = (3,)
    strides = None

    def __init__(self, ptr: int = 0x299000) -> None:
        self._ptr = int(ptr)

    def __dlpack__(self):
        return object()

    def __dlpack_device__(self):
        return (2, 0)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (self._ptr, False),
            "version": 3,
        }


class _FakeCupyFloat64Column(_FakeCupyInt64Column):
    dtype = "float64"

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (self._ptr, False),
            "version": 3,
        }


class _FakeNumbaDeviceInt64Column:
    __module__ = "numba.cuda.cudadrv.devicearray"
    dtype = "int64"
    shape = (3,)

    def __init__(self, ptr: int = 0x29A000) -> None:
        self._ptr = int(ptr)

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (self._ptr, False),
            "version": 3,
        }

    def copy_to_host(self):  # matches the shape of real Numba device arrays.
        return [0, 1, 2]


class _FakeTorchCudaColumn(_FakeCupyInt64Column):
    __module__ = "torch"
    requires_grad = False


class _FakeHostArray:
    __module__ = "numpy"
    dtype = "int64"
    shape = (3,)
    strides = None

    @property
    def __array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (0x29B000, False),
            "version": 3,
        }


class Goal2990V26NeutralPartnerHandoffTest(unittest.TestCase):
    def test_cupy_columns_plan_and_prepare_without_torch_carrier(self) -> None:
        packet = rt.prepare_v2_6_neutral_partner_handoff(
            {
                "group_ids": _FakeCupyInt64Column(),
                "values": _FakeCupyFloat64Column(0x299800),
            },
            partner="cupy",
        )
        validation = rt.validate_v2_6_neutral_partner_handoff(packet)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(rt.V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION, packet["contract_version"])
        self.assertEqual("cupy", packet["selected_partner"])
        self.assertTrue(packet["partner_choice_user_owned"])
        self.assertTrue(packet["all_columns_device_resident"])
        self.assertTrue(packet["copy_or_borrow_status_runtime_observed"])
        self.assertFalse(packet["torch_conversion_used"])
        self.assertFalse(packet["torch_carrier_used"])
        self.assertEqual(0, packet["torch_source_column_count"])
        self.assertEqual(2, packet["runtime_observed_descriptor_count"])
        self.assertTrue(packet["all_leases_completed"])
        self.assertFalse(packet["true_zero_copy_claim_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertEqual(
            ("handoff_begin", "continuation_complete"),
            tuple(packet["lease_records"][0]["event_log"]),
        )
        self.assertEqual("cupy", packet["column_records"][0]["source_protocol"])

    def test_numba_cuda_array_interface_columns_use_neutral_descriptor(self) -> None:
        packet = rt.prepare_v2_6_neutral_partner_handoff(
            {
                "group_ids": _FakeNumbaDeviceInt64Column(),
            },
            partner="numba",
        )
        record = packet["column_records"][0]

        self.assertEqual("accept", rt.validate_v2_6_neutral_partner_handoff(packet)["status"])
        self.assertEqual("numba", packet["selected_partner"])
        self.assertEqual("cuda_array_interface", record["source_protocol"])
        self.assertEqual("borrowed_device_pointer_unmeasured", record["transfer_status"])
        self.assertTrue(record["direct_device_pointer_observed"])
        self.assertFalse(record["torch_conversion_used"])
        self.assertFalse(record["torch_carrier_used"])

    def test_torch_source_is_rejected_for_cupy_numba_neutral_path(self) -> None:
        packet = rt.plan_v2_6_neutral_partner_handoff(
            {"group_ids": _FakeTorchCudaColumn()},
            partner="numba",
        )

        self.assertEqual("reject", packet["status"])
        self.assertGreater(packet["torch_source_column_count"], 0)
        self.assertIn("torch source protocol is forbidden", " ".join(packet["errors"]))
        with self.assertRaisesRegex(ValueError, "torch source protocol is forbidden"):
            rt.prepare_v2_6_neutral_partner_handoff(
                {"group_ids": _FakeTorchCudaColumn()},
                partner="numba",
            )

    def test_host_columns_fail_closed_when_device_resident_required(self) -> None:
        packet = rt.plan_v2_6_neutral_partner_handoff(
            {"group_ids": _FakeHostArray()},
            partner="cupy",
        )

        self.assertEqual("reject", packet["status"])
        self.assertFalse(packet["all_columns_device_resident"])
        self.assertIn("device-resident CUDA column is required", " ".join(packet["errors"]))

    def test_symbols_are_importable_but_not_star_exports(self) -> None:
        for name in (
            "V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION",
            "plan_v2_6_neutral_partner_handoff",
            "prepare_v2_6_neutral_partner_handoff",
            "validate_v2_6_neutral_partner_handoff",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2990",
            "v2.6 neutral partner handoff",
            "CuPy",
            "Numba",
            "without torch carrier",
            "not true-zero-copy wording",
            "not a release authorization",
            "pod",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
