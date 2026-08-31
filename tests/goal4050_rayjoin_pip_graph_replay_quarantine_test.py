from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4050_rayjoin_pip_graph_replay_quarantine_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4050_rayjoin_pip_graph_current_negative_probe_pod.json"


class Goal4050RayJoinPipGraphReplayQuarantineTest(unittest.TestCase):
    def test_pod_artifact_records_working_non_graph_lanes_and_failed_graph_lane(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], 4050)
        self.assertEqual(artifact["single"]["count"], 6)
        self.assertEqual(artifact["batch"]["counts"], [6, 6, 6, 6, 6])
        self.assertEqual(artifact["batch_executor"]["counts"], [6, 6, 6, 6, 6])
        self.assertEqual(artifact["graph_validated"]["status"], "failed_closed")
        self.assertIn("OptiX error: CUDA error", artifact["graph_validated"]["error"])
        self.assertEqual(artifact["graph_raw"]["status"], "prepare_or_replay_failed")
        self.assertFalse(any(artifact["claim_boundary"].values()))

    def test_current_rayjoin_guidance_quarantines_prepared_points_graph_replay(self) -> None:
        route = rt.explain_current_benchmark_route("spatial_rayjoin")
        spatial = {row["app"]: row for row in rt.current_benchmark_adequacy()}["spatial_rayjoin"]

        self.assertIn("Goal4050", route["evidence_refs"])
        self.assertIn("Goal4050", spatial["evidence_refs"])
        self.assertIn("CUDA graph replay", route["rejected_or_unpromoted_candidates"][-1])
        self.assertIn("quarantined", route["next_runtime_action"])
        self.assertIn("OptiX/CUDA prepare failure", spatial["next_generic_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])

    def test_report_documents_quarantine_and_non_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Graph with validation",
            "failed_closed",
            "Raw graph without validation",
            "prepare_or_replay_failed",
            "quarantined until a real OptiX-capture fix exists",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
