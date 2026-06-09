from __future__ import annotations

import json
import pathlib
import unittest
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4108_prepared_direct_status_reuse_timing_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4108_prepared_direct_status_reuse_timing_pod.json"


def _load_artifact() -> dict[str, Any]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4108PreparedDirectStatusReuseTimingTest(unittest.TestCase):
    def test_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual("rtdl.goal4108.prepared_direct_status_reuse_timing.v1", payload["schema"])
        self.assertEqual(payload["source_commit"][:8], "fa7386ce")
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["native_abi_added"])

    def test_prepared_direct_status_replay_beats_one_shot_and_current_route(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}

        expected_thresholds = {
            "clustered3d": (1.7, 3.5),
            "road3d": (2.3, 4.4),
            "ngsim_dense": (1.4, 1.1),
        }
        for profile, (one_shot_threshold, current_threshold) in expected_thresholds.items():
            row = rows[profile]
            self.assertTrue(row["same_signature"], profile)
            self.assertGreater(row["prepared_replay_over_one_shot_speedup_median"], one_shot_threshold)
            self.assertGreater(row["prepared_replay_over_current_route_speedup_median"], current_threshold)
            self.assertLess(row["prepared_direct_status_replay_sec"]["median_sec"], row["one_shot_direct_status_median_sec"])
            self.assertLess(row["prepared_direct_status_replay_sec"]["median_sec"], row["current_route_median_sec"])
            self.assertLess(row["prepared_three_run_amortized_sec"], row["current_route_median_sec"])
            self.assertFalse(row["partition_convergence_hybrid_promoted"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])

    def test_prepared_handle_metadata_avoids_pair_materialization(self) -> None:
        for row in _load_artifact()["rows"]:
            handle = row["prepared_handle_metadata"]
            prepare = handle["prepare_metadata"]
            self.assertTrue(handle["prepared_direct_status_union_handle"])
            self.assertFalse(handle["near_pair_columns_materialized"])
            self.assertFalse(handle["partition_pair_rows_materialized"])
            self.assertTrue(handle["pair_materialization_avoided"])
            self.assertFalse(handle["partition_convergence_hybrid_promoted"])
            self.assertFalse(handle["automatic_partner_selection_allowed"])
            self.assertTrue(prepare["prepared_direct_status_runtime_columns"])
            self.assertFalse(prepare["near_pair_columns_materialized"])
            self.assertFalse(prepare["partition_pair_rows_materialized"])
            self.assertTrue(prepare["pair_materialization_avoided"])

    def test_report_documents_boundary_and_speedups(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Goal4108 - Prepared Direct Status Union Reuse Timing",
            "0.050407",
            "0.028225",
            "0.085393",
            "1.802x",
            "2.465x",
            "1.488x",
            "3.752x",
            "4.648x",
            "1.207x",
            "does not promote",
            "does not authorize release",
            "true-zero-copy",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
