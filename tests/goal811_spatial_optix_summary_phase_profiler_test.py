from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from scripts import goal811_spatial_optix_summary_phase_profiler as profiler


class _PreparedStub:
    def __init__(self, rows):
        self.rows = tuple(rows)
        self.closed = False

    def run(self, query_points, *, radius: float, threshold: int):
        return self.rows

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int):
        return sum(1 for row in self.rows if int(row["neighbor_count"]) >= threshold)

    def close(self) -> None:
        self.closed = True


class Goal811SpatialOptixSummaryPhaseProfilerTest(unittest.TestCase):
    def test_service_dry_run_has_reference_phases(self) -> None:
        payload = profiler.run_profile(
            scenario="service_coverage_gaps",
            mode="dry-run",
            copies=1,
        )

        scenario = payload["scenario"]
        self.assertEqual(scenario["scenario"], "service_coverage_gaps")
        self.assertIn("input_build", scenario["timings_sec"])
        self.assertIn("cpu_reference_total", scenario["timings_sec"])
        self.assertEqual(scenario["result"]["household_count"], 4)

    def test_event_dry_run_has_reference_phases(self) -> None:
        payload = profiler.run_profile(
            scenario="event_hotspot_screening",
            mode="dry-run",
            copies=1,
        )

        scenario = payload["scenario"]
        self.assertEqual(scenario["scenario"], "event_hotspot_screening")
        self.assertIn("input_build", scenario["timings_sec"])
        self.assertIn("cpu_reference_total", scenario["timings_sec"])
        self.assertGreaterEqual(scenario["result"]["hotspot_count"], 1)

    def test_service_optix_mode_splits_prepare_query_and_postprocess(self) -> None:
        rows = (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 2, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 3, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 4, "neighbor_count": 0, "threshold_reached": 0},
        )
        prepared = _PreparedStub(rows)
        with mock.patch.object(
            profiler.service_app.rt,
            "prepare_optix_fixed_radius_count_threshold_2d",
            return_value=prepared,
        ):
            payload = profiler.run_profile(
                scenario="service_coverage_gaps",
                mode="optix",
                copies=1,
            )

        timings = payload["scenario"]["timings_sec"]
        self.assertIn("optix_prepare", timings)
        self.assertIn("optix_query", timings)
        self.assertIn("python_postprocess", timings)
        self.assertEqual(payload["scenario"]["result"]["uncovered_household_count"], 1)
        self.assertEqual(payload["scenario"]["result"]["summary_mode"], "scalar_threshold_count")
        self.assertIsNone(payload["scenario"]["result"]["uncovered_household_ids"])
        self.assertTrue(prepared.closed)

    def test_event_optix_mode_splits_prepare_query_and_postprocess(self) -> None:
        rows = (
            {"query_id": 1, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 2, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 3, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 4, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 5, "neighbor_count": 1, "threshold_reached": 0},
            {"query_id": 6, "neighbor_count": 1, "threshold_reached": 0},
        )
        prepared = _PreparedStub(rows)
        with mock.patch.object(
            profiler.event_app.rt,
            "prepare_optix_fixed_radius_count_threshold_2d",
            return_value=prepared,
        ):
            payload = profiler.run_profile(
                scenario="event_hotspot_screening",
                mode="optix",
                copies=1,
            )

        timings = payload["scenario"]["timings_sec"]
        self.assertIn("optix_prepare", timings)
        self.assertIn("optix_query", timings)
        self.assertIn("python_postprocess", timings)
        self.assertEqual(payload["scenario"]["result"]["hotspot_count"], 4)
        self.assertEqual(payload["scenario"]["result"]["summary_mode"], "scalar_threshold_count")
        self.assertIsNone(payload["scenario"]["result"]["hotspots"])
        self.assertTrue(prepared.closed)

    def test_cli_writes_json(self) -> None:
        output = Path("docs/reports/goal811_test_output.json")
        try:
            rc = profiler.main(
                [
                    "--scenario",
                    "service_coverage_gaps",
                    "--mode",
                    "dry-run",
                    "--output-json",
                    str(output),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertIn("service_coverage_gaps", output.read_text(encoding="utf-8"))
        finally:
            output.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
