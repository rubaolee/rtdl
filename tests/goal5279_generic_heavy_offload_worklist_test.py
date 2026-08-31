from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _work_fixture():
    return {
        "source_ids": [100, 101, 102, 103],
        "primitive_ids": [10, 11, 12, 13],
        "begin_offsets": [0, 4, 8, 10],
        "work_counts": [2, 9, 1, 7],
        "lower_bounds": [0.1, 0.2, 0.3, 0.4],
        "upper_bounds": [1.0, 2.0, 3.0, 4.0],
        "miss_mask": [False, False, True, False],
    }


class Goal5279GenericHeavyOffloadWorklistTest(unittest.TestCase):
    def test_worklist_emits_active_and_miss_rows_with_peak_telemetry(self) -> None:
        import rtdsl as rt

        fixture = _work_fixture()
        worklist = rt.heavy_offload_worklist_numpy_columns(
            **fixture,
            heavy_threshold=5,
            return_metadata=True,
        )

        columns = worklist["columns"]
        telemetry = worklist["telemetry"]
        metadata = worklist["metadata"]

        self.assertEqual(metadata["contract"], rt.HEAVY_OFFLOAD_WORKLIST_CONTRACT)
        self.assertEqual(tuple(metadata["row_schema"]), rt.HEAVY_OFFLOAD_WORKLIST_ROW_SCHEMA)
        self.assertEqual(metadata["app_semantics"], "none")
        self.assertFalse(metadata["overflowed"])
        self.assertEqual(metadata["row_count"], 3)
        self.assertEqual(metadata["attempted_row_count"], 3)

        self.assertEqual(columns["work_source_ids"].tolist(), [101, 102, 103])
        self.assertEqual(columns["work_primitive_ids"].tolist(), [11, 12, 13])
        self.assertEqual(columns["work_begin_offsets"].tolist(), [4, 8, 10])
        self.assertEqual(columns["work_counts"].tolist(), [9, 1, 7])
        self.assertEqual(
            columns["work_kind_codes"].tolist(),
            [
                rt.HEAVY_OFFLOAD_WORKLIST_KIND_CODES["active"],
                rt.HEAVY_OFFLOAD_WORKLIST_KIND_CODES["miss"],
                rt.HEAVY_OFFLOAD_WORKLIST_KIND_CODES["active"],
            ],
        )
        self.assertEqual(columns["work_cost_estimates"].tolist(), [9.0, 1.0, 7.0])
        self.assertEqual(columns["lower_bounds"].tolist(), [0.2, 0.3, 0.4])
        self.assertEqual(columns["upper_bounds"].tolist(), [2.0, 3.0, 4.0])

        self.assertEqual(telemetry["in_queue_capacity"], 4)
        self.assertEqual(telemetry["miss_queue_capacity"], 1)
        self.assertEqual(telemetry["in_queue_bytes"], 32)
        self.assertEqual(telemetry["miss_queue_bytes"], 8)
        self.assertEqual(telemetry["heavy_offload_current_rows"], 3)
        self.assertEqual(telemetry["heavy_offload_peak_rows"], 3)
        self.assertEqual(telemetry["heavy_offload_queue_current_bytes"], 48)
        self.assertEqual(telemetry["heavy_offload_queue_peak_bytes"], 48)
        self.assertGreater(telemetry["device_buffer_bytes_excluding_accel"], 0)
        self.assertIsNone(telemetry["native_accel_bytes_if_applicable"])

    def test_overflow_fails_closed_without_partial_rows(self) -> None:
        import rtdsl as rt

        fixture = _work_fixture()
        worklist = rt.heavy_offload_worklist_numpy_columns(
            **fixture,
            heavy_threshold=5,
            row_capacity=2,
            return_metadata=True,
        )

        self.assertTrue(worklist["metadata"]["overflowed"])
        self.assertEqual(worklist["metadata"]["attempted_row_count"], 3)
        self.assertEqual(worklist["metadata"]["row_count"], 0)
        self.assertEqual(worklist["telemetry"]["heavy_offload_attempted_rows"], 3)
        self.assertEqual(worklist["telemetry"]["heavy_offload_current_rows"], 0)
        for array in worklist["columns"].values():
            self.assertEqual(array.size, 0)

    def test_non_xhd_facility_backlog_consumer_uses_same_generic_worklist(self) -> None:
        import rtdsl as rt

        service_station_ids = [1, 2, 3, 4]
        demand_region_ids = [500, 501, 502, 503]
        backlog = [3, 12, 5, 18]
        stale_regions = [False, False, True, False]
        worklist = rt.heavy_offload_worklist_numpy_columns(
            source_ids=service_station_ids,
            primitive_ids=demand_region_ids,
            begin_offsets=[0, 3, 15, 20],
            work_counts=backlog,
            lower_bounds=[0.0, 2.0, 4.0, 8.0],
            upper_bounds=[1.0, 5.0, 9.0, 11.0],
            miss_mask=stale_regions,
            work_cost_estimates=[3.0, 24.0, 10.0, 36.0],
            heavy_threshold=10,
            return_metadata=True,
        )

        self.assertEqual(worklist["columns"]["work_source_ids"].tolist(), [2, 3, 4])
        self.assertEqual(worklist["columns"]["work_primitive_ids"].tolist(), [501, 502, 503])
        self.assertEqual(worklist["columns"]["work_cost_estimates"].tolist(), [24.0, 10.0, 36.0])
        self.assertEqual(worklist["metadata"]["app_semantics"], "none")

        source = inspect.getsource(rt.heavy_offload_worklist_numpy_columns).lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec"):
            self.assertNotIn(forbidden, source)

    def test_public_surface_exports_schema_and_reference(self) -> None:
        import rtdsl as rt

        for name in (
            "HEAVY_OFFLOAD_WORKLIST_CONTRACT",
            "HEAVY_OFFLOAD_WORKLIST_KIND_CODES",
            "HEAVY_OFFLOAD_WORKLIST_ROW_SCHEMA",
            "heavy_offload_worklist_numpy_columns",
        ):
            self.assertIn(name, rt.__all__)

    def test_bad_contracts_fail_closed_or_raise(self) -> None:
        import rtdsl as rt

        fixture = _work_fixture()
        bad = dict(fixture)
        bad["primitive_ids"] = [1, 2]
        with self.assertRaisesRegex(ValueError, "primitive ids must have the same shape"):
            rt.heavy_offload_worklist_numpy_columns(**bad, heavy_threshold=5)

        with self.assertRaisesRegex(ValueError, "heavy_threshold must be non-negative"):
            rt.heavy_offload_worklist_numpy_columns(**fixture, heavy_threshold=-1)

        with self.assertRaisesRegex(ValueError, "miss_mask must have the same shape"):
            rt.heavy_offload_worklist_numpy_columns(
                **{key: value for key, value in fixture.items() if key != "miss_mask"},
                miss_mask=[True],
                heavy_threshold=5,
            )

        with self.assertRaisesRegex(ValueError, "miss_mask and deferred_mask must not overlap"):
            rt.heavy_offload_worklist_numpy_columns(
                **fixture,
                deferred_mask=[False, False, True, False],
                heavy_threshold=5,
            )


if __name__ == "__main__":
    unittest.main()
