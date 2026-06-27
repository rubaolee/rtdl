from __future__ import annotations

import json
from pathlib import Path
import unittest

from examples.benchmark_apps.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4173_declared_all_predicate_rtdbscan_2m_probe_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4173_declared_all_predicate_rtdbscan_2m_probe_pod.json"


class Goal4173DeclaredAllPredicateRtDbscan2MProbeTest(unittest.TestCase):
    def test_report_records_timing_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted bounded pod evidence; no route promotion",
            "Declared all-true versus current: `1.662x`",
            "skips RT count-threshold phase; external proof required",
            "`rt_count_threshold_executed` is false",
            "`rt_core_accelerated` is false",
            "does not promote this route as the default",
            "mixed-predicate",
            "known_host_phase_sec",
            "not intended to sum exactly",
        ):
            self.assertIn(fragment, report)

    def test_artifact_acceptance_and_claim_boundaries(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal4173")
        self.assertEqual(artifact["commit"], "0ec736408af952a61485680865c7f760fb406799")
        self.assertIn("RTX 4000 Ada", artifact["gpu"])
        self.assertEqual(artifact["common"]["point_count"], 2_097_152)
        self.assertEqual(artifact["common"]["seed"], 20260519)
        self.assertEqual(artifact["warmup_point_count"], 4096)
        self.assertTrue(artifact["acceptance"]["same_signature_current_measured_declared"])
        self.assertTrue(artifact["acceptance"]["declared_skipped_rt_count_threshold"])
        self.assertTrue(artifact["acceptance"]["declared_external_proof_required"])
        self.assertTrue(artifact["acceptance"]["declared_all_predicate_fast_path_observed"])
        self.assertTrue(artifact["acceptance"]["declared_no_rt_core_claim"])
        self.assertFalse(artifact["acceptance"]["route_promotion_authorized"])
        self.assertFalse(artifact["acceptance"]["release_authorized"])
        self.assertFalse(artifact["acceptance"]["public_speedup_claim_authorized"])
        self.assertFalse(artifact["acceptance"]["broad_rt_core_claim_authorized"])
        self.assertFalse(artifact["acceptance"]["whole_app_claim_authorized"])
        self.assertFalse(artifact["acceptance"]["true_zero_copy_claim_authorized"])

    def test_artifact_rows_and_speedups_match_expected_shape(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["label"]: row for row in artifact["rows"]}
        self.assertEqual(set(rows), {
            "current_grouped_stream_numba",
            "measured_all_true_predicate_direct_status",
            "declared_all_true_predicate_direct_status",
        })
        signature = {
            "cluster_sizes": {"1": 2_097_152},
            "core_count": 2_097_152,
            "noise_count": 0,
        }
        for row in rows.values():
            self.assertEqual(row["signature"], signature)
        self.assertAlmostEqual(rows["current_grouped_stream_numba"]["elapsed_sec"], 34.29874958842993)
        self.assertAlmostEqual(rows["measured_all_true_predicate_direct_status"]["elapsed_sec"], 25.003687508404255)
        self.assertAlmostEqual(rows["declared_all_true_predicate_direct_status"]["elapsed_sec"], 20.64225125312805)
        self.assertGreater(artifact["speedups"]["declared_all_true_vs_current_elapsed"], 1.66)
        self.assertGreater(artifact["speedups"]["declared_all_true_vs_measured_all_true_elapsed"], 1.21)
        declared = rows["declared_all_true_predicate_direct_status"]["metadata"]
        self.assertEqual(declared["predicate_flags_source"], "caller_declared_all_true")
        self.assertFalse(declared["rt_count_threshold_executed"])
        self.assertTrue(declared["caller_declared_predicate_columns_require_external_proof"])
        self.assertFalse(declared["rt_core_accelerated"])

    def test_advisor_evidence_refs_include_goal4173_without_promoting_route(self) -> None:
        advice = app.explain_rt_dbscan_explicit_route_choice(
            "road3d",
            repeated_component_signature=False,
            point_count=2_097_152,
        )
        declared = [
            option
            for option in advice["options"]
            if option["mode"] == app.RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE
        ]
        self.assertTrue(declared)
        self.assertIn("Goal4173", declared[0]["evidence_refs"])
        self.assertFalse(declared[0]["route_promotion_authorized"])
        self.assertNotEqual(advice["options"][0]["mode"], app.RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE)


if __name__ == "__main__":
    unittest.main()
