from __future__ import annotations

import argparse
import unittest
from pathlib import Path

from scripts import goal2348_rtnn_v2_2_external_runner as runner


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2821_rtnn_heterogeneous_batched_aggregate_requests_2026-05-31.md"


class Goal2821RtnnHeterogeneousBatchedAggregateRequestsTest(unittest.TestCase):
    def test_runner_parses_heterogeneous_aggregate_requests(self) -> None:
        args = argparse.Namespace(
            aggregate_request_count=4,
            aggregate_radius_multipliers="0.5,1.0,1.5,2.0",
            aggregate_k_values="8,16,32,50",
        )

        requests = runner._aggregate_batch_requests(args, base_radius=0.02, base_k_max=50)

        self.assertEqual(
            requests,
            (
                {"radius": 0.01, "k_max": 8},
                {"radius": 0.02, "k_max": 16},
                {"radius": 0.03, "k_max": 32},
                {"radius": 0.04, "k_max": 50},
            ),
        )

    def test_runner_rejects_mismatched_request_lists(self) -> None:
        args = argparse.Namespace(
            aggregate_request_count=4,
            aggregate_radius_multipliers="1.0,2.0",
            aggregate_k_values=None,
        )

        with self.assertRaisesRegex(ValueError, "length must match aggregate_request_count"):
            runner._aggregate_batch_requests(args, base_radius=0.02, base_k_max=50)

    def test_runner_metadata_exposes_request_mode_and_requests(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("--aggregate-radius-multipliers", text)
        self.assertIn("--aggregate-k-values", text)
        self.assertIn("aggregate_batch_requests", text)
        self.assertIn("aggregate_batch_request_mode", text)
        self.assertIn("heterogeneous", text)
        self.assertIn("max_prepared_radius", text)
        self.assertIn("prepared.aggregate_ranked_summary_prepared_queries_batch", text)
        self.assertNotIn("rtnn", text[text.index("def _aggregate_batch_requests"):text.index("def run_rtdl_batched_3d_neighbors")].lower())

    def test_report_keeps_claim_boundary_pending_pod_evidence(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("implementation-pending-pod-evidence", report)
        self.assertIn("parameter sweep", report)
        self.assertIn("maximum requested radius", report)
        self.assertIn("No single-request speedup claim is authorized", report)
        self.assertIn("Pod evidence is required", report)


if __name__ == "__main__":
    unittest.main()
