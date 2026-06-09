from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4222_rtdbscan_blocked_vs_unblocked_profile_map_rtx4000ada"
SUMMARY = ARTIFACT_DIR / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal4222_rtdbscan_blocked_vs_unblocked_profile_map_2026-06-09.md"

FORBIDDEN_TRUE_FLAGS = {
    "release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "rt_dbscan_paper_reproduction_claim_authorized",
    "true_zero_copy_claim_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_logic_allowed",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _forbidden_true_paths(value, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FLAGS and child is True:
                hits.append(child_path)
            hits.extend(_forbidden_true_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_forbidden_true_paths(child, f"{path}[{index}]"))
    return hits


class Goal4222RtdbscanBlockedVsUnblockedProfileMapTest(unittest.TestCase):
    def test_summary_and_report_exist(self) -> None:
        self.assertTrue(SUMMARY.is_file())
        self.assertTrue(REPORT.is_file())

    def test_profile_map_passes_with_expected_scope(self) -> None:
        summary = _load(SUMMARY)
        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["source_commit"], "63289bbc")
        self.assertEqual(summary["source_dirty"], [])
        self.assertEqual(summary["datasets"], ["clustered3d", "road3d", "ngsim_dense"])
        self.assertEqual(summary["point_counts"], [65536, 262144])
        self.assertEqual(len(summary["rows"]), 6)
        self.assertIn("NVIDIA RTX 4000 Ada Generation", summary["gpu"])
        self.assertEqual(_forbidden_true_paths(summary["claim_boundary"]), [])

    def test_unblocked_wins_every_profile_and_policy_is_canonical(self) -> None:
        summary = _load(SUMMARY)
        for row in summary["rows"]:
            self.assertEqual(row["recommended_default_shape"], "unblocked", row)
            self.assertGreater(row["blocked_vs_unblocked_elapsed_ratio"], 3.0, row)
            unblocked = row["unblocked"]
            blocked = row["blocked"]
            self.assertEqual(unblocked["status"], "pass")
            self.assertEqual(blocked["status"], "pass")
            self.assertLess(unblocked["elapsed_sec"], blocked["elapsed_sec"])
            self.assertEqual(unblocked["grouped_stream_continuation_pass_count"], 1)
            expected_blocked_pass_count = 16 if row["point_count"] == 65536 else 64
            self.assertEqual(
                blocked["grouped_stream_continuation_pass_count"],
                expected_blocked_pass_count,
            )
            for payload in (unblocked, blocked):
                self.assertEqual(payload["boundary_assignment_policy"], "single_pass_candidate_root_rebased")
                self.assertEqual(payload["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")
                self.assertEqual(payload["partner"], "numba")
                self.assertEqual(_forbidden_true_paths(payload), [])

    def test_artifact_stdout_files_exist_for_each_mode(self) -> None:
        summary = _load(SUMMARY)
        for row in summary["rows"]:
            for label in ("unblocked", "blocked"):
                stdout = ROOT / row[label]["stdout_path"]
                stderr = ROOT / row[label]["stderr_path"]
                self.assertTrue(stdout.is_file(), stdout)
                self.assertTrue(stderr.is_file(), stderr)
                payload = _load(stdout)
                self.assertEqual(payload["metadata"]["boundary_assignment_policy"], "single_pass_candidate_root_rebased")


if __name__ == "__main__":
    unittest.main()
