from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5462GenericOptixAabbSparseRefitGateTest(unittest.TestCase):
    def test_committed_generic_microbenchmarks_match(self) -> None:
        for count in (4096, 65536):
            payload = json.loads(
                (DOCS / f"goal5462_generic_optix_aabb_sparse_refit_linux_{count}.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(payload["matched"])
            self.assertEqual(
                payload["correctness"]["native_refit_counts"],
                payload["correctness"]["snapshot_rebuild_counts"],
            )
            self.assertGreater(payload["timing_diagnostic"]["same_host_microbenchmark_speedup"], 5.0)
            self.assertFalse(payload["claim_boundary"]["librts_paper_performance_claimed"])
            self.assertFalse(payload["claim_boundary"]["embree_used"])

    def test_librts_sequence_keeps_hybrid_execution_boundary(self) -> None:
        payload = json.loads(
            (APP / "results" / "librts_goal5462_native_sparse_refit_mutation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["author"]["counts"], [2, 1, 0, 1, 0])
        self.assertEqual(payload["rtdl"]["counts"], [2, 1, 0, 1, 0])
        self.assertEqual(
            payload["rtdl"]["mutation_execution_models"],
            [
                "native_sparse_slot_refit_with_rollback",
                "atomic_snapshot_rebuild",
                "atomic_snapshot_rebuild",
                "atomic_snapshot_rebuild",
            ],
        )
        self.assertTrue(payload["claim_boundary"]["native_incremental_rtdl_update_claimed"])
        self.assertFalse(payload["claim_boundary"]["native_incremental_rtdl_insert_delete_claimed"])

    def test_sparse_refit_native_window_is_app_neutral(self) -> None:
        source = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        ).lower()
        begin = source.index("static void refit_prepared_aabb_index_2d_slots_optix")
        end = source.index("struct gpuaabb3d", begin)
        window = source[begin:end]
        for forbidden in ("librts", "rtspatial", "paper", "ray multicast"):
            self.assertNotIn(forbidden, window)


if __name__ == "__main__":
    unittest.main()
