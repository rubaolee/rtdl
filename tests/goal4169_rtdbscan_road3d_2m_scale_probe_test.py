from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4169_rtdbscan_road3d_2m_scale_probe_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4169_rtdbscan_road3d_2m_scale_probe_2026-06-09.md"


class Goal4169RtDbscanRoad3d2MScaleProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.rows = {row["label"]: row for row in cls.payload["rows"]}

    def test_artifact_records_bounded_pod_context(self) -> None:
        self.assertEqual(self.payload["schema"], "rtdl.goal4169.rtdbscan_2m_scale_probe.v1")
        self.assertEqual(self.payload["commit"], "72a4aedc6425646e00cf903c395c6b007cbd3dcc")
        self.assertIn("NVIDIA RTX 4000 Ada", self.payload["gpu"])
        self.assertEqual(self.payload["dataset"], "road3d")
        self.assertEqual(self.payload["point_count"], 2_097_152)
        boundary = self.payload["claim_boundary"]
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_claim_authorized",
            "route_promotion_authorized",
            "automatic_partner_selection_authorized",
            "hidden_dispatch_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_all_predicate_wrapper_preserves_rtdbscan_signature_and_wins(self) -> None:
        current = self.rows["current_grouped_stream_numba"]
        candidate = self.rows["predicate_all_true_until_stable"]
        self.assertEqual(current["status"], "ok")
        self.assertEqual(candidate["status"], "ok")
        self.assertEqual(candidate["signature"], current["signature"])
        self.assertGreater(current["reported_elapsed_sec"] / candidate["reported_elapsed_sec"], 1.0)
        metadata = candidate["metadata"]
        self.assertTrue(metadata["all_predicate_fast_path"])
        self.assertEqual(metadata["border_candidate_updates"], 0)
        self.assertTrue(metadata["direct_status_convergence_proven"])

    def test_plain_component_signature_is_fast_but_not_the_app_signature_shape(self) -> None:
        current = self.rows["current_grouped_stream_numba"]
        generic = self.rows["prepared_direct_status_until_stable"]
        self.assertEqual(generic["status"], "ok")
        self.assertGreater(current["reported_elapsed_sec"] / generic["reported_elapsed_sec"], 1.0)
        self.assertNotEqual(generic["signature"], current["signature"])
        self.assertEqual(generic["signature"]["component_sizes"], [2_097_152])
        self.assertEqual(sorted(int(value) for value in current["signature"]["cluster_sizes"].values()), [2_097_152])

    def test_comparison_records_exact_wrapper_match_only(self) -> None:
        comparisons = {row["candidate"]: row for row in self.payload["comparisons"]}
        self.assertFalse(comparisons["prepared_direct_status_until_stable"]["same_signature"])
        self.assertTrue(comparisons["predicate_all_true_until_stable"]["same_signature"])
        self.assertGreater(comparisons["predicate_all_true_until_stable"]["speedup_current_over_candidate"], 1.4)

    def test_report_keeps_boundary_and_interpretation_precise(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted bounded scale evidence; no route promotion",
            "2,097,152 points",
            "1.411x faster",
            "does not include the RT-DBSCAN",
            "does not solve mixed-predicate rows",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)

    def test_current_route_registry_names_bounded_2m_evidence_without_promotion(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
            "rtdl.v2_10.current_benchmark_route_decisions.goal4169.v1",
        )
        route = rt.explain_current_benchmark_route("rt_dbscan")
        self.assertIn("Goal4169 extends", route["current_reader_decision"])
        self.assertIn("2,097,152 points", route["current_reader_decision"])
        self.assertIn("Goal4169 records road3d 2M evidence", route["user_choice_guidance"])
        self.assertIn("Goal4169", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
