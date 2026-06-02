from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3008_numba_group_argmin_global_argmax_front_door_2026-06-01.md"


class Goal3008NumbaGroupArgminGlobalArgmaxFrontDoorTest(unittest.TestCase):
    def test_front_door_source_has_numba_branch_without_app_terms(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        for phrase in (
            'partner == "numba"',
            "group_argmin_then_global_argmax_partner_columns",
            "grouped_argmin_f64_partner_columns",
            "run_numba_grouped_argmax_f64",
            "v2_6_numba_partner_continuation_operations",
            "host_present_group_compaction_used",
            "true_zero_copy_claim_authorized",
        ):
            self.assertIn(phrase, source)

        start = source.index("def group_argmin_then_global_argmax_partner_columns")
        numba_start = source.index('if partner == "numba"', start)
        numba_branch = source[numba_start : source.index('runtime = _partner_module(partner)', numba_start)]
        for forbidden in ("hausdorff", "rtnn", "rayjoin", "dbscan"):
            self.assertNotIn(forbidden, numba_branch.lower())

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "group_argmin_then_global_argmax_partner_columns",
            "partner=\"numba\"",
            "Hausdorff-style and",
            "nearest-witness benchmark apps",
            "does not call RT",
            "does not authorize",
            "v2.6 release",
            "Numba speedup wording",
            "true-zero-copy wording",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_numba_front_door_matches_expected_witness_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable front-door validation")

        import numpy as np
        from numba import cuda

        group_ids = cuda.to_device(np.asarray([0, 0, 1, 1, 2, 2], dtype=np.int64))
        item_ids = cuda.to_device(np.asarray([5, 4, 9, 8, 7, 6], dtype=np.int64))
        scores = cuda.to_device(np.asarray([2.0, 2.0, 5.0, 4.0, 4.0, 4.0], dtype=np.float64))

        result = rt.group_argmin_then_global_argmax_partner_columns(
            {"group_ids": group_ids, "item_ids": item_ids, "scores": scores},
            group_count=3,
            partner="numba",
            return_metadata=True,
        )

        self.assertEqual(result["columns"]["argmin_item_ids"].copy_to_host().tolist(), [4, 8, 6])
        self.assertEqual(result["columns"]["argmin_scores"].copy_to_host().tolist(), [2.0, 4.0, 4.0])
        self.assertEqual(result["metadata"]["winner_group_id"], 1)
        self.assertEqual(result["metadata"]["winner_item_id"], 8)
        self.assertEqual(result["metadata"]["winner_score"], 4.0)
        self.assertEqual(
            result["metadata"]["v2_6_numba_partner_continuation_operations"],
            ("grouped_argmin_f64", "grouped_argmax_f64"),
        )
        self.assertFalse(result["metadata"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(result["metadata"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
