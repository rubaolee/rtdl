from __future__ import annotations

import json
import pathlib
import unittest
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4105_direct_status_vs_current_route_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4105_direct_status_vs_current_route_pod.json"


def _load_artifact() -> dict[str, Any]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4105DirectStatusVsCurrentRouteTest(unittest.TestCase):
    def test_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual(payload["source_commit"][:8], "a6bf5eae")
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["native_abi_added"])

    def test_direct_status_is_not_promotable_as_naive_app_level_route(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}

        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            row = rows[profile]
            self.assertFalse(row["direct_is_faster_than_current"])
            self.assertLess(row["current_over_direct_speedup_median"], 1.0)
            self.assertTrue(row["same_signature"])
            self.assertFalse(row["direct_partition_summary_materialized"])
            self.assertFalse(row["direct_near_pair_columns_materialized"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"])

        self.assertLess(rows["clustered3d"]["current_over_direct_speedup_median"], 0.6)
        self.assertLess(rows["road3d"]["current_over_direct_speedup_median"], 0.5)
        self.assertLess(rows["ngsim_dense"]["current_over_direct_speedup_median"], 0.3)

    def test_report_records_prepared_resident_next_target(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "resident/runtime win",
            "naive app-level call",
            "0.475x",
            "0.380x",
            "0.206x",
            "not route-promotable",
            "prepared/resident direct-status partition-convergence handle",
            "does not promote",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
