from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4130_tuned_direct_status_warm_one_shot_probe_2026-06-09.md"
ARTIFACTS = {
    65536: ROOT / "docs" / "reports" / "goal4130_tuned_direct_status_warm_one_shot_65k_pod.json",
    131072: ROOT / "docs" / "reports" / "goal4130_tuned_direct_status_warm_one_shot_131k_pod.json",
    262144: ROOT / "docs" / "reports" / "goal4130_tuned_direct_status_warm_one_shot_262k_pod.json",
}


def _payload(scale: int) -> dict:
    return json.loads(ARTIFACTS[scale].read_text(encoding="utf-8"))


def _best_row(row: dict) -> dict:
    return next(
        factor_row
        for factor_row in row["factor_rows"]
        if factor_row["partition_cell_factor"] == row["best_replay_partition_cell_factor"]
    )


def _one_shot_speedup(row: dict) -> float:
    best = _best_row(row)
    current_total = float(row["current_route_prepare_sec"]) + float(row["current_route_replay_sec"])
    direct_total = float(best["prepare_sec"]) + float(best["replay_sec"])
    return current_total / direct_total


class Goal4130TunedDirectStatusWarmOneShotProbeTest(unittest.TestCase):
    def test_artifacts_are_clean_commit_pinned_and_non_authorizing(self) -> None:
        for scale, path in ARTIFACTS.items():
            with self.subTest(scale=scale):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual("rtdl.goal4117.partition_cell_factor_route_sweep.v1", payload["schema"])
                self.assertEqual("f9f1b82b", payload["source_commit"][:8])
                self.assertFalse(payload["source_tracked_worktree_dirty"])
                self.assertEqual(scale, payload["point_count"])
                self.assertEqual(2, payload["repeat"])
                self.assertEqual(1, payload["warmup"])
                self.assertFalse(payload["release_authorized"])
                self.assertFalse(payload["public_speedup_claim_authorized"])
                self.assertFalse(payload["automatic_partner_selection_authorized"])
                self.assertFalse(payload["native_abi_added"])
                self.assertFalse(payload["app_specific_engine_logic_allowed"])

    def test_warmed_one_shot_total_wins_all_profiles_and_scales(self) -> None:
        expected_factors = {
            65536: {"clustered3d": 0.25, "road3d": 0.25, "ngsim_dense": 0.5},
            131072: {"clustered3d": 0.25, "road3d": 0.25, "ngsim_dense": 0.25},
            262144: {"clustered3d": 0.25, "road3d": 0.25, "ngsim_dense": 0.25},
        }
        minimum_one_shot_speedups = {
            65536: {"clustered3d": 2.5, "road3d": 2.6, "ngsim_dense": 1.8},
            131072: {"clustered3d": 3.1, "road3d": 2.6, "ngsim_dense": 3.4},
            262144: {"clustered3d": 3.1, "road3d": 2.2, "ngsim_dense": 2.9},
        }
        for scale, payload_path in ARTIFACTS.items():
            rows = {row["profile"]: row for row in json.loads(payload_path.read_text(encoding="utf-8"))["rows"]}
            for profile, row in rows.items():
                with self.subTest(scale=scale, profile=profile):
                    self.assertEqual(expected_factors[scale][profile], row["best_replay_partition_cell_factor"])
                    self.assertGreater(_one_shot_speedup(row), minimum_one_shot_speedups[scale][profile])
                    self.assertTrue(row["all_factors_match_current_signature"])

    def test_report_documents_warmed_one_shot_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "repeat=2",
            "warmup=1",
            "one-shot total",
            "1.819x",
            "3.410x",
            "not make the route automatic",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
