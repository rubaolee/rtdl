from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4122_tuned_direct_status_scale_probe_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4122_tuned_direct_status_scale_probe_pod.json"


def _load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4122TunedDirectStatusScaleProbeTest(unittest.TestCase):
    def test_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual("rtdl.goal4117.partition_cell_factor_route_sweep.v1", payload["schema"])
        self.assertEqual("c38d071b", payload["source_commit"][:8])
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertEqual(131072, payload["point_count"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["automatic_partner_selection_authorized"])
        self.assertFalse(payload["native_abi_added"])
        self.assertFalse(payload["app_specific_engine_logic_allowed"])

    def test_tuned_direct_status_wins_all_131k_profiles(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}

        self.assertEqual(0.25, rows["clustered3d"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["clustered3d"]["best_replay_over_current_speedup"], 3.2)
        self.assertEqual(0.25, rows["road3d"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["road3d"]["best_replay_over_current_speedup"], 1.5)
        self.assertEqual(0.25, rows["ngsim_dense"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["ngsim_dense"]["best_replay_over_current_speedup"], 1.3)

        for row in rows.values():
            self.assertTrue(row["all_factors_match_current_signature"])

    def test_ngsim_factor_is_scale_sensitive(self) -> None:
        ngsim = {row["partition_cell_factor"]: row for row in _load_artifact()["rows"][2]["factor_rows"]}

        self.assertGreater(ngsim[0.25]["replay_over_current_speedup"], 1.3)
        self.assertGreater(ngsim[0.5]["replay_over_current_speedup"], 1.0)
        self.assertGreater(
            ngsim[0.25]["replay_over_current_speedup"],
            ngsim[0.5]["replay_over_current_speedup"],
        )
        self.assertEqual(5, ngsim[0.25]["max_neighbor_offset"])
        self.assertEqual(3, ngsim[0.5]["max_neighbor_offset"])

    def test_report_documents_scale_sensitive_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "131,072",
            "3.211x",
            "1.545x",
            "1.399x",
            "scale-sensitive",
            "Goal4117 found `ngsim_dense` factor `0.5`",
            "Goal4122 finds `ngsim_dense` factor `0.25`",
            "does not authorize automatic factor selection",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
