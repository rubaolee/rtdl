from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4138_tuned_direct_status_1m_factor025_probe_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4138_tuned_direct_status_warm_one_shot_1m_factor025_pod.json"


def _load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4138TunedDirectStatus1mFactor025ProbeTest(unittest.TestCase):
    def test_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual("rtdl.goal4117.partition_cell_factor_route_sweep.v1", payload["schema"])
        self.assertEqual("c9469d43", payload["source_commit"][:8])
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertEqual(1048576, payload["point_count"])
        self.assertEqual([0.25], payload["partition_cell_factors"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["automatic_partner_selection_authorized"])
        self.assertFalse(payload["native_abi_added"])
        self.assertFalse(payload["app_specific_engine_logic_allowed"])

    def test_factor025_stays_positive_at_1m(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}
        minimum_replay = {"clustered3d": 3.4, "road3d": 1.3, "ngsim_dense": 1.7}
        minimum_one_shot = {"clustered3d": 3.3, "road3d": 1.7, "ngsim_dense": 2.4}

        for profile, row in rows.items():
            with self.subTest(profile=profile):
                self.assertEqual(0.25, row["best_replay_partition_cell_factor"])
                factor = row["factor_rows"][0]
                current_total = row["current_route_prepare_sec"] + row["current_route_replay_sec"]
                direct_total = factor["prepare_sec"] + factor["replay_sec"]
                self.assertGreater(factor["replay_over_current_speedup"], minimum_replay[profile])
                self.assertGreater(current_total / direct_total, minimum_one_shot[profile])
                self.assertTrue(factor["same_signature"])
                self.assertTrue(row["all_factors_match_current_signature"])

    def test_report_documents_limited_1m_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "1,048,576",
            "factor `0.25`",
            "not a full factor sweep",
            "1.396x",
            "1.705x",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
