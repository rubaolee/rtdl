from __future__ import annotations

import unittest
from unittest import mock

import numpy as np

import rtdsl as rt


class _FakeCudaColumn:
    def __init__(self, ptr: int, typestr: str, shape: tuple[int, ...] = (4,)) -> None:
        self._ptr = int(ptr)
        self.shape = shape
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


class Goal5045PublicDeviceOrderByContractTest(unittest.TestCase):
    def test_public_symbols_and_contract_are_exported_without_device_group_by(self) -> None:
        for name in (
            "DEVICE_ORDER_BY_CONTRACT_VERSION",
            "DEVICE_ORDER_BY_API_MATURITY",
            "DEVICE_ORDER_BY_SUPPORTED_SIGNATURES",
            "DeviceOrderByResult",
            "describe_device_order_by_contract",
            "device_order_by",
            "device_order_by_reference_i64_f64_i64_i64",
            "validate_device_order_by_contract",
        ):
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__)

        self.assertFalse(hasattr(rt, "device_group_by"))
        self.assertNotIn("device_group_by", rt.__all__)
        contract = rt.describe_device_order_by_contract()
        validation = rt.validate_device_order_by_contract(contract)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual(("i64_f64_i64_i64_lex",), contract["supported_signatures"])
        self.assertEqual(("cpu_reference", "native_cuda"), contract["supported_backends"])
        self.assertFalse(contract["device_group_by_public_claim_authorized"])
        self.assertFalse(contract["public_speedup_claim_authorized"])
        self.assertFalse(contract["true_zero_copy_claim_authorized"])

    def test_cpu_reference_matches_numpy_lexsort_and_uses_explicit_tie_key(self) -> None:
        key0 = np.asarray([2, 1, 1, 2, 1], dtype=np.int64)
        key1 = np.asarray([0.5, 0.2, 0.2, 0.1, 0.2], dtype=np.float64)
        key2 = np.asarray([0, 5, 5, 0, 4], dtype=np.int64)
        tie = np.asarray([0, 2, 1, 3, 4], dtype=np.int64)

        result = rt.device_order_by_reference_i64_f64_i64_i64(
            key0=key0,
            key1=key1,
            key2=key2,
            order_key=tie,
            key_names=("edge", "distance", "tie", "original_order"),
        )

        expected = np.lexsort((tie, key2, key1, key0)).astype(np.int64, copy=False)
        np.testing.assert_array_equal(expected, result.order_indices)
        np.testing.assert_array_equal(key0[expected], result.sorted_columns["edge"])
        self.assertEqual("cpu_reference", result.backend)
        self.assertFalse(result.to_metadata()["stable_sort_claim_authorized"])
        self.assertTrue(result.to_metadata()["explicit_final_tie_key_required"])

    def test_generic_device_order_by_rejects_unsupported_shapes_and_dtypes(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly four keys"):
            rt.device_order_by({"a": [1], "b": [2]}, keys=("a", "b"))
        with self.assertRaisesRegex(ValueError, "unsupported device_order_by signature"):
            rt.device_order_by({"a": [1]}, keys=("a", "b", "c", "d"), signature="i32_lex")
        with self.assertRaisesRegex(ValueError, "must be int64"):
            rt.device_order_by(
                {
                    "a": np.asarray([1], dtype=np.int32),
                    "b": np.asarray([1.0], dtype=np.float64),
                    "c": np.asarray([1], dtype=np.int64),
                    "d": np.asarray([0], dtype=np.int64),
                },
                keys=("a", "b", "c", "d"),
            )
        with self.assertRaisesRegex(ValueError, "identical lengths"):
            rt.device_order_by(
                {
                    "a": np.asarray([1, 2], dtype=np.int64),
                    "b": np.asarray([1.0], dtype=np.float64),
                    "c": np.asarray([1], dtype=np.int64),
                    "d": np.asarray([0], dtype=np.int64),
                },
                keys=("a", "b", "c", "d"),
            )

    def test_native_cuda_path_requires_device_column_buffer_and_calls_generic_helper(self) -> None:
        buffer = rt.device_column_buffer(
            {
                "edge": _FakeCudaColumn(0x504500, "<i8"),
                "distance": _FakeCudaColumn(0x504580, "<f8"),
                "tie": _FakeCudaColumn(0x504600, "<i8"),
                "order": _FakeCudaColumn(0x504680, "<i8"),
            },
            producer="generic_sort_keys",
            producer_consumer_stream_ordering="same_stream",
            native_device_column_output_proven_on_hardware=True,
        )

        with mock.patch(
            "rtdsl.optix_runtime.run_cuda_lexsort_i64_f64_i64_i64_device",
            return_value={
                "backend": "native_thrust_lexsort_i64_f64_i64_i64",
                "row_count": 4,
                "device_resident": True,
            },
        ) as native:
            result = rt.device_order_by(
                buffer,
                keys=("edge", "distance", "tie", "order"),
                backend="native_cuda",
            )

        native.assert_called_once_with(
            edge_key_device_ptr=0x504500,
            dist_key_device_ptr=0x504580,
            tie_key_device_ptr=0x504600,
            order_key_device_ptr=0x504680,
            count=4,
        )
        self.assertEqual("native_cuda", result.backend)
        self.assertEqual(4, result.row_count)
        metadata = result.to_metadata()
        self.assertEqual("native_thrust_lexsort_i64_f64_i64_i64", metadata["metadata"]["backend"])
        self.assertTrue(metadata["metadata"]["device_resident_candidate"])
        self.assertFalse(metadata["metadata"]["materializes_host_rows_for_bridge"])
        self.assertTrue(metadata["metadata"]["input_key_columns_mutated_in_place"])
        self.assertFalse(metadata["device_group_by_public_claim_authorized"])

    def test_native_cuda_rejects_host_materialized_or_non_device_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires a DeviceColumnBuffer"):
            rt.device_order_by(
                {
                    "edge": np.asarray([1], dtype=np.int64),
                    "distance": np.asarray([1.0], dtype=np.float64),
                    "tie": np.asarray([1], dtype=np.int64),
                    "order": np.asarray([0], dtype=np.int64),
                },
                keys=("edge", "distance", "tie", "order"),
                backend="native_cuda",
            )

        host_buffer = rt.device_column_buffer(
            {
                "edge": np.asarray([1], dtype=np.int64),
                "distance": np.asarray([1.0], dtype=np.float64),
                "tie": np.asarray([1], dtype=np.int64),
                "order": np.asarray([0], dtype=np.int64),
            },
            producer="host_keys",
            source_mode="host_rows_to_columns_bridge",
            materializes_host_rows_for_bridge=True,
        )
        with self.assertRaisesRegex(ValueError, "device-resident"):
            rt.device_order_by(
                host_buffer,
                keys=("edge", "distance", "tie", "order"),
                backend="native_cuda",
            )


if __name__ == "__main__":
    unittest.main()
