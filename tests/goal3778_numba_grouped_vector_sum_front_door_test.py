from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NUMBA_RUNTIME = ROOT / "src/rtdsl/numba_partner_continuation.py"
PARTNER_ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
REPORT = ROOT / "docs/reports/goal3778_numba_grouped_vector_sum_front_door_2026-06-07.md"
ARTIFACT = ROOT / "docs/reports/goal3778_numba_grouped_vector_sum_front_door_a5000.json"


def _numba_cuda_available() -> bool:
    try:
        import _numba_cuda_redirector  # noqa: F401
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal3778NumbaGroupedVectorSumFrontDoorTest(unittest.TestCase):
    def test_numba_descriptor_and_support_matrix_promote_generic_vector_sum_preview(self) -> None:
        descriptor = rt.describe_numba_grouped_vector_sum_f64x2()
        self.assertEqual(descriptor["operation"], "grouped_vector_sum_f64x2")
        self.assertEqual(descriptor["partner"], "numba")
        self.assertEqual(descriptor["status"], "preview_not_promoted")
        self.assertEqual(descriptor["input_columns"], ("group_ids:int64", "values_x:float64", "values_y:float64"))
        self.assertEqual(descriptor["output_columns"], ("sum_x:float64", "sum_y:float64"))
        self.assertFalse(descriptor["raw_kernel_required"])
        self.assertFalse(descriptor["replaces_rt_traversal"])
        self.assertFalse(descriptor["promoted_performance_path"])

        self.assertIn("grouped_vector_sum_f64x2", rt.V2_5_NUMBA_PREVIEW_OPERATIONS)
        support = rt.plan_v2_5_partner_support("grouped_vector_sum_f64x2", "numba")
        self.assertEqual(support["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertTrue(support["supported"])
        self.assertTrue(support["requires_cuda"])
        self.assertFalse(support["public_speedup_claim_authorized"])
        self.assertFalse(support["true_zero_copy_claim_authorized"])

    def test_front_door_accepts_explicit_numba_without_app_or_native_engine_logic(self) -> None:
        runtime_source = NUMBA_RUNTIME.read_text(encoding="utf-8")
        adapter_source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("def run_numba_grouped_vector_sum_f64x2", runtime_source)
        self.assertIn("def _numba_grouped_vector_sum_f64x2_kernel", runtime_source)
        self.assertIn("cuda.atomic.add(output_x", runtime_source)
        self.assertIn("cuda.atomic.add(output_y", runtime_source)
        self.assertIn('"grouped_vector_sum_f64x2"', adapter_source)
        self.assertIn('partner == "numba"', adapter_source)
        self.assertNotIn("barnes", runtime_source.lower())
        self.assertNotIn("force", runtime_source.lower())

        dry_run = rt.execute_grouped_vector_sum_typed_stream_partner_columns(
            group_ids=np.asarray([0, 0, 1], dtype=np.int64),
            values_x=np.asarray([1.0, 2.0, 3.0], dtype=np.float64),
            values_y=np.asarray([-1.0, 4.0, 0.5], dtype=np.float64),
            group_count=2,
            partner="numba",
            stream_id="goal3778_dry_run",
            dry_run=True,
        )
        self.assertEqual(dry_run["status"], "dry_run_partner_consumer_request")
        self.assertEqual(dry_run["operation"], "grouped_vector_sum_f64x2")
        self.assertEqual(dry_run["continuation_plan"]["user_selected_partner"], "numba")
        self.assertFalse(dry_run["automatic_partner_selection_allowed"])
        self.assertFalse(dry_run["release_authorized"])
        self.assertFalse(dry_run["true_zero_copy_claim_authorized"])

    def test_numba_cuda_execution_matches_reference_when_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        group_ids = cuda.to_device(np.asarray([0, 0, 1, 2, 2, 2], dtype=np.int64))
        values_x = cuda.to_device(np.asarray([1.5, 2.5, -1.0, 4.0, 5.0, -2.0], dtype=np.float64))
        values_y = cuda.to_device(np.asarray([10.0, -4.0, 3.0, 0.25, 0.75, 1.0], dtype=np.float64))

        result = rt.grouped_vector_sum_2d_partner_columns(
            {"group_ids": group_ids, "values_x": values_x, "values_y": values_y},
            group_count=4,
            partner="numba",
            return_metadata=True,
        )
        self.assertTrue(np.allclose(result["columns"]["sum_x"].copy_to_host(), [4.0, -1.0, 7.0, 0.0]))
        self.assertTrue(np.allclose(result["columns"]["sum_y"].copy_to_host(), [6.0, 3.0, 2.0, 0.0]))
        metadata = result["metadata"]
        self.assertEqual(metadata["partner"], "numba")
        self.assertTrue(metadata["v2_5_numba_preview_kernel_used"])
        self.assertEqual(metadata["v2_6_neutral_handoff_validation_status"], "accept")
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["v2_5_release_authorized"])

    def test_report_records_goal3778_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3778", text)
        self.assertIn("grouped_vector_sum_f64x2", text)
        self.assertIn("partner=\"numba\"", text)
        self.assertIn("does not add force law", text)
        self.assertIn("does not authorize", text)
        if ARTIFACT.exists():
            artifact = ARTIFACT.read_text(encoding="utf-8")
            self.assertIn('"rows_match_reference": true', artifact)
            self.assertIn('"public_speedup_claim_authorized": false', artifact)


if __name__ == "__main__":
    unittest.main()
