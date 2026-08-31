from __future__ import annotations

import json
import pathlib
import unittest
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4104_direct_status_union_preview_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4104_direct_status_union_timing_pod.json"


def _load_artifact() -> dict[str, Any]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal4104DirectStatusUnionTimingTest(unittest.TestCase):
    def test_pod_artifact_is_clean_commit_pinned_and_non_authorizing(self) -> None:
        payload = _load_artifact()

        self.assertEqual(payload["source_commit"][:8], "08e5836d")
        self.assertFalse(payload["source_tracked_worktree_dirty"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["native_abi_added"])

    def test_direct_status_union_beats_materialized_unordered_path_on_all_profiles(self) -> None:
        rows = {row["profile"]: row for row in _load_artifact()["rows"]}

        self.assertGreater(rows["clustered3d"]["materialized_over_direct_speedup_median"], 1.20)
        self.assertGreater(rows["road3d"]["materialized_over_direct_speedup_median"], 1.45)
        self.assertGreater(rows["ngsim_dense"]["materialized_over_direct_speedup_median"], 1.25)
        for row in rows.values():
            self.assertLess(
                row["direct_status_union_sec"]["median_sec"],
                row["materialized_unordered_sec"]["median_sec"],
            )
            self.assertTrue(row["same_signature_as_materialized"])
            self.assertFalse(row["direct_partition_summary_materialized"])
            self.assertFalse(row["direct_near_pair_columns_materialized"])
            self.assertEqual(row["direct_pair_count"], row["materialized_pair_count"])
            self.assertEqual(row["direct_union_iterations"], 2)
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"])

    def test_report_records_design_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "device_direct_status_union",
            "not_materialized_direct_status_scan",
            "1.239x",
            "1.508x",
            "1.311x",
            "not a route promotion",
            "does not promote",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
