from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def retry_scheduler_worklist():
    import rtdsl as rt

    return rt.heavy_offload_worklist_numpy_columns(
        source_ids=[200, 201, 202, 203, 204],
        primitive_ids=[10, 11, 12, 13, 14],
        begin_offsets=[0, 5, 9, 12, 20],
        work_counts=[4, 1, 15, 2, 13],
        lower_bounds=[0.0, 1.0, 2.0, 3.0, 4.0],
        upper_bounds=[0.5, 1.5, 6.0, 4.0, 7.0],
        miss_mask=[False, False, False, True, False],
        deferred_mask=[False, True, False, False, False],
        work_cost_estimates=[4.0, 100.0, 30.0, 80.0, 26.0],
        heavy_threshold=10,
        return_metadata=True,
    )


class Goal5280HeavyOffloadNonXhdConsumerGateTest(unittest.TestCase):
    def test_retry_scheduler_consumer_uses_active_miss_and_deferred_rows(self) -> None:
        import rtdsl as rt

        worklist = retry_scheduler_worklist()
        columns = worklist["columns"]
        telemetry = worklist["telemetry"]

        self.assertEqual(worklist["metadata"]["contract"], rt.HEAVY_OFFLOAD_WORKLIST_CONTRACT)
        self.assertEqual(worklist["metadata"]["app_semantics"], "none")
        self.assertEqual(columns["work_source_ids"].tolist(), [201, 202, 203, 204])
        self.assertEqual(columns["work_primitive_ids"].tolist(), [11, 12, 13, 14])
        self.assertEqual(
            columns["work_kind_codes"].tolist(),
            [
                rt.HEAVY_OFFLOAD_WORKLIST_KIND_CODES["deferred"],
                rt.HEAVY_OFFLOAD_WORKLIST_KIND_CODES["active"],
                rt.HEAVY_OFFLOAD_WORKLIST_KIND_CODES["miss"],
                rt.HEAVY_OFFLOAD_WORKLIST_KIND_CODES["active"],
            ],
        )
        self.assertEqual(columns["work_cost_estimates"].tolist(), [100.0, 30.0, 80.0, 26.0])
        self.assertEqual(telemetry["in_queue_capacity"], 5)
        self.assertEqual(telemetry["miss_queue_capacity"], 1)
        self.assertEqual(telemetry["deferred_queue_capacity"], 1)
        self.assertEqual(telemetry["heavy_offload_peak_rows"], 4)
        self.assertEqual(telemetry["heavy_offload_queue_peak_bytes"], 64)

    def test_retry_scheduler_consumer_is_independent_from_paper_apps(self) -> None:
        import rtdsl as rt

        consumer_source = inspect.getsource(retry_scheduler_worklist).lower()
        helper_source = inspect.getsource(rt.heavy_offload_worklist_numpy_columns).lower()
        for source in (consumer_source, helper_source):
            for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
                self.assertNotIn(forbidden, source)

    def test_retry_scheduler_overflow_fails_closed(self) -> None:
        import rtdsl as rt

        worklist = rt.heavy_offload_worklist_numpy_columns(
            source_ids=[200, 201, 202, 203, 204],
            primitive_ids=[10, 11, 12, 13, 14],
            begin_offsets=[0, 5, 9, 12, 20],
            work_counts=[4, 1, 15, 2, 13],
            lower_bounds=[0.0, 1.0, 2.0, 3.0, 4.0],
            upper_bounds=[0.5, 1.5, 6.0, 4.0, 7.0],
            miss_mask=[False, False, False, True, False],
            deferred_mask=[False, True, False, False, False],
            heavy_threshold=10,
            row_capacity=3,
            return_metadata=True,
        )

        self.assertTrue(worklist["metadata"]["overflowed"])
        self.assertEqual(worklist["metadata"]["attempted_row_count"], 4)
        self.assertEqual(worklist["metadata"]["row_count"], 0)
        self.assertEqual(worklist["telemetry"]["heavy_offload_attempted_rows"], 4)
        self.assertEqual(worklist["telemetry"]["heavy_offload_peak_rows"], 0)
        for array in worklist["columns"].values():
            self.assertEqual(array.size, 0)


if __name__ == "__main__":
    unittest.main()
