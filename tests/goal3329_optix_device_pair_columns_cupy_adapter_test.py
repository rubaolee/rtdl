import inspect
import json
from pathlib import Path
import unittest

from rtdsl.optix_runtime import OptixNativeDevicePairColumnOutput


ROOT = Path(__file__).resolve().parents[1]
POD_SMOKE = ROOT / "docs" / "reports" / "goal3329_optix_device_pair_columns_cupy_adapter_pod_smoke_2026-06-04.json"


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

    def test_pod_smoke_wrapped_real_pair_columns(self):
        data = json.loads(POD_SMOKE.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3329.pod_cupy_pair_column_smoke.v1")
        self.assertEqual(data["field_names"], ["point_id", "shape_id"])
        self.assertEqual(data["row_count"], 6)
        self.assertEqual(set(data["sample"]), {"point_id", "shape_id"})
        self.assertFalse(data["true_zero_copy_authorized"])
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
