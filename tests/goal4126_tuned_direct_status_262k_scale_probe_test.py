from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4126_tuned_direct_status_262k_scale_probe_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4126_tuned_direct_status_262k_scale_probe_pod.json"


def _load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4126TunedDirectStatus262kScaleProbeTest(unittest.TestCase):
    def test_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual("rtdl.goal4117.partition_cell_factor_route_sweep.v1", payload["schema"])
        self.assertEqual("5ddd50cd", payload["source_commit"][:8])
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertEqual(262144, payload["point_count"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["automatic_partner_selection_authorized"])
        self.assertFalse(payload["native_abi_added"])
        self.assertFalse(payload["app_specific_engine_logic_allowed"])

    def test_tuned_direct_status_wins_all_262k_profiles(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}

        self.assertEqual(0.25, rows["clustered3d"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["clustered3d"]["best_replay_over_current_speedup"], 3.0)
        self.assertEqual(0.25, rows["road3d"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["road3d"]["best_replay_over_current_speedup"], 1.4)
        self.assertEqual(0.25, rows["ngsim_dense"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["ngsim_dense"]["best_replay_over_current_speedup"], 1.6)

        for row in rows.values():
            self.assertTrue(row["all_factors_match_current_signature"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])

    def test_half_cell_factor_is_not_a_universal_dense_default(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}
        ngsim = {row["partition_cell_factor"]: row for row in rows["ngsim_dense"]["factor_rows"]}

        self.assertGreater(ngsim[0.25]["replay_over_current_speedup"], 1.6)
        self.assertLess(ngsim[0.5]["replay_over_current_speedup"], 1.0)
        self.assertGreater(
            ngsim[0.25]["replay_over_current_speedup"],
            ngsim[0.5]["replay_over_current_speedup"],
        )
        self.assertEqual(5, ngsim[0.25]["max_neighbor_offset"])
        self.assertEqual(3, ngsim[0.5]["max_neighbor_offset"])

    def test_report_documents_262k_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "262,144",
            "3.118x",
            "1.428x",
            "1.642x",
            "0.5` was best at 65k",
            "`0.25` wins at 131k and 262k",
            "does not authorize automatic factor selection",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
