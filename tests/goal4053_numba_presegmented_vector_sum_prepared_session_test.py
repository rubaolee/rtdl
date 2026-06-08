from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NUMBA_RUNTIME = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal4053_numba_presegmented_vector_sum_prepared_session_2026-06-08.md"


def _numba_cuda_available() -> bool:
    try:
        import _numba_cuda_redirector  # noqa: F401
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal4053NumbaPresegmentedVectorSumPreparedSessionTest(unittest.TestCase):
    def test_prepared_session_api_is_generic_and_exported(self) -> None:
        runtime_source = NUMBA_RUNTIME.read_text(encoding="utf-8")
        adapter_source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertTrue(hasattr(rt, "NUMBA_GROUPED_VECTOR_SUM_OFFSETS_SESSION_VERSION"))
        self.assertTrue(hasattr(rt, "prepare_numba_grouped_vector_sum_f64x2_offsets_session"))
        self.assertTrue(hasattr(rt, "run_numba_prepared_grouped_vector_sum_f64x2_by_offsets"))
        self.assertTrue(hasattr(rt, "prepare_grouped_vector_sum_2d_partner_columns_session"))
        self.assertTrue(hasattr(rt, "run_grouped_vector_sum_2d_partner_columns_session"))
        self.assertIn("def prepare_numba_grouped_vector_sum_f64x2_offsets_session", runtime_source)
        self.assertIn("def run_numba_prepared_grouped_vector_sum_f64x2_by_offsets", runtime_source)
        self.assertIn("def prepare_grouped_vector_sum_2d_partner_columns_session", adapter_source)
        self.assertIn("def run_grouped_vector_sum_2d_partner_columns_session", adapter_source)
        self.assertNotIn("barnes", runtime_source.lower())
        self.assertNotIn("force", runtime_source.lower())

    def test_prepared_session_matches_one_shot_when_numba_cuda_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        columns = {
            "group_ids": cuda.to_device(np.asarray([0, 0, 1, 2, 2, 2], dtype=np.int64)),
            "row_offsets": cuda.to_device(np.asarray([0, 2, 3, 6], dtype=np.int64)),
            "values_x": cuda.to_device(np.asarray([1.5, 2.5, -1.0, 4.0, 5.0, -2.0], dtype=np.float64)),
            "values_y": cuda.to_device(np.asarray([10.0, -4.0, 3.0, 0.25, 0.75, 1.0], dtype=np.float64)),
        }
        one_shot = rt.grouped_vector_sum_2d_partner_columns(
            columns,
            group_count=3,
            partner="numba",
            validate_row_offsets=False,
            return_metadata=True,
        )
        prepared = rt.prepare_grouped_vector_sum_2d_partner_columns_session(
            columns,
            group_count=3,
            partner="numba",
            validate_row_offsets=False,
            return_metadata=True,
        )
        replay = rt.run_grouped_vector_sum_2d_partner_columns_session(
            prepared["session"],
            return_metadata=True,
        )

        self.assertTrue(np.allclose(replay["columns"]["sum_x"].copy_to_host(), one_shot["columns"]["sum_x"].copy_to_host()))
        self.assertTrue(np.allclose(replay["columns"]["sum_y"].copy_to_host(), one_shot["columns"]["sum_y"].copy_to_host()))
        metadata = replay["metadata"]
        self.assertTrue(metadata["prepared_session_reused"])
        self.assertTrue(metadata["output_columns_reused"])
        self.assertFalse(metadata["per_run_neutral_handoff_validation_used"])
        self.assertFalse(metadata["v2_5_numba_global_atomic_add_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_prepared_session_rejects_unsupported_partner(self) -> None:
        with self.assertRaisesRegex(ValueError, "partner='numba'"):
            rt.prepare_grouped_vector_sum_2d_partner_columns_session(
                {
                    "group_ids": np.asarray([0], dtype=np.int64),
                    "row_offsets": np.asarray([0, 1], dtype=np.int64),
                    "values_x": np.asarray([1.0], dtype=np.float64),
                    "values_y": np.asarray([2.0], dtype=np.float64),
                },
                group_count=1,
                partner="cupy",
            )

    def test_report_records_goal4053_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4053", text)
        self.assertIn("prepare_grouped_vector_sum_2d_partner_columns_session", text)
        self.assertIn("run_grouped_vector_sum_2d_partner_columns_session", text)
        self.assertIn("per-call neutral-handoff", text)
        self.assertIn("not authorize true zero-copy", text)


if __name__ == "__main__":
    unittest.main()
