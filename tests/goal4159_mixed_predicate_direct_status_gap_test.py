from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4159_mixed_predicate_direct_status_scale_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4159_mixed_predicate_direct_status_gap_2026-06-09.md"


def _canonical_signature(signature: dict[str, object]) -> dict[str, object]:
    return {
        "core_count": int(signature["core_count"]),
        "noise_count": int(signature["noise_count"]),
        "cluster_sizes_sorted": sorted(int(value) for value in signature["cluster_sizes"].values()),
    }


class Goal4159MixedPredicateDirectStatusGapTest(unittest.TestCase):
    def test_artifact_captures_mixed_predicate_gap(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal4159")
        self.assertEqual(artifact["git_commit"], "63cfbc9a")
        self.assertEqual(len(artifact["rows"]), 21)

        comparisons = artifact["comparisons"]
        self.assertEqual(len(comparisons), 14)
        exact_matches = [row for row in comparisons if row["same_signature"]]
        canonical_matches = [
            row for row in comparisons
            if _canonical_signature(row["current_signature"]) == _canonical_signature(row["candidate_signature"])
        ]
        self.assertEqual(len(exact_matches), 8)
        self.assertEqual(len(canonical_matches), 12)

        self.assertTrue(all(row["candidate_all_predicate_fast_path"] is None for row in comparisons))
        self.assertTrue(all(int(row["candidate_border_candidate_updates"]) > 0 for row in comparisons))

        stable = [row for row in comparisons if row["candidate"] == "predicate_direct_status_until_stable"]
        single_pass = [row for row in comparisons if row["candidate"] == "predicate_direct_status_single_pass"]
        self.assertEqual(sum(row["speedup_current_over_candidate"] > 1.0 for row in stable), 2)
        self.assertEqual(sum(row["speedup_current_over_candidate"] > 1.0 for row in single_pass), 3)
        self.assertTrue(all(row["candidate_convergence_proven"] is True for row in stable))
        self.assertTrue(all(row["candidate_convergence_proven"] is False for row in single_pass))

        boundary = artifact["claim_boundary"]
        for key in (
            "route_promotion_authorized",
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "whole_app_claim_authorized",
        ):
            self.assertIs(boundary[key], False)

    def test_report_blocks_promotion_and_names_next_contract(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "diagnostic packet accepted; route promotion remains blocked",
            "Component label-order drift",
            "Real border-assignment gap",
            "Canonical size-signature matches: 12/14 comparisons",
            "blocks predicate direct-status route promotion",
            "generic border-assignment policy",
            "`lowest_neighbor`, `lowest_component_root`, or `reference_grouped_stream_compatible`",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
