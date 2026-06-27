from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from examples.benchmark_apps.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3017_numba_grouped_witness_no_host_sync_fast_path_2026-06-01.md"
ADAPTER_SOURCE = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
NUMBA_SOURCE = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py"


class Goal3017NumbaGroupedWitnessNoHostSyncFastPathTest(unittest.TestCase):
    def test_sources_expose_explicit_fast_path_flags(self) -> None:
        combined = (
            ADAPTER_SOURCE.read_text(encoding="utf-8")
            + NUMBA_SOURCE.read_text(encoding="utf-8")
            + APP.read_text(encoding="utf-8")
        )
        for phrase in (
            "numba_known_dense_groups",
            "numba_validate_group_ids",
            "numba_validate_nan_scores",
            "compact_present_groups",
            "host_present_group_compaction_used",
            "nan_validation_host_sync_used",
        ):
            self.assertIn(phrase, combined)

    def test_report_states_safety_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "conservative defaults remain unchanged",
            "numba_known_dense_groups=True",
            "host_present_group_compaction_used: False",
            "nan_validation_host_sync_used: False",
            "must not be used for arbitrary user-provided score rows",
            "does not authorize true zero-copy",
        ):
            self.assertIn(phrase, text)

    def test_fast_path_executes_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable fast-path validation")

        import numpy as np

        try:
            import _numba_cuda_redirector  # noqa: F401
        except ImportError:
            pass
        from numba import cuda

        payload = rt.group_argmin_then_global_argmax_partner_columns(
            {
                "group_ids": cuda.to_device(np.asarray([0, 0, 1, 1], dtype=np.int64)),
                "item_ids": cuda.to_device(np.asarray([20, 21, 30, 31], dtype=np.int64)),
                "scores": cuda.to_device(np.asarray([3.0, 1.0, 4.0, 2.0], dtype=np.float64)),
            },
            group_count=2,
            partner="numba",
            numba_known_dense_groups=True,
            numba_validate_group_ids=False,
            numba_validate_nan_scores=False,
            return_metadata=True,
        )
        metadata = payload["metadata"]
        self.assertEqual(metadata["winner_group_id"], 1)
        self.assertEqual(metadata["winner_item_id"], 31)
        self.assertEqual(metadata["winner_score"], 2.0)
        self.assertTrue(metadata["numba_known_dense_groups"])
        self.assertFalse(metadata["host_present_group_compaction_used"])
        self.assertFalse(metadata["nan_validation_host_sync_used"])

    def test_hausdorff_modes_record_fast_path_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable Hausdorff Numba validation")

        for mode in ("partner_numba_witness_exact", "partner_numba_block_nearest_exact"):
            payload = hausdorff.run_app(mode, copies=2)
            self.assertTrue(payload["matches_oracle"])
            for key in ("directed_a_to_b", "directed_b_to_a"):
                directed = payload[key]
                self.assertTrue(directed["numba_known_dense_groups"])
                self.assertFalse(directed["host_present_group_compaction_used"])
                self.assertFalse(directed["nan_validation_host_sync_used"])


if __name__ == "__main__":
    unittest.main()
