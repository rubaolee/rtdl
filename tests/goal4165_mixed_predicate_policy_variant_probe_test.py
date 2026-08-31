from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4165_mixed_policy_variant_probe_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4165_mixed_predicate_policy_variant_probe_2026-06-09.md"


class Goal4165MixedPredicatePolicyVariantProbeTest(unittest.TestCase):
    def test_artifact_records_no_single_grouped_variant_as_universal_reference(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal4165")
        self.assertEqual(artifact["commit"], "d25eff118d8590068c5aa0ead9c557240ae3a06c")
        self.assertIn("RTX 4000 Ada", artifact["gpu"])
        self.assertEqual(len(artifact["rows"]), 12)
        variants = (
            "grouped_stream_numba_same_root_true",
            "grouped_stream_numba_same_root_false",
            "grouped_stream_numba_direct_side_effect",
        )
        for variant in variants:
            exact = sum(1 for row in artifact["rows"] if row["candidate_matches"][variant])
            canonical = sum(1 for row in artifact["rows"] if row["candidate_canonical_matches"][variant])
            self.assertEqual(exact, 7, variant)
            self.assertEqual(canonical, 11, variant)

    def test_only_road_sparse_seed_variants_show_canonical_mismatch(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        mismatches = []
        for row in artifact["rows"]:
            bad = tuple(
                variant
                for variant, matches in sorted(row["candidate_canonical_matches"].items())
                if not matches
            )
            if bad:
                mismatches.append((row["case"], row["seed"], bad))
        self.assertEqual(
            mismatches,
            [
                ("road_sparse_many_noise", 17, ("grouped_stream_numba_direct_side_effect",)),
                (
                    "road_sparse_many_noise",
                    123,
                    (
                        "grouped_stream_numba_same_root_false",
                        "grouped_stream_numba_same_root_true",
                    ),
                ),
            ],
        )

    def test_report_states_policy_interpretation_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "No grouped-stream variant explains every predicate direct-status result.",
            "Predicate-false items that touch more than one predicate-true component need an explicit border assignment policy",
            "a raw component-size signature is too strict",
            "does not promote predicate direct-status for mixed predicate rows",
            "policy-aware RT-DBSCAN semantic signature",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
