import inspect
import unittest

from rtdsl.optix_runtime import OptixNativeDevicePairColumnOutput


class Goal3329OptixDevicePairColumnsCupyAdapterTest(unittest.TestCase):
    def test_public_cupy_adapter_exists_and_uses_field_names(self):
        self.assertTrue(hasattr(OptixNativeDevicePairColumnOutput, "as_cupy_columns"))
        source = inspect.getsource(OptixNativeDevicePairColumnOutput.as_cupy_columns)
        self.assertIn("self.field_names[0]", source)
        self.assertIn("self.field_names[1]", source)
        self.assertIn("self.left_ids_device_ptr", source)
        self.assertIn("self.right_ids_device_ptr", source)

    def test_zero_copy_boundary_remains_false(self):
        output = OptixNativeDevicePairColumnOutput(
            library=object(),
            owner=object(),
            left_ids_device_ptr=0,
            right_ids_device_ptr=0,
            row_count=0,
            capacity=0,
            candidate_event_count=0,
            overflow=False,
            device_ordinal=0,
            traversal_seconds=0.0,
            native_symbol="test_symbol",
        )
        self.assertFalse(output.true_zero_copy_authorized)
        self.assertFalse(output.exact_relation_witness_rows_materialized)

    def test_private_wrapper_guards_overflow_and_missing_pointers(self):
        source = inspect.getsource(OptixNativeDevicePairColumnOutput._cupy_column)
        self.assertIn("cannot wrap an overflowed device pair-column stream", source)
        self.assertIn("does not own CUDA columns", source)
        self.assertIn("UnownedMemory", source)


if __name__ == "__main__":
    unittest.main()
