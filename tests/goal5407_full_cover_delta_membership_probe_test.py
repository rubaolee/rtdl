from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5407_full_cover_delta_membership_probe.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5407_full_cover_delta_membership_probe_pod.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5407_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load Goal5407 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5407FullCoverDeltaMembershipProbeTest(unittest.TestCase):
    def test_per_source_count_summary_reports_distribution(self) -> None:
        module = _load_module()
        source_ids = np.asarray([0, 0, 1, 2, 2, 2], dtype=np.int64)
        summary = module.per_source_count_summary(source_ids, active_count=4)
        self.assertEqual(4, summary["active_count"])
        self.assertEqual(6, summary["row_count"])
        self.assertEqual(0, summary["min_rows_per_active"])
        self.assertEqual(3, summary["max_rows_per_active"])
        self.assertEqual(["0", "1", "2", "3"], sorted(summary["rows_per_active_histogram"]))
        self.assertFalse(summary["all_sources_have_same_row_count"])

    def test_sample_pair_membership_detects_present_and_missing_author_rows(self) -> None:
        module = _load_module()
        source_ids = np.asarray([10, 10, 11, 12], dtype=np.int64)
        cell_ids = np.asarray([3, 7, 5, 9], dtype=np.int64)
        rows = module.sample_pair_membership(
            source_ids=source_ids,
            cell_ids=cell_ids,
            sample_source_ids=[10, 11, 12],
            sample_cell_ids=[7, 8, 9],
        )
        self.assertTrue(rows[0]["author_cell_present_in_rtdl_full_cover"])
        self.assertFalse(rows[1]["author_cell_present_in_rtdl_full_cover"])
        self.assertTrue(rows[2]["author_cell_present_in_rtdl_full_cover"])
        self.assertEqual([5], rows[1]["rtdl_cells_sample"])

    def test_classification_flags_row_identity_gap_when_author_sample_missing(self) -> None:
        module = _load_module()
        classification = module.classify_delta(
            count_summary={"all_sources_have_same_row_count": True},
            memberships=[
                {"author_cell_present_in_rtdl_full_cover": True},
                {"author_cell_present_in_rtdl_full_cover": False},
            ],
            author_feedback_updates=294,
            cmin2_after_ray_hash=123,
            cmin2_after_load_balance_hash=123,
        )
        self.assertEqual(
            "author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap",
            classification["label"],
        )
        self.assertFalse(classification["all_author_sample_pairs_present_in_rtdl_full_cover"])
        self.assertFalse(classification["feedback_changes_cmin2_hash"])

    def test_runner_keeps_claim_boundary_closed(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"explicit_lb_support_claimed": False', source)
        self.assertIn('"figure7_reproduction_claimed": False', source)
        self.assertIn('"full_xhd_paper_reproduction_claimed": False', source)
        self.assertIn("author_sample_pair_membership_in_rtdl_full_cover", source)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal5407 POD artifact not present")
    def test_pod_artifact_is_delta_probe_not_lb_support(self) -> None:
        import json

        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "rtdl.paper_reproduction.xhd.goal5407.full_cover_delta_membership_probe.v1",
            payload["schema"],
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(24508120, payload["goal5406_summary"]["rtdl_full_cover_rows"])
        self.assertEqual(27133990, payload["goal5406_summary"]["author_raw_offload_rows"])
        self.assertEqual(2625870, payload["delta"]["total_delta_rows"])
        self.assertEqual(6, payload["delta"]["delta_rows_per_active_if_uniform"])
        self.assertFalse(payload["decision"]["explicit_lb_support_authorized"])
        self.assertFalse(payload["claim_boundary"]["explicit_lb_support_claimed"])


if __name__ == "__main__":
    unittest.main()
