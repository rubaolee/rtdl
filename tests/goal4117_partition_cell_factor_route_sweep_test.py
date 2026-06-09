from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4117_partition_cell_factor_route_sweep_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4117_partition_cell_factor_route_sweep_pod.json"
SCRIPT = ROOT / "scripts" / "goal4117_partition_cell_factor_route_sweep.py"


def _load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4117PartitionCellFactorRouteSweepTest(unittest.TestCase):
    def test_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual("rtdl.goal4117.partition_cell_factor_route_sweep.v1", payload["schema"])
        self.assertEqual("493bccf5", payload["source_commit"][:8])
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["automatic_partner_selection_authorized"])
        self.assertFalse(payload["native_abi_added"])
        self.assertFalse(payload["app_specific_engine_logic_allowed"])

    def test_tuned_factors_win_repeated_route_for_all_profiles(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}

        self.assertEqual(0.25, rows["clustered3d"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["clustered3d"]["best_replay_over_current_speedup"], 2.9)
        self.assertGreater(rows["clustered3d"]["best_amortized_over_current_speedup"], 9.0)

        self.assertEqual(0.25, rows["road3d"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["road3d"]["best_replay_over_current_speedup"], 1.8)
        self.assertGreater(rows["road3d"]["best_amortized_over_current_speedup"], 2.3)

        self.assertEqual(0.5, rows["ngsim_dense"]["best_replay_partition_cell_factor"])
        self.assertGreater(rows["ngsim_dense"]["best_replay_over_current_speedup"], 1.3)
        self.assertGreater(rows["ngsim_dense"]["best_amortized_over_current_speedup"], 2.4)

        for row in rows.values():
            self.assertTrue(row["all_factors_match_current_signature"])
            for factor_row in row["factor_rows"]:
                self.assertTrue(factor_row["same_signature"])
                self.assertEqual(factor_row["partition_cell_factor"], factor_row["metadata_cell_factor"])
                self.assertEqual(factor_row["partition_cell_factor"], factor_row["handle_cell_factor"])
                self.assertFalse(factor_row["automatic_partner_selection_authorized"])
                self.assertFalse(factor_row["partition_convergence_hybrid_promoted"])

    def test_ngsim_default_loss_is_repaired_by_explicit_larger_factor(self) -> None:
        ngsim = {row["partition_cell_factor"]: row for row in _load_artifact()["rows"][2]["factor_rows"]}

        self.assertLess(ngsim[0.125]["replay_over_current_speedup"], 0.2)
        self.assertGreater(ngsim[0.5]["replay_over_current_speedup"], 1.3)
        self.assertGreater(ngsim[0.125]["partition_count"], 60000)
        self.assertLess(ngsim[0.5]["partition_count"], 7000)
        self.assertEqual(9, ngsim[0.125]["max_neighbor_offset"])
        self.assertEqual(3, ngsim[0.5]["max_neighbor_offset"])

    def test_script_and_report_document_explicit_not_auto_tuned_route(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("partition_cell_factor", script)
        self.assertIn("automatic_partner_selection_authorized", script)
        self.assertIn("not hidden auto-tuning", report)
        self.assertIn("0.25", report)
        self.assertIn("0.5", report)
        self.assertIn("1.312x", report)
        self.assertIn("does not promote automatic tuning", report)
        self.assertIn("does not authorize release", report)


if __name__ == "__main__":
    unittest.main()
