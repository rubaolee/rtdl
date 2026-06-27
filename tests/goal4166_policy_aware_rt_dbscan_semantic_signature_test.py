from __future__ import annotations

import json
from pathlib import Path
import unittest

from examples.benchmark_apps.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
GOAL4159_ARTIFACT = ROOT / "docs" / "reports" / "goal4159_mixed_predicate_direct_status_scale_pod.json"
GOAL4165_ARTIFACT = ROOT / "docs" / "reports" / "goal4165_mixed_policy_variant_probe_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4166_policy_aware_rt_dbscan_semantic_signature_2026-06-09.md"


class Goal4166PolicyAwareRtDbscanSemanticSignatureTest(unittest.TestCase):
    def test_helper_separates_policy_bound_component_sizes_from_core_noise_contract(self) -> None:
        artifact = json.loads(GOAL4159_ARTIFACT.read_text(encoding="utf-8"))
        row = next(
            item for item in artifact["comparisons"]
            if item["case"] == "road_sparse_many_noise"
            and item["candidate"] == "predicate_direct_status_until_stable"
        )
        current = row["current_signature"]
        candidate = row["candidate_signature"]
        self.assertFalse(app.same_canonical_component_size_signature(current, candidate))
        self.assertFalse(
            app.same_policy_aware_rt_dbscan_semantic_signature(
                current,
                candidate,
                border_assignment_policy="policy_bound_reference",
                component_size_contract="policy_bound_component_sizes",
            )
        )
        self.assertTrue(
            app.same_policy_aware_rt_dbscan_semantic_signature(
                current,
                candidate,
                border_assignment_policy="border_tie_break_not_semantic",
                component_size_contract="core_noise_assigned_counts_only",
            )
        )

    def test_helper_fields_are_stable_and_explanatory(self) -> None:
        signature = {
            "cluster_sizes": {10: 4, 20: 6},
            "core_count": 7,
            "noise_count": 2,
        }
        policy_bound = app.policy_aware_rt_dbscan_semantic_signature(
            signature,
            border_assignment_policy="lowest_predicate_true_point_id_within_radius",
        )
        self.assertEqual(policy_bound["contract"], "rt_dbscan_policy_aware_semantic_signature_v1")
        self.assertEqual(policy_bound["component_size_contract"], "policy_bound_component_sizes")
        self.assertEqual(policy_bound["cluster_sizes"], (4, 6))
        self.assertEqual(policy_bound["component_count"], 2)
        self.assertEqual(policy_bound["assigned_count"], 10)
        self.assertEqual(policy_bound["border_count"], 3)
        self.assertEqual(policy_bound["point_count"], 12)

        counts_only = app.policy_aware_rt_dbscan_semantic_signature(
            signature,
            border_assignment_policy="border_tie_break_not_semantic",
            component_size_contract="core_noise_assigned_counts_only",
        )
        self.assertNotIn("cluster_sizes", counts_only)
        self.assertNotIn("component_count", counts_only)
        self.assertEqual(counts_only["assigned_count"], 10)
        self.assertEqual(counts_only["border_count"], 3)

    def test_goal4165_probe_rows_all_match_under_core_noise_assigned_contract(self) -> None:
        artifact = json.loads(GOAL4165_ARTIFACT.read_text(encoding="utf-8"))
        for row in artifact["rows"]:
            candidate = next(run for run in row["runs"] if run["label"] == "predicate_direct_status_until_stable")
            for reference in row["runs"]:
                if reference["label"] == "predicate_direct_status_until_stable":
                    continue
                self.assertTrue(
                    app.same_policy_aware_rt_dbscan_semantic_signature(
                        reference["signature"],
                        candidate["signature"],
                        border_assignment_policy="border_tie_break_not_semantic",
                        component_size_contract="core_noise_assigned_counts_only",
                    ),
                    (row["case"], row["seed"], reference["label"]),
                )

    def test_invalid_contract_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "component_size_contract must be"):
            app.policy_aware_rt_dbscan_semantic_signature(
                {"cluster_sizes": {1: 1}, "core_count": 1, "noise_count": 0},
                border_assignment_policy="x",
                component_size_contract="not_a_contract",
            )

    def test_route_advisor_names_policy_aware_helper(self) -> None:
        advice = app.explain_rt_dbscan_explicit_route_choice(
            "road3d",
            repeated_component_signature=True,
            point_count=65536,
        )
        self.assertEqual(
            advice["policy_aware_semantic_signature_helper"],
            "policy_aware_rt_dbscan_semantic_signature",
        )
        self.assertEqual(
            advice["mixed_predicate_comparison_contracts"],
            ("policy_bound_component_sizes", "core_noise_assigned_counts_only"),
        )

    def test_report_records_scope(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted app-layer semantic helper",
            "`policy_bound_component_sizes`",
            "`core_noise_assigned_counts_only`",
            "does not promote predicate direct-status",
            "Native engine remains unchanged",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
