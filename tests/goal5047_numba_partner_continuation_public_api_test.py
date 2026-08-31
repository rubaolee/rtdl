from __future__ import annotations

import unittest
from unittest import mock

import numpy as np

import rtdsl as rt


class _FakeCudaColumn:
    dtype = "uint32"
    shape = (4,)

    def __init__(self, ptr: int, typestr: str = "<u4") -> None:
        self._ptr = int(ptr)
        self._typestr = typestr

    @property
    def __cuda_array_interface__(self):
        return {
            "shape": self.shape,
            "typestr": self._typestr,
            "data": (self._ptr, False),
            "version": 3,
            "device": 0,
        }


class Goal5047NumbaPartnerContinuationPublicApiTest(unittest.TestCase):
    def test_public_symbols_and_contract_are_exported(self) -> None:
        for name in (
            "NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION",
            "NUMBA_PARTNER_CONTINUATION_API_MATURITY",
            "NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS",
            "NumbaPartnerContinuationPlan",
            "NumbaPartnerContinuationResult",
            "describe_numba_partner_continuation_contract",
            "numba_partner_continuation",
            "run_numba_partner_continuation",
            "validate_numba_partner_continuation_contract",
        ):
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__)

        contract = rt.describe_numba_partner_continuation_contract()
        validation = rt.validate_numba_partner_continuation_contract(contract)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("DeviceColumnBuffer", contract["input_surface"])
        self.assertTrue(contract["host_fallback_requires_explicit_opt_in"])
        self.assertFalse(contract["replaces_rt_traversal"])
        self.assertFalse(contract["public_speedup_claim_authorized"])
        self.assertIn(rt.NUMBA_UINT32_EQUAL_MASK_OPERATION, contract["public_operations"])

    def test_plan_requires_device_column_buffer_and_explicit_bindings(self) -> None:
        buffer = rt.device_column_buffer(
            {"values": _FakeCudaColumn(0x504700)},
            producer="generic_uint32_values",
            producer_consumer_stream_ordering="same_stream",
            native_device_column_output_proven_on_hardware=True,
        )
        plan = rt.numba_partner_continuation(
            operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
            input_buffer=buffer,
            input_bindings={"values": "values"},
            scalar_inputs={"target": 7},
        )

        metadata = plan.to_metadata()
        self.assertEqual(rt.NUMBA_UINT32_EQUAL_MASK_OPERATION, metadata["operation"])
        self.assertEqual("same_stream", metadata["stream_ordering"])
        self.assertTrue(metadata["stream_synchronization_proven"])
        self.assertTrue(metadata["device_resident_candidate"])
        self.assertFalse(metadata["materializes_host_rows_for_bridge"])
        self.assertFalse(metadata["host_fallback_used"])
        self.assertFalse(metadata["replaces_rt_traversal"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

        with self.assertRaisesRegex(ValueError, "DeviceColumnBuffer"):
            rt.numba_partner_continuation(
                operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
                input_buffer={"values": [1, 2, 3]},
                input_bindings={"values": "values"},
            )
        with self.assertRaisesRegex(ValueError, "requires explicit input bindings"):
            rt.numba_partner_continuation(
                operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
                input_buffer=buffer,
                input_bindings={},
            )
        with self.assertRaisesRegex(ValueError, "is missing"):
            rt.numba_partner_continuation(
                operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
                input_buffer=buffer,
                input_bindings={"values": "absent"},
            )

    def test_host_materialized_buffer_requires_explicit_fallback(self) -> None:
        host_buffer = rt.device_column_buffer(
            {"values": np.asarray([1, 2, 3], dtype=np.uint32)},
            producer="host_values",
            source_mode="host_rows_to_columns_bridge",
            materializes_host_rows_for_bridge=True,
        )
        with self.assertRaisesRegex(ValueError, "allow_host_fallback"):
            rt.numba_partner_continuation(
                operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
                input_buffer=host_buffer,
                input_bindings={"values": "values"},
            )

        plan = rt.numba_partner_continuation(
            operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
            input_buffer=host_buffer,
            input_bindings={"values": "values"},
            allow_host_fallback=True,
        )
        self.assertTrue(plan.to_metadata()["allow_host_fallback"])
        self.assertTrue(plan.to_metadata()["host_fallback_used"])

    def test_run_skips_cleanly_when_cuda_unavailable(self) -> None:
        buffer = rt.device_column_buffer(
            {"values": _FakeCudaColumn(0x504740)},
            producer="generic_uint32_values",
        )
        plan = rt.numba_partner_continuation(
            operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
            input_buffer=buffer,
            input_bindings={"values": "values"},
            scalar_inputs={"target": 1},
        )
        with mock.patch("rtdsl.numba_partner_api._numba_ops.numba_partner_available", return_value=False):
            result = rt.run_numba_partner_continuation(plan)

        self.assertEqual("skipped_cuda_unavailable", result.status)
        self.assertFalse(result.to_metadata()["public_speedup_claim_authorized"])
        self.assertFalse(result.to_metadata()["true_zero_copy_claim_authorized"])

    def test_run_binds_columns_and_scalar_options_to_existing_runner(self) -> None:
        buffer = rt.device_column_buffer(
            {"values": _FakeCudaColumn(0x504780)},
            producer="generic_uint32_values",
        )
        plan = rt.numba_partner_continuation(
            operation=rt.NUMBA_UINT32_EQUAL_MASK_OPERATION,
            input_buffer=buffer,
            input_bindings={"values": "values"},
            scalar_inputs={"target": 42},
            options={"block_size": 128},
        )
        fake_output = _FakeCudaColumn(0x5047C0)
        with mock.patch("rtdsl.numba_partner_api._numba_ops.numba_partner_available", return_value=True):
            with mock.patch(
                "rtdsl.numba_partner_api._RUNNERS",
                {
                    rt.NUMBA_UINT32_EQUAL_MASK_OPERATION: mock.Mock(
                        return_value={
                            "outputs": {"mask": fake_output},
                            "elapsed_sec": 0.01,
                            "host_column_materialization_used": False,
                        }
                    )
                },
            ) as runners:
                result = rt.run_numba_partner_continuation(plan)

        runner = runners[rt.NUMBA_UINT32_EQUAL_MASK_OPERATION]
        runner.assert_called_once_with(values=buffer.columns["values"], target=42, block_size=128)
        self.assertEqual("completed", result.status)
        self.assertEqual(("mask",), result.to_metadata()["outputs"])
        self.assertFalse(result.to_metadata()["host_fallback_used"])

    def test_unsupported_operations_fail_closed(self) -> None:
        buffer = rt.device_column_buffer(
            {"values": _FakeCudaColumn(0x5047F0)},
            producer="generic_values",
        )
        with self.assertRaisesRegex(ValueError, "unsupported public Numba"):
            rt.numba_partner_continuation(
                operation="rayjoin_overlay_kernel",
                input_buffer=buffer,
                input_bindings={"values": "values"},
            )


if __name__ == "__main__":
    unittest.main()
