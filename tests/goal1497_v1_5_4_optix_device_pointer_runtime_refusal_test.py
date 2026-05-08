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

    def test_runtime_refuses_reserved_device_symbol_execution(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "reserved but not implemented"):
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


if __name__ == "__main__":
    unittest.main()
