from __future__ import annotations

import unittest
from unittest import mock

from scripts import goal811_spatial_optix_summary_phase_profiler as profiler


SCHEMA = "goal826_tier2_phase_contract_v1"


class _PreparedStub:
    def __init__(self, rows):
        self.rows = tuple(rows)

    def run(self, query_points, *, radius: float, threshold: int):
        return self.rows

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int):
        return sum(1 for row in self.rows if int(row["neighbor_count"]) >= threshold)

    def close(self) -> None:
        pass


class Goal826Tier2PhaseProfilerContractTest(unittest.TestCase):
    def test_service_contract_is_deferred_and_phase_named(self) -> None:
        payload = profiler.run_profile(
            scenario="service_coverage_gaps",
            mode="dry-run",
            copies=1,
        )

        self.assertEqual(payload["schema_version"], SCHEMA)
        contract = payload["cloud_claim_contract"]
        self.assertIn("coverage-gap compact summaries", contract["claim_scope"])
        self.assertIn("not nearest-clinic row output", contract["non_claim"])
        self.assertEqual(contract["activation_status"], "deferred_until_real_rtx_phase_run_and_review")
        self.assertIn("single consolidated RTX batch", contract["cloud_policy"])
        self.assertEqual(
            tuple(contract["required_phase_groups"]),
            ("input_build", "optix_prepare", "optix_query", "python_postprocess"),
        )

    def test_event_contract_is_deferred_and_phase_named(self) -> None:
        payload = profiler.run_profile(
            scenario="event_hotspot_screening",
            mode="dry-run",
            copies=1,
        )

        self.assertEqual(payload["schema_version"], SCHEMA)
        contract = payload["cloud_claim_contract"]
        self.assertIn("hotspot compact summaries", contract["claim_scope"])
        self.assertIn("not neighbor-row output", contract["non_claim"])
        self.assertEqual(contract["activation_status"], "deferred_until_real_rtx_phase_run_and_review")
        self.assertIn("single consolidated RTX batch", contract["cloud_policy"])

    def test_optix_profile_contains_all_claim_contract_phases(self) -> None:
        rows = (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 2, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 3, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 4, "neighbor_count": 0, "threshold_reached": 0},
        )
        with mock.patch.object(
            profiler.service_app.rt,
            "prepare_optix_fixed_radius_count_threshold_2d",
            return_value=_PreparedStub(rows),
        ):
            payload = profiler.run_profile(
                scenario="service_coverage_gaps",
                mode="optix",
                copies=1,
            )

        timings = payload["scenario"]["timings_sec"]
        for key in payload["cloud_claim_contract"]["required_phase_groups"]:
            self.assertIn(key, timings)


if __name__ == "__main__":
    unittest.main()
