from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NUMBA_RUNTIME = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
TYPED_STREAM_ADAPTER = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
BH_APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4052_numba_presegmented_vector_sum_2026-06-08.md"


def _numba_cuda_available() -> bool:
    try:
        import _numba_cuda_redirector  # noqa: F401
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal4052NumbaPresegmentedVectorSumTest(unittest.TestCase):
    def test_numba_runtime_exposes_generic_offset_vector_sum(self) -> None:
        runtime_source = NUMBA_RUNTIME.read_text(encoding="utf-8")
        adapter_source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        descriptor = rt.describe_numba_grouped_vector_sum_f64x2()

        self.assertIn("def run_numba_grouped_vector_sum_f64x2_by_offsets", runtime_source)
        self.assertIn("def _numba_grouped_vector_sum_f64x2_offsets_kernel", runtime_source)
        self.assertIn("presegmented_row_offsets_supported", runtime_source)
        self.assertIn("optional_input_columns", descriptor)
        self.assertEqual(descriptor["optional_input_columns"], ("row_offsets:int64",))
        self.assertTrue(descriptor["presegmented_row_offsets_supported"])
        self.assertNotIn("barnes", runtime_source.lower())
        self.assertNotIn("force", runtime_source.lower())

        self.assertIn("run_numba_grouped_vector_sum_f64x2_by_offsets", adapter_source)
        self.assertIn('"v2_5_numba_presegmented_offsets_used"', adapter_source)
        self.assertIn('"v2_5_numba_global_atomic_add_used"', adapter_source)
        self.assertIn("validate_row_offsets: bool = True", adapter_source)

    def test_typed_stream_and_benchmark_helpers_expose_explicit_validation_switch(self) -> None:
        typed_stream_source = TYPED_STREAM_ADAPTER.read_text(encoding="utf-8")
        app_source = BH_APP.read_text(encoding="utf-8")

        self.assertIn("validate_row_offsets: bool = True", typed_stream_source)
        self.assertIn('"row_offset_validation_requested"', typed_stream_source)
        self.assertIn("validate_row_offsets=bool(validate_row_offsets)", typed_stream_source)
        self.assertIn("validate_row_offsets: bool = True", app_source)
        self.assertIn("validate_row_offsets=bool(validate_row_offsets)", app_source)

    def test_numba_offset_path_keeps_old_unsegmented_path_available(self) -> None:
        adapter_source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("if row_offsets is None:", adapter_source)
        self.assertIn("run_numba_grouped_vector_sum_f64x2(", adapter_source)
        self.assertIn("run_numba_grouped_vector_sum_f64x2_by_offsets(", adapter_source)

    def test_numba_cuda_offset_path_matches_reference_when_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        columns = {
            "group_ids": cuda.to_device(np.asarray([0, 0, 1, 2, 2, 2], dtype=np.int64)),
            "row_offsets": cuda.to_device(np.asarray([0, 2, 3, 6], dtype=np.int64)),
            "values_x": cuda.to_device(np.asarray([1.5, 2.5, -1.0, 4.0, 5.0, -2.0], dtype=np.float64)),
            "values_y": cuda.to_device(np.asarray([10.0, -4.0, 3.0, 0.25, 0.75, 1.0], dtype=np.float64)),
        }
        result = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=3,
            partner="numba",
            return_metadata=True,
        )

        self.assertTrue(np.allclose(result["columns"]["sum_x"].copy_to_host(), [4.0, -1.0, 7.0]))
        self.assertTrue(np.allclose(result["columns"]["sum_y"].copy_to_host(), [6.0, 3.0, 2.0]))
        metadata = result["metadata"]
        self.assertEqual(metadata["partner"], "numba")
        self.assertTrue(metadata["v2_5_numba_preview_kernel_used"])
        self.assertTrue(metadata["v2_5_numba_presegmented_offsets_used"])
        self.assertEqual("numba_grouped_vector_sum_offsets_f64x2_kernel", metadata["v2_5_numba_adapter_kernel"])
        self.assertFalse(metadata["v2_5_numba_global_atomic_add_used"])
        self.assertTrue(metadata["v2_5_numba_row_offset_validation_host_sync_used"])
        self.assertEqual(metadata["v2_6_neutral_handoff_validation_status"], "accept")
        self.assertEqual(metadata["v2_6_neutral_handoff_column_count"], 4)
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["v2_5_release_authorized"])

    def test_numba_cuda_offset_path_can_skip_repeated_offset_validation_when_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        columns = {
            "group_ids": cuda.to_device(np.asarray([0, 0, 1, 1], dtype=np.int64)),
            "row_offsets": cuda.to_device(np.asarray([0, 2, 4], dtype=np.int64)),
            "values_x": cuda.to_device(np.asarray([1.0, 3.0, -2.0, 5.0], dtype=np.float64)),
            "values_y": cuda.to_device(np.asarray([0.5, 1.5, 10.0, -3.0], dtype=np.float64)),
        }
        result = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=2,
            partner="numba",
            validate_row_offsets=False,
            return_metadata=True,
        )

        self.assertTrue(np.allclose(result["columns"]["sum_x"].copy_to_host(), [4.0, 3.0]))
        self.assertTrue(np.allclose(result["columns"]["sum_y"].copy_to_host(), [2.0, 7.0]))
        self.assertFalse(result["metadata"]["v2_5_numba_row_offset_validation_host_sync_used"])

    def test_offset_path_rejects_bad_offsets_when_cuda_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        with self.assertRaisesRegex(ValueError, "row_offsets must start at 0 and end at the row count"):
            rt.run_numba_grouped_vector_sum_f64x2_by_offsets(
                cuda.to_device(np.asarray([0, 1, 2], dtype=np.int64)),
                cuda.to_device(np.asarray([1.0], dtype=np.float64)),
                cuda.to_device(np.asarray([2.0], dtype=np.float64)),
            )

    def test_report_records_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4052", text)
        self.assertIn("run_numba_grouped_vector_sum_f64x2_by_offsets", text)
        self.assertIn("presegmented row_offsets", text)
        self.assertIn("validate_row_offsets", text)
        self.assertIn("does not add Barnes-Hut", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
