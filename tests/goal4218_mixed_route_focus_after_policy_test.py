from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4218_mixed_route_focus_after_policy_rtx4000ada"
MANIFEST = ARTIFACT_DIR / "summary_manifest.json"
REPORT = ROOT / "docs" / "reports" / "goal4218_mixed_route_focus_after_policy_2026-06-09.md"

FORBIDDEN_TRUE_FLAGS = {
    "release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "rayjoin_paper_reproduction_claim_authorized",
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


class Goal4218MixedRouteFocusAfterPolicyTest(unittest.TestCase):
    def test_manifest_and_report_exist(self) -> None:
        self.assertTrue(MANIFEST.is_file())
        self.assertTrue(REPORT.is_file())

    def test_manifest_passes_at_expected_commit(self) -> None:
        manifest = _load(MANIFEST)
        self.assertEqual(manifest["status"], "pass")
        self.assertEqual(manifest["source_commit"], "63289bbc")
        self.assertEqual(manifest["source_dirty"], [])
        self.assertLess(manifest["elapsed_sec"], 60.0)
        self.assertEqual(_forbidden_true_paths(manifest["claim_boundary"]), [])

    def test_rayjoin_contract_split_remains_visible(self) -> None:
        summary = _load(ARTIFACT_DIR / "rayjoin" / "summary.json")
        hot = summary["representative_hot_path_summary"]
        self.assertTrue(hot["all_contract_counts_match"])
        self.assertEqual(hot["contract_count"], 4)
        self.assertEqual(hot["recommended_route_summary"]["numba_contracts"], ["pip_one_shot"])
        self.assertEqual(
            hot["recommended_route_summary"]["rtdl_optix_contracts"],
            ["pip_repeated_requests", "lsi_scalar_count", "overlay_active_count"],
        )
        self.assertLess(hot["pip_one_shot"]["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertGreater(hot["pip_repeated_requests"]["per_request_speedup_vs_single_request"], 1.0)
        self.assertGreater(hot["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(hot["overlay_active_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertEqual(_forbidden_true_paths(summary), [])

    def test_rtdbscan_unblocked_beats_blocked_for_default_profile(self) -> None:
        unblocked = _load(
            ARTIFACT_DIR
            / "rtdbscan"
            / "optix_rt_core_grouped_stream_numba_column_signature_3d.json"
        )
        blocked = _load(
            ARTIFACT_DIR
            / "rtdbscan"
            / "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d.json"
        )
        for payload in (unblocked, blocked):
            metadata = payload["metadata"]
            self.assertEqual(metadata["boundary_assignment_policy"], "single_pass_candidate_root_rebased")
            self.assertEqual(metadata["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")
            self.assertEqual(_forbidden_true_paths(payload), [])

        self.assertEqual(unblocked["metadata"]["grouped_stream_continuation_pass_count"], 1)
        self.assertEqual(blocked["metadata"]["grouped_stream_continuation_pass_count"], 16)
        self.assertLess(unblocked["elapsed_sec"], blocked["elapsed_sec"])
        self.assertGreater(blocked["elapsed_sec"] / unblocked["elapsed_sec"], 4.0)


if __name__ == "__main__":
    unittest.main()
