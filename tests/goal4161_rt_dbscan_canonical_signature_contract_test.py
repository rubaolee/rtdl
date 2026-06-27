from __future__ import annotations

import json
from pathlib import Path
import unittest

from examples.benchmark_apps.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4159_mixed_predicate_direct_status_scale_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4161_rt_dbscan_canonical_signature_contract_2026-06-09.md"


class Goal4161RtDbscanCanonicalSignatureContractTest(unittest.TestCase):
    def test_canonical_signature_ignores_component_label_permutation(self) -> None:
        left = {"cluster_sizes": {1: 10, 2: 20, 3: 20}, "core_count": 40, "noise_count": 2}
        right = {"cluster_sizes": {7: 20, 9: 10, 11: 20}, "core_count": 40, "noise_count": 2}
        self.assertNotEqual(left, right)
        self.assertEqual(
            app.canonical_component_size_signature(left),
            {"cluster_sizes": (10, 20, 20), "core_count": 40, "noise_count": 2},
        )
        self.assertTrue(app.same_canonical_component_size_signature(left, right))

    def test_goal4159_artifact_separates_label_drift_from_real_border_gap(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        comparisons = artifact["comparisons"]
        exact_mismatches = [row for row in comparisons if not row["same_signature"]]
        canonical_mismatches = [
            row for row in comparisons
            if not app.same_canonical_component_size_signature(
                row["current_signature"],
                row["candidate_signature"],
            )
        ]
        self.assertEqual(len(exact_mismatches), 6)
        self.assertEqual(len(canonical_mismatches), 2)
        self.assertTrue(all(row["case"] == "road_sparse_many_noise" for row in canonical_mismatches))

    def test_report_states_scope(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted app-layer comparison helper",
            "label ids are not semantic",
            "`canonical_component_size_signature(signature)`",
            "does not solve the Goal4159 `road_sparse_many_noise` gap",
            "native engine must remain app-agnostic",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
