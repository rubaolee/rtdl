import unittest

from rtdsl import optix_runtime


class Goal1497V154OptixDevicePointerRuntimeRefusalTest(unittest.TestCase):
    def test_runtime_names_reserved_device_symbol(self) -> None:
        self.assertEqual(
            optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL,
            "rtdl_optix_collect_k_bounded_i64_device",
        )
        self.assertEqual(
            optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_HOST_SYMBOL,
            "rtdl_optix_collect_k_bounded_i64",
        )

    def test_runtime_refuses_device_symbol_execution_without_explicit_opt_in(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "remains experimental"):
            optix_runtime.collect_k_bounded_i64_device_optix(
                candidate_rows_device_ptr=1,
                candidate_count=1,
                row_width=2,
                rows_out_device_ptr=2,
                row_capacity=1,
            )

    def test_runtime_validates_obvious_bad_device_pointer_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "row_width must be positive"):
            optix_runtime.collect_k_bounded_i64_device_optix(
                candidate_rows_device_ptr=1,
                candidate_count=1,
                row_width=0,
                rows_out_device_ptr=2,
                row_capacity=1,
            )
        with self.assertRaisesRegex(ValueError, "candidate_rows_device_ptr must be nonzero"):
            optix_runtime.collect_k_bounded_i64_device_optix(
                candidate_rows_device_ptr=0,
                candidate_count=1,
                row_width=2,
                rows_out_device_ptr=2,
                row_capacity=1,
            )
        with self.assertRaisesRegex(ValueError, "rows_out_device_ptr must be nonzero"):
            optix_runtime.collect_k_bounded_i64_device_optix(
                candidate_rows_device_ptr=1,
                candidate_count=1,
                row_width=2,
                rows_out_device_ptr=0,
                row_capacity=1,
            )

    def test_runtime_can_call_experimental_symbol_when_explicitly_enabled(self) -> None:
        class FakeSymbol:
            def __init__(self) -> None:
                self.argtypes = None
                self.restype = None
                self.calls = []

            def __call__(
                self,
                candidate_rows_device_ptr,
                candidate_count,
                row_width,
                rows_out_device_ptr,
                row_capacity,
                emitted_count_out,
                overflowed_out,
                h2d_transfers_out,
                d2h_transfers_out,
                internal_device_transfers_out,
                error_out,
                error_size,
            ):
                self.calls.append(
                    (
                        int(candidate_rows_device_ptr.value),
                        int(candidate_count.value),
                        int(row_width.value),
                        int(rows_out_device_ptr.value),
                        int(row_capacity.value),
                    )
                )
                emitted_count_out._obj.value = 3
                overflowed_out._obj.value = 0
                h2d_transfers_out._obj.value = 0
                d2h_transfers_out._obj.value = 2
                internal_device_transfers_out._obj.value = 0
                return 0

        class FakeLib:
            pass

        fake_symbol = FakeSymbol()
        fake_lib = FakeLib()
        setattr(fake_lib, optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL, fake_symbol)
        original_loader = optix_runtime._load_optix_library
        try:
            optix_runtime._load_optix_library = lambda: fake_lib
            result = optix_runtime.collect_k_bounded_i64_device_optix(
                candidate_rows_device_ptr=11,
                candidate_count=4,
                row_width=2,
                rows_out_device_ptr=22,
                row_capacity=3,
                allow_experimental=True,
            )
        finally:
            optix_runtime._load_optix_library = original_loader

        self.assertEqual(fake_symbol.calls, [(11, 4, 2, 22, 3)])
        self.assertEqual(result["valid_count"], 3)
        self.assertFalse(result["overflowed"])
        self.assertEqual(result["transfer_accounting"]["device_to_host_transfers_after_backend_execution"], 2)
        self.assertFalse(result["claim_flags"]["public_speedup_wording_authorized"])


if __name__ == "__main__":
    unittest.main()
