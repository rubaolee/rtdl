from __future__ import annotations

import json
import pathlib
import unittest
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4114_prepared_direct_status_app_repeat_route_timing_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4114_prepared_direct_status_app_repeat_route_timing_pod.json"


def _load_artifact() -> dict[str, Any]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4114PreparedDirectStatusAppRepeatRouteTimingTest(unittest.TestCase):
    def test_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual("rtdl.goal4114.prepared_direct_status_app_repeat_route_timing.v1", payload["schema"])
        self.assertEqual(payload["source_commit"][:8], "0f83ffab")
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["native_abi_added"])

    def test_repeated_route_result_is_shape_dependent(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}

        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            self.assertTrue(rows[profile]["same_signature"])
            self.assertFalse(rows[profile]["partition_convergence_hybrid_promoted"])
            self.assertFalse(rows[profile]["release_authorized"])
            self.assertFalse(rows[profile]["public_speedup_claim_authorized"])

        self.assertGreater(rows["clustered3d"]["prepared_replay_over_current_replay_speedup"], 1.7)
        self.assertGreater(rows["road3d"]["prepared_replay_over_current_replay_speedup"], 1.3)
        self.assertLess(rows["ngsim_dense"]["prepared_replay_over_current_replay_speedup"], 0.2)

        self.assertGreater(rows["clustered3d"]["prepared_amortized_over_current_amortized_speedup"], 1.7)
        self.assertGreater(rows["road3d"]["prepared_amortized_over_current_amortized_speedup"], 1.8)
        self.assertLess(rows["ngsim_dense"]["prepared_amortized_over_current_amortized_speedup"], 0.9)

    def test_payloads_record_repeated_protocols(self) -> None:
        for row in _load_artifact()["rows"]:
            prepared_protocol = row["prepared_payload"]["metadata"]["prepared_direct_status_repeat_protocol"]
            current_protocol = row["current_payload"]["metadata"]["prepared_query_repeat_protocol"]
            self.assertEqual(prepared_protocol["repeat"], 4)
            self.assertEqual(prepared_protocol["warmup"], 1)
            self.assertEqual(prepared_protocol["measured_run_count"], 3)
            self.assertTrue(prepared_protocol["signatures_stable"])
            self.assertEqual(current_protocol["repeat"], 4)
            self.assertEqual(current_protocol["warmup"], 1)
            self.assertEqual(current_protocol["measured_run_count"], 3)
            self.assertTrue(current_protocol["signatures_stable"])

    def test_report_documents_mixed_guidance(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Goal4114 - Prepared Direct Status Repeated App-Route Timing",
            "1.796x",
            "1.439x",
            "0.178x",
            "not a universal RT-DBSCAN replacement",
            "clustered/road-like repeated component signatures",
            "dense NGSIM-like repeated component signatures",
            "does not promote",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
