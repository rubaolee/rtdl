from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4243_short_row_long_repeat_refresh_rtx4000ada"
SUMMARY = ARTIFACT_DIR / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal4243_short_row_long_repeat_refresh_2026-06-09.md"

FORBIDDEN_TRUE_FLAGS = {
    "release_authorized",
    "v2_0_release_authorized",
    "v2_6_release_authorized",
    "v2_8_release_authorized",
    "v2_9_release_authorized",
    "v2_10_release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "true_zero_copy_claim_authorized",
    "true_zero_copy_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_logic_allowed",
    "amd_performance_claim_authorized",
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


class Goal4243ShortRowLongRepeatRefreshTest(unittest.TestCase):
    def test_artifacts_and_report_exist(self) -> None:
        self.assertTrue(SUMMARY.is_file())
        self.assertTrue(REPORT.is_file())
        for filename in (
            "goal4243_hausdorff.stdout.json",
            "goal4243_contact_manifold.stdout.json",
            "goal4243_triangle_counting.stdout.json",
        ):
            self.assertTrue((ARTIFACT_DIR / filename).is_file(), filename)

    def test_summary_has_clean_current_head_provenance(self) -> None:
        summary = _load(SUMMARY)
        self.assertEqual(summary["schema"], "rtdl.goal4243.short_row_long_repeat_refresh.v3")
        self.assertEqual(summary["source_commit_short"], "9a40f7f5")
        self.assertTrue(summary["pre_artifact_worktree_clean"])
        self.assertEqual(summary["pre_artifact_git_status_short"], "")
        self.assertIn("NVIDIA RTX 4000 Ada Generation", summary["gpu"])

    def test_all_three_short_rows_have_second_level_repeat_evidence(self) -> None:
        summary = _load(SUMMARY)
        self.assertTrue(summary["all_rows_above_one_second"])
        rows = summary["rows"]
        self.assertEqual(set(rows), {"hausdorff_xhd", "contact_manifold", "triangle_counting"})
        self.assertGreater(rows["hausdorff_xhd"]["aggregate_sec"], 10.0)
        self.assertEqual(rows["hausdorff_xhd"]["repeat"], 1500)
        self.assertTrue(rows["hausdorff_xhd"]["matches_oracle"])
        self.assertTrue(rows["hausdorff_xhd"]["rt_core_accelerated"])

        self.assertGreater(rows["contact_manifold"]["aggregate_sec"], 10.0)
        self.assertEqual(rows["contact_manifold"]["repeat"], 50000)
        self.assertTrue(rows["contact_manifold"]["matches_cpu_reference"])
        self.assertFalse(rows["contact_manifold"]["overflowed"])

        self.assertGreater(rows["triangle_counting"]["aggregate_sec"], 1.0)
        self.assertEqual(rows["triangle_counting"]["repeat"], 10000)
        self.assertTrue(rows["triangle_counting"]["triangle_count_matches_oracle"])
        self.assertTrue(rows["triangle_counting"]["rt_core_accelerated"])

    def test_claim_boundaries_remain_closed(self) -> None:
        summary = _load(SUMMARY)
        self.assertEqual(_forbidden_true_paths(summary), [])
        for filename in (
            "goal4243_hausdorff.stdout.json",
            "goal4243_contact_manifold.stdout.json",
            "goal4243_triangle_counting.stdout.json",
        ):
            self.assertEqual(_forbidden_true_paths(_load(ARTIFACT_DIR / filename)), [])

        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "does not authorize release action",
            "Hausdorff speedup claim",
            "full physics",
            "paper-system reproduction",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
