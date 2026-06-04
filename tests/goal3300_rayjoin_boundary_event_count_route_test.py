from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3300_rayjoin_boundary_event_count_route_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3300_boundary_event_same_slice_pod_2026-06-04.json"


class Goal3300RayJoinBoundaryEventCountRouteTest(unittest.TestCase):
    def test_app_and_runner_expose_boundary_event_mode_without_native_app_logic(self) -> None:
        app = APP.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn('boundary_event_point_id_count_device_columns', app)
        self.assertIn('first_boundary_crossing_device_columns', app)
        self.assertIn('grouped_count_by_point_id_device_columns', app)
        self.assertIn('positive_membership_equivalent": False', app)
        self.assertIn('boundary_event_contract_not_positive_membership', app)
        self.assertIn('rtdl_boundary_event_count_not_pip_membership', runner)
        self.assertIn('def validate_rtdl_sample_payload', runner)

    def test_report_records_negative_performance_result_and_next_primitive(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "negative for PIP performance",
            "boundary-event count, not PIP membership",
            "The grouped-count continuation is not the bottleneck",
            "fused generic closed-shape first-hit or predicate-count path",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_pod_artifact_records_split_timings_and_claim_boundaries(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["rtdl_commit"], "56a91c8955985acd2ef98964c776444797b7bce9")
        self.assertEqual(artifact["status"], "pass_with_optimization_gap")
        self.assertFalse(any(artifact["claim_boundary"].values()))
        comparisons = {row["workload"]: row for row in artifact["comparisons"]}
        self.assertEqual(comparisons["lsi"]["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(
            comparisons["pip"]["count_contract_status"],
            "rtdl_boundary_event_count_not_pip_membership",
        )
        self.assertGreater(comparisons["pip"]["rtdl_over_rayjoin_query_ratio"], 10.0)
        pip = artifact["rtdl"]["pip"]
        self.assertEqual(pip["count_mode"], "boundary_event_point_id_count_device_columns")
        self.assertEqual(pip["counts"]["last"], 3961)
        self.assertGreater(pip["boundary_event_device_columns_ms"]["median"], 3.0)
        self.assertLess(pip["boundary_event_grouped_count_ms"]["median"], 0.5)
        self.assertEqual(pip["native_phase_samples"][0]["mode"], "boundary_event_device_columns")
        self.assertEqual(pip["native_phase_samples"][0]["candidate_download"], 0.0)


if __name__ == "__main__":
    unittest.main()
